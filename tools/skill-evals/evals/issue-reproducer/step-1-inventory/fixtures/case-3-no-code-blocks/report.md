Issue: AIRFLOW-88404
Title: Scheduler becomes unresponsive after 48 hours

Body:
  After running the Airflow scheduler for approximately 48 hours without restart,
  it stops scheduling new task instances. No error is logged.

  Environment: Airflow 2.9.1, PostgreSQL 15, Python 3.11, Kubernetes deployment.

Comments:
  (none)
