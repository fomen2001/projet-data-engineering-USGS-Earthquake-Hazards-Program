Ce projet de Data Engineering proche des standards industriels consiste à ingérer des données publiques sur les séismes à partir des flux GeoJSON de l’USGS, à les stocker dans une base de données PostgreSQL, à les transformer en données analytiques exploitables, puis à orchestrer l’ensemble du pipeline avec Apache Airflow, le tout dans un environnement dockerisé.

📊 Jeu de données

USGS Earthquake Hazards Program — Flux GeoJSON publics (sans clé API)

Ces flux fournissent des informations en quasi temps réel sur les séismes :

magnitude

localisation

date et heure

profondeur

coordonnées géographiques

🔗 Source officielle :
https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

👉 Concrètement : on récupère automatiquement les séismes survenus dans le monde (par exemple sur les dernières 24 heures).

🏗️ Architecture du projet (Vue d’ensemble)
1️⃣ Extraction (Extract)

Ce que l’on fait
On interroge l’API publique de l’USGS pour récupérer les données de séismes au format GeoJSON (flux des dernières 24 heures).

👉 Pourquoi ?
C’est une situation réaliste de récupération de données externes via API, très courante en entreprise.

2️⃣ Chargement – couche brute (Load / Raw)

Ce que l’on fait
Chaque événement sismique est stocké tel quel dans PostgreSQL, dans une table appelée :

raw.usgs_earthquakes


Les données sont stockées en JSONB

Chaque séisme a un identifiant unique

👉 Pourquoi ?

Conserver la donnée originale sans perte

Permettre un retraitement ultérieur

Assurer la traçabilité des données

3️⃣ Transformation – couche analytique (Transform / Curated)

Ce que l’on fait
On extrait les champs utiles du JSON (date, magnitude, lieu, coordonnées…) pour créer une table structurée :

curated.earthquakes


👉 Pourquoi ?

Les données sont plus faciles à interroger en SQL

Meilleures performances

Données prêtes pour l’analyse, la BI ou le machine learning

4️⃣ Contrôles de qualité (Data Quality Checks)

Ce que l’on fait
On vérifie automatiquement :

qu’un identifiant de séisme existe

que les magnitudes sont dans des valeurs cohérentes

que les coordonnées géographiques sont présentes

👉 Pourquoi ?

Éviter des données corrompues

Garantir la fiabilité du pipeline

5️⃣ Orchestration avec Apache Airflow

Ce que l’on fait
Un DAG Airflow planifie et enchaîne automatiquement :

l’extraction

le chargement

la transformation

les contrôles de qualité

👉 Pourquoi ?

Automatisation complète

Supervision visuelle

Relance facile en cas d’erreur

🧰 Technologies utilisées

Python : ingestion API, transformation des données

PostgreSQL : stockage des données (raw + curated)

Apache Airflow : orchestration et planification

Docker Compose : environnement reproductible

👉 En clair : n’importe qui peut lancer le projet avec une seule commande.