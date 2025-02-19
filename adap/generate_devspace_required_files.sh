#!/usr/bin/env bash

echo "Run rake tasks to generate qa datafiles for ${NAMESPACE}"
echo "  generate qa_secret.key and account_devspace.json in akon"
kubectl rollout status deployment akon-web-deployment
kubectl logs -f deploy/akon-web-deployment -c init-akon-db
kubectl rollout status deployment make-services --timeout=180s
kubectl logs -f deploy/make-services -c init-make-db
kubectl exec -i deploy/akon-web-deployment -c web -- /app/script/entrypoint_devspace.sh bundle exec rake create_qa_integration_test_users FORCE_DATAFILE_REGEN=${FORCE_DATAFILE_REGEN}
echo "  generate predefined_data.json in make"
kubectl rollout status deployment make-services
kubectl exec -i deploy/make-services -c web -- /app/script/entrypoint_devspace.sh bundle exec rake create_qa_automation_test_jobs FORCE_DATAFILE_REGEN=${FORCE_DATAFILE_REGEN}
