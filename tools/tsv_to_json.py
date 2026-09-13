#!/usr/bin/env python3
"""Convertit une Content Taxonomy IAB (TSV) en JSON arborescent.

Les TSV sources sont publies par l'IAB Tech Lab :
https://github.com/InteractiveAdvertisingBureau/Taxonomies

Usage :
    tools/tsv_to_json.py 3.1
    tools/tsv_to_json.py 3.0-vectors -o IAB_Content_Vectors_EN_v3.0.json
    tools/tsv_to_json.py 2.2 --from-file /chemin/vers/Content\\ Taxonomy\\ 2.2.tsv
"""

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = (
    "https://raw.githubusercontent.com/InteractiveAdvertisingBureau"
    "/Taxonomies/main/Content%20Taxonomies/"
)

# version -> (nom du TSV source, nom du JSON produit)
SOURCES = {
    "2.0": ("Content Taxonomy 2.0.tsv", "IAB_Content_Categories_EN_v2.0.json"),
    "2.1": ("Content Taxonomy 2.1.tsv", "IAB_Content_Categories_EN_v2.1.json"),
    "2.2": ("Content Taxonomy 2.2.tsv", "IAB_Content_Categories_EN_v2.2.json"),
    "3.0": ("Content Taxonomy 3.0.tsv", "IAB_Content_Categories_EN_v3.0.json"),
    "3.1": ("Content Taxonomy 3.1.tsv", "IAB_Content_Categories_EN_v3.1.json"),
    "3.0-vectors": (
        "Content Taxonomy 3.0 Descriptive Vectors.tsv",
        "IAB_Content_Vectors_EN_v3.0.json",
    ),
}

# Colonnes du TSV, apres les deux lignes d'en-tete.
ID, PARENT, NAME = 0, 1, 2
EXTENSION = 7


def read_rows(text):
    """Renvoie les lignes de donnees du TSV, en-tetes et lignes vides exclues."""
    rows = list(csv.reader(text.splitlines(), delimiter="\t"))
    return [r for r in rows[2:] if any(cell.strip() for cell in r)]


def cell(row, index):
    return row[index].strip() if len(row) > index else ""


def build_tree(rows, extension_as_text=False):
    """Construit l'arbre des categories a partir des lignes du TSV.

    L'ordre du TSV est conserve. La colonne Extension devient un booleen `scd`
    (Sensitive Category Designation), sauf pour le fichier de vecteurs ou elle
    contient du texte libre et devient `extension`.
    """
    children = {}
    for row in rows:
        ext = cell(row, EXTENSION)
        node = {"id": cell(row, ID), "name": cell(row, NAME)}
        if extension_as_text:
            node["extension"] = ext or None
        else:
            node["scd"] = ext == "SCD"
        node["children"] = []
        children.setdefault(cell(row, PARENT), []).append(node)

    by_id = {node["id"]: node for nodes in children.values() for node in nodes}
    for parent_id, nodes in children.items():
        if parent_id:
            by_id[parent_id]["children"] = nodes
    return children.get("", [])


def count_nodes(nodes):
    return sum(1 + count_nodes(node["children"]) for node in nodes)


def validate(rows, tree):
    """Verifie l'integrite du TSV source et de l'arbre produit."""
    ids = [cell(row, ID) for row in rows]
    errors = []

    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        errors.append(f"IDs dupliques : {duplicates}")

    known = set(ids)
    orphans = sorted(
        {cell(r, PARENT) for r in rows if cell(r, PARENT) and cell(r, PARENT) not in known}
    )
    if orphans:
        errors.append(f"parents orphelins : {orphans}")

    if not ids:
        errors.append("aucune ligne de donnees dans le TSV")

    total = count_nodes(tree)
    if total != len(rows):
        errors.append(f"{total} noeuds dans l'arbre pour {len(rows)} lignes de TSV")

    return errors


def fetch(version, from_file=None):
    if from_file:
        return Path(from_file).read_text(encoding="utf-8-sig")
    filename = SOURCES[version][0]
    url = BASE_URL + urllib.parse.quote(filename)
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8-sig")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=sorted(SOURCES), help="version a convertir")
    parser.add_argument("-o", "--output", help="fichier JSON produit")
    parser.add_argument("--from-file", help="TSV local, au lieu du telechargement")
    args = parser.parse_args()

    rows = read_rows(fetch(args.version, args.from_file))
    tree = build_tree(rows, extension_as_text=args.version.endswith("-vectors"))

    errors = validate(rows, tree)
    if errors:
        for error in errors:
            print(f"erreur : {error}", file=sys.stderr)
        return 1

    output = Path(args.output or SOURCES[args.version][1])
    output.write_text(
        json.dumps(tree, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"{output} : {count_nodes(tree)} categories, {len(tree)} racines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
