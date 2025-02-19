#!/bin/bash
pytest  -m "$2" -n 5 --show-capture=no -s --env=$1 --flaky=$3  --set="$2" --key="$4"  --browser_stack="true" --os_system="$5"  --browser="$6" --html=./result/report.html --junitxml=./result/junit_report.xml  --alluredir=allure_result_folder adap/

