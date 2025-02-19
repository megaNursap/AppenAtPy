#!/bin/bash
pytest  -m "$2" --show-capture=no -s --env=$1 --spira=$4 --flaky=$3  --set="$2" --key="$5" --html=./result/report.html --junitxml=./result/junit_report.xml  --alluredir=allure_result_folder adap/

