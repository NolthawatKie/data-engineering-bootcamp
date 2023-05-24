from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils import timezone

def _world() :
    print("world")

with DAG(
    dag_id="specific_datetime_every_month",
    schedule="0 18 3 * *",
    start_date=timezone.datetime(2023, 5, 1),
    catchup=False,
    tags=["DEB", "Skooldio"],
):

    hello = BashOperator(
        task_id = "hello",
        bash_command="echo hello",
    )

    world = PythonOperator(
        task_id = "world",
        python_callable=_world,
    )


    hello >> world
