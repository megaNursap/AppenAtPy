#!/usr/bin/env bash

echo "Ensure we can interact with ECR"
set +x
$(aws ecr get-login --registry-ids $AWS_ACCOUNT --no-include-email --region us-east-1)
set -xe
set +e
echo "Set kubeconfig to use devspace ${NAMESPACE}"
aws eks --region us-east-1 update-kubeconfig --name engineering-devspace-sandbox
kubectl config set-context --current --namespace="${NAMESPACE}"

