From: alice@example.com
Subject: Apache Airflow REST API exposes DAG execution data without login

I discovered that the Airflow REST API does not enforce authentication on the
DAG runs endpoint. By sending a GET request to /api/v1/dags/my_dag/dagRuns
with no Authorization header, I receive a full JSON response with task states,
execution dates, and logs. This affects any Airflow deployment with the REST
API enabled. Version tested: 2.9.3.
