#!/bin/bash

if [[ $1 == ac_* ]]; then
    TESTPATH='appen_connect/'
elif [[ $1 == 'adap_ac' ]]; then
	  TESTPATH='integration/'
elif [[ $1 == 'gap' ]]; then
	  TESTPATH='gap/'
else
	  TESTPATH='adap/'
fi

pytest  -m "$2" -n 3 --dist=loadscope --show-capture=no -s --env=$1 --flaky=$3  --set="$2" --key="$4" --crp="$5" --jenkins_test_url="$6" --json-report --json-report-omit collectors log  keywords --json-report-file none  --html=./result/report.html --junitxml=./result/junit_report.xml  --alluredir=allure_result_folder  $TESTPATH

