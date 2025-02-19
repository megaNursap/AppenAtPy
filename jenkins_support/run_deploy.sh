#!/bin/bash
pytest  -m ${2/'-'/'_'} --show-capture=no -s --env=$1 --key="$3" --html=./result/report.html --junitxml=./result/junit_report.xml  --alluredir=allure_result_folder adap/
