# IAB Content Categories

Les taxonomies de contenu de l'[IAB Tech Lab](https://iabtechlab.com/standards/content-taxonomy/),
converties en JSON.

## Versions disponibles

| Version | Fichier | Catégories | Format |
|---|---|---|---|
| 1.0 | [`IAB_Content_Categories_EN_v1.0.json`](IAB_Content_Categories_EN_v1.0.json) | 392 | dict plat `code → libellé` |
| 2.0 | [`IAB_Content_Categories_EN_v2.0.json`](IAB_Content_Categories_EN_v2.0.json) | 1179 | arbre `children` |
| 2.1 | [`IAB_Content_Categories_EN_v2.1.json`](IAB_Content_Categories_EN_v2.1.json) | 1179 | arbre `children` |
| 2.2 | [`IAB_Content_Categories_EN_v2.2.json`](IAB_Content_Categories_EN_v2.2.json) | 1196 | arbre `children` |
| 3.0 | [`IAB_Content_Categories_EN_v3.0.json`](IAB_Content_Categories_EN_v3.0.json) | 703 | arbre `children` |
| 3.0 | [`IAB_Content_Vectors_EN_v3.0.json`](IAB_Content_Vectors_EN_v3.0.json) | 47 | arbre `children`, champ `extension` |

## Formats

La **1.0** est un dictionnaire plat : la hiérarchie est encodée dans le code lui-même
(`IAB1` → `IAB1-1`). Elle vient de l'annexe de la spec OpenRTB 2.1, d'où le « 2.1 »
qu'on lui attribue parfois par erreur.

À partir de la **2.0**, l'IAB passe à un système d'IDs relationnels avec une colonne
`Parent` : la hiérarchie n'est plus déductible du code. Ces versions sont donc publiées
ici sous forme d'arbre :

```json
[
  {
    "id": "483",
    "name": "Sports",
    "scd": false,
    "children": [
      { "id": "533", "name": "Soccer", "scd": false, "children": [] }
    ]
  }
]
```

- `id` est une chaîne : à partir de la 2.2, l'IAB mélange IDs numériques (`483`) et
  alphanumériques (`80DV8O`).
- `scd` reprend la colonne `Extension` du TSV source : `true` pour une
  *Sensitive Category Designation*.
- `children` est toujours présent, vide sur les feuilles.
- L'ordre des nœuds suit celui du TSV source.

### Descriptive Vectors

La 3.0 s'accompagne d'un fichier annexe, les *Descriptive Vectors*, qui ne décrit pas
le sujet du contenu mais sa forme : environnement de diffusion, intention, source,
format, niveau de risque pour la marque. Ses IDs n'entrent pas en collision avec ceux
des catégories 3.0, les deux fichiers peuvent donc être utilisés ensemble.

Sa colonne `Extension` ne contient pas un flag SCD mais du texte libre. Il porte donc
un champ `extension` (chaîne ou `null`) à la place de `scd` :

```json
{
  "id": "1030",
  "name": "*Content Language Extension",
  "extension": "See ISO-639-1-alpha-2",
  "children": []
}
```

## Régénérer les fichiers

[`tools/tsv_to_json.py`](tools/tsv_to_json.py) convertit un TSV publié par l'IAB.
Sans dépendance externe, Python 3 seulement.

```sh
tools/tsv_to_json.py 3.1                 # télécharge le TSV et écrit le JSON
tools/tsv_to_json.py 3.1 --from-file x.tsv -o sortie.json
```

Le script refuse d'écrire si le TSV source contient des IDs dupliqués, des parents
orphelins, ou si l'arbre produit ne compte pas autant de nœuds que le TSV a de lignes.

## Sources

- Taxonomies IAB Tech Lab : <https://github.com/InteractiveAdvertisingBureau/Taxonomies>
- Content Taxonomy 1.0, via la spec OpenRTB 2.1 et
  <https://gist.github.com/crowdmatt/5040911>
