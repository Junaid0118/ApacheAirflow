from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd

# ---- Functions ----

def extract(ti, **kwargs):
    df = pd.read_csv('utils/deliveries.csv')
    ti.xcom_push(key='data', value=df.to_dict())
    print("Extracted data")

def transform(ti, **kwargs):
    data = ti.xcom_pull(key='data', task_ids='extract_task')
    transformed_data = pd.DataFrame.from_dict(data)[['match_no']]
    ti.xcom_push(key='transformed_data', value=transformed_data.to_dict())
    print("Transformed data")

def load(ti, **kwargs):
    data = ti.xcom_pull(key='transformed_data', task_ids='transform_task')
    df = pd.DataFrame.from_dict(data)
    df.to_csv('output.csv', index=False)
    print("Data loaded into output.csv")

# ---- DAG Definition ----

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
    'email': ['junaidiqbalshah011@gmail.com'],     
    'email_on_failure': True,
    'email_on_retry': False,     
}

with DAG(
    dag_id='etl_csv_pipeline',
    default_args=default_args,
    description='Simple ETL DAG with CSV',
    start_date=datetime(2025, 8, 25),
    schedule='@daily',  # Updated from schedule_interval
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id='extract_task',
        python_callable=extract,
        sla=timedelta(minutes=1),
    )

    transform_task = PythonOperator(
        task_id='transform_task',
        python_callable=transform,
    )

    load_task = PythonOperator(
        task_id='load_task',
        python_callable=load,
    )

    extract_task >> transform_task >> load_task
