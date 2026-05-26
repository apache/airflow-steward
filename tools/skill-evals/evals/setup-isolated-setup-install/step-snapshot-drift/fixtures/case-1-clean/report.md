## Snapshot lock file state

cat .apache-steward.lock:
  method: git-branch
  url: https://github.com/apache/airflow-steward.git
  ref: v0.9.2

cat .apache-steward.local.lock:
  method: git-branch
  url: https://github.com/apache/airflow-steward.git
  ref: v0.9.2

Result: lock files match — no drift detected.
