#!/usr/bin/env bash

SESSION_ID=$1

if [ -z "$SESSION_ID" ]
then
    echo "Usage: $0 session_id"; exit 1
else
    PYTHONPATH='.' SESSION_ID=$SESSION_ID python - <<EOF
from adap.settings import Config
Config.NAMESPACE = 'main'
from adap.perf_platform.utils import k8
session_labels = f'session_id={Config.SESSION_ID}'
k8.delete_all_labelled_resources(label=session_labels)
EOF

fi