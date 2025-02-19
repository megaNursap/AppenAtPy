#!/bin/bash
pytest  -m "$2" -n 6 --dist=loadscope  --show-capture=no -v -s --env=$1  --set="$2" --key="$3" --jenkins_test_url="$4" --crp="$5" --jira="$6" --deployment_url="$7" --json-report --json-report-omit collectors log  keywords --json-report-file none  --html=./result/report.html --junitxml=./result/junit_report.xml  --alluredir=allure_result_folder

