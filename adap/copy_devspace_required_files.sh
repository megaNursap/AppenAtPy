#!/usr/bin/env bash

echo "Using kubectl NAMESPACE = $NAMESPACE"
kubectl config current-context
akon_web=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" | grep akon-web)
if [[ -n "$akon_web" ]]; then
  echo "Connecting to $akon_web to copy files"
  echo "Copying $akon_web:account_devspace.json to adap/data/account_devspace.json"
  kubectl cp $akon_web:account_devspace.json -c web ./adap/data/account_devspace.json
  head -40 ./adap/data/account_devspace.json
  echo "Writing qa_secret.key from akon-services:web environment"
  kubectl cp $akon_web:qa_secret.key -c web ./qa_secret.key
  cat qa_secret.key

  make_web=$(kubectl get pods -l app.kubernetes.io/component=make-services --no-headers -o custom-columns=":metadata.name")
  echo "Connecting to $make_web to copy files"
  [ -f ./adap/data/predefined_data.json ] && echo "Backing up ./adap/data/predefined_data.json" && cp ./adap/data/predefined_data.json ./adap/data/predefined_data.json.bak-$(date +'%s')
  echo "Copying $make_web:predefined_data.json"
  kubectl cp -c web $make_web:predefined_data.json ./adap/data/predefined_data.json 
  head -40 ./adap/data/predefined_data.json

  echo "if any of the file are missing, run \`devspace run qa_integration_init\` in akon and/or make as needed"
else 
  echo "No pod found with 'kubectl get pods --no-headers -o custom-columns=\":metadata.name\" | grep akon-web'"
  kubectl get pods
  exit 1
fi
