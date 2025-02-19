#!/bin/bash
echo "locust"
pip install -r requirements.txt
cd files
TEST_ENV=$4 WAIT_CONFIG_TYPE=$5 WAIT_TIME=$6 locust -f adap/deprecated/performance/tasks/$7.py --no-web --clients=$1 --run-time=$3m --hatch-rate=$2 --csv=./../results/report.csv --only-summary
