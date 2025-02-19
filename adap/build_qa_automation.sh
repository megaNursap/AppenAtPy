#!/usr/bin/env bash

checkImage() {
  docker image inspect ${CURRENT_BUILD_IMAGE_NAME} 2> /dev/null
}

echo "FORCE_IMAGE_REBUILD=$FORCE_IMAGE_REBUILD"
echo "Checking for qa-automation image for ${NAMESPACE}"
if [ "$(checkImage)" = '[]' ]; then
  echo "No image in local docker trying to pull from ECR"
  docker pull ${CURRENT_BUILD_IMAGE_NAME} 2> /dev/null
fi
if [ "$(checkImage)" = '[]' ] || [ "$FORCE_IMAGE_REBUILD" = 'true' ]; then
  echo "qa-automation image not yet built or build forced"
  docker build -t ${CURRENT_BUILD_IMAGE_NAME} .
  echo "Archiving ${CURRENT_BUILD_IMAGE_NAME} for subsequent test runs"
  docker push ${CURRENT_BUILD_IMAGE_NAME} 
fi
