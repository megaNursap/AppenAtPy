#!/bin/bash
echo $3
pytest  -m "$2 and not skip_hipaa" --show-capture=no --env=$1 --flaky=$3 --html=./result/report.html --junitxml=./result/junit_report.xml  --alluredir=allure_result_folder adap/
echo "REPORT"
allure generate ./allure_result_folder/ -o ./allure_report/ --clean
