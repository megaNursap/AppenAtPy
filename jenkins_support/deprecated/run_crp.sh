#!/bin/bash
pytest  -m "$2" --show-capture=no -v -s --env=$1 --spira=$4 --flaky=$3  --set="$2" --key="$5" --jenkins_test_url="$6" --deployment_url="$9" --crp="$7" --jira="$8" --json-report --json-report-omit collectors log  keywords --json-report-file none  --html=./result/report.html --junitxml=./result/junit_report.xml  --alluredir=allure_result_folder  adap/

