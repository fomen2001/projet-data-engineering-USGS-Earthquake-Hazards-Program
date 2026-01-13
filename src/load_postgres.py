from __future__ import annotations
from typing import Dict, Any, Iterable, Tuple
from sqlalchemy import create_engine, text
from src.utils import utc_now
import json

def iter_features(payload: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    """Yield GeoJSON features from a USGS FeatureCollection payload."""
    for f in payload.get("features", []):
        if isinstance(f, dict):
            yield f

def upsert_raw(engine_url: str, payload: Dict[str, Any]) -> int:
    """
    Upsert raw features into raw.usgs_earthquakes (JSONB).

    Returns number of upserted rows.
    """
    engine = create_engine(engine_url)
    fetched_at = utc_now()

    rows: list[Tuple[str, str, Dict[str, Any]]] = []
    for feat in iter_features(payload):
        event_id = feat.get("id")
        if not event_id:
            continue
        rows.append((event_id, fetched_at.isoformat(), feat))

    if not rows:
        return 0

    sql = text("""
        INSERT INTO raw.usgs_earthquakes (event_id, fetched_at, payload)
        VALUES (:event_id, :fetched_at, CAST(:payload AS JSONB))
        ON CONFLICT (event_id)
        DO UPDATE SET fetched_at = EXCLUDED.fetched_at,
                      payload    = EXCLUDED.payload;
    """)

    with engine.begin() as conn:
        conn.execute(
            sql,
            [
                {"event_id": r[0], "fetched_at": r[1], "payload": json.dumps(r[2])}
                for r in rows
            ],
        )

    return len(rows)
