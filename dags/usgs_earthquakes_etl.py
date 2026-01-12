from __future__ import annotations
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

from src.extract_usgs import fetch_usgs_geojson
from src.load_postgres import upsert_raw
from src.transform import build_curated_from_raw, run_quality_checks

ENGINE_URL = "postgresql+psycopg2://de_user:de_pass@postgres:5432/earthquakes"

def task_extract(**context):
    payload = fetch_usgs_geojson()
    context["ti"].xcom_push(key="payload", value=payload)

def task_load_raw(**context):
    payload = context["ti"].xcom_pull(key="payload")
    return upsert_raw(ENGINE_URL, payload)

def task_transform():
    return build_curated_from_raw(ENGINE_URL)

def task_quality():
    run_quality_checks(ENGINE_URL)

with DAG(
    dag_id="usgs_earthquakes_etl",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["data-engineering", "usgs", "postgres"],
) as dag:

    extract = PythonOperator(task_id="extract_usgs", python_callable=task_extract)
    load_raw = PythonOperator(task_id="load_raw_postgres", python_callable=task_load_raw)
    transform = PythonOperator(task_id="transform_to_curated", python_callable=task_transform)
    quality = PythonOperator(task_id="data_quality_checks", python_callable=task_quality)

    extract >> load_raw >> transform >> quality
