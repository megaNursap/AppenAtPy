"""
Script intends to get the passwords required for manually creating/connection the platform_performance database.
Requires kubectl installed with permissions to get secrets in main namespace
and configmaps in monitoring namespace.
Important: login to AWS prior to executing
"""

from perf_platform_dbase_pwds import get_pg_pwd,get_qa_perf_db_pwd, get_grafana_pwd


def main():
    get_pg_pwd()
    get_qa_perf_db_pwd()
    get_grafana_pwd()


if __name__ == '__main__':
    main()

