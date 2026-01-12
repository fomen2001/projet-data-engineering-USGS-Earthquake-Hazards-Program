CREATE TABLE IF NOT EXISTS raw.usgs_earthquakes (
  event_id TEXT PRIMARY KEY,
  fetched_at TIMESTAMPTZ NOT NULL,
  payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS curated.earthquakes (
  event_id TEXT PRIMARY KEY,
  event_time TIMESTAMPTZ,
  updated_time TIMESTAMPTZ,
  place TEXT,
  magnitude DOUBLE PRECISION,
  mag_type TEXT,
  status TEXT,
  tsunami SMALLINT,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  depth_km DOUBLE PRECISION,
  url TEXT,
  source TEXT,
  fetched_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_curated_event_time ON curated.earthquakes(event_time);
CREATE INDEX IF NOT EXISTS idx_curated_mag ON curated.earthquakes(magnitude);
