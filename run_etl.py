import os
from src.extract_usgs import fetch_usgs_geojson
from src.load_postgres import upsert_raw
from src.transform import build_curated_from_raw, run_quality_checks

# Mets ici tes identifiants (ou utilise des variables d’environnement)
ENGINE_URL = os.getenv(
    "ENGINE_URL",
    "postgresql+psycopg2://de_user:de_pass@localhost:5432/earthquakes"
)

def main():
    print("1) Extract USGS…")
    payload = fetch_usgs_geojson()
    print(f"   -> features: {len(payload.get('features', []))}")

    print("2) Load RAW to Postgres…")
    n = upsert_raw(ENGINE_URL, payload)
    print(f"   -> upserted rows: {n}")

    print("3) Transform to CURATED…")
    m = build_curated_from_raw(ENGINE_URL)
    print(f"   -> transformed rows (best effort): {m}")

    print("4) Data quality checks…")
    run_quality_checks(ENGINE_URL)
    print("✅ Done")

if __name__ == "__main__":
    main()
