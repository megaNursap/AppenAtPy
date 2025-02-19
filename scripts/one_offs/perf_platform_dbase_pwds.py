import subprocess
import re


def get_pg_pwd():
    print("get postgres user password from secret")
    pgpassword = 'kubectl get secret --namespace main ' \
                 'results-db-timescaledb-passwords ' \
                 '-o jsonpath="{.data.postgres}" | base64 --decode'
    pgpassword = subprocess.check_output(pgpassword, shell=1).decode('utf8')
    print(f"pgpassword: {pgpassword}\n")
    assert len(pgpassword) > 0
    return pgpassword

def get_qa_perf_db_pwd():
    print("get qa_performance_db user password from secret")
    qa_perf_db_password = 'kubectl get secret --namespace main ' \
                          'db-conn-details ' \
                          '-o jsonpath="{.data.RESULTS_DB_PASSWORD}" | ' \
                          'base64 --decode'
    qa_perf_db_password = subprocess.check_output(qa_perf_db_password, shell=1).decode('utf8')
    assert len(qa_perf_db_password)>0
    print(f"qa_perf_db_password: {qa_perf_db_password}\n")
    return qa_perf_db_password

def get_grafana_pwd():
    print("get grafana user password from grafana datasource")
    grafana_datasource = 'kubectl get configmaps -n monitoring ' \
                         'prometheus-operator-grafana-datasource ' \
                         '-o jsonpath="{.data}"'
    grafana_datasource = subprocess.check_output(grafana_datasource, shell=1).decode('utf8')
    grafana_password = list(set(re.findall(r'(?<=password: \\").+?(?=\\")', grafana_datasource)))
    assert len(grafana_password) == 1
    grafana_password = grafana_password[0]
    print(f"Grafana password: {grafana_password}\n")
    return grafana_password




