from __future__ import annotations
import pandas as pd
from sqlalchemy import create_engine, text

def build_curated_from_raw(engine_url: str) -> int:
    """
    Transform raw JSONB records into curated.earthquakes (flattened schema).
    Uses SQL extraction from JSONB for robustness.
    """
    engine = create_engine(engine_url)

    transform_sql = text("""
    INSERT INTO curated.earthquakes (
      event_id, event_time, updated_time, place, magnitude, mag_type, status, tsunami,
      latitude, longitude, depth_km, url, source, fetched_at
    )
    SELECT
      r.event_id,
      to_timestamp( (r.payload->'properties'->>'time')::double precision / 1000.0 ) AT TIME ZONE 'UTC' AS event_time,
      to_timestamp( (r.payload->'properties'->>'updated')::double precision / 1000.0 ) AT TIME ZONE 'UTC' AS updated_time,
      r.payload->'properties'->>'place' AS place,
      NULLIF(r.payload->'properties'->>'mag','')::double precision AS magnitude,
      r.payload->'properties'->>'magType' AS mag_type,
      r.payload->'properties'->>'status' AS status,
      NULLIF(r.payload->'properties'->>'tsunami','')::smallint AS tsunami,
      (r.payload->'geometry'->'coordinates'->>1)::double precision AS latitude,
      (r.payload->'geometry'->'coordinates'->>0)::double precision AS longitude,
      (r.payload->'geometry'->'coordinates'->>2)::double precision AS depth_km,
      r.payload->'properties'->>'url' AS url,
      r.payload->'properties'->>'net' AS source,
      r.fetched_at
    FROM raw.usgs_earthquakes r
    ON CONFLICT (event_id)
    DO UPDATE SET
      event_time   = EXCLUDED.event_time,
      updated_time = EXCLUDED.updated_time,
      place        = EXCLUDED.place,
      magnitude    = EXCLUDED.magnitude,
      mag_type     = EXCLUDED.mag_type,
      status       = EXCLUDED.status,
      tsunami      = EXCLUDED.tsunami,
      latitude     = EXCLUDED.latitude,
      longitude    = EXCLUDED.longitude,
      depth_km     = EXCLUDED.depth_km,
      url          = EXCLUDED.url,
      source       = EXCLUDED.source,
      fetched_at   = EXCLUDED.fetched_at;
    """)

    with engine.begin() as conn:
        res = conn.execute(transform_sql)
        # rowcount peut être -1 selon driver; on renvoie un int "best effort"
        return int(res.rowcount) if res.rowcount is not None else 0

def run_quality_checks(engine_url: str) -> None:
    """
    Basic data quality checks (raise error if failed).
    """
    engine = create_engine(engine_url)
    checks = [
      ("event_id_not_null", "SELECT COUNT(*) FROM curated.earthquakes WHERE event_id IS NULL"),
      ("mag_range", "SELECT COUNT(*) FROM curated.earthquakes WHERE magnitude IS NOT NULL AND (magnitude < -1 OR magnitude > 12)"),
      ("coords_not_null", "SELECT COUNT(*) FROM curated.earthquakes WHERE latitude IS NULL OR longitude IS NULL"),
    ]

    with engine.begin() as conn:
        for name, q in checks:
            bad = conn.execute(text(q)).scalar()
            if bad and int(bad) > 0:
                raise ValueError(f"Data quality check failed: {name} (bad_rows={bad})")
