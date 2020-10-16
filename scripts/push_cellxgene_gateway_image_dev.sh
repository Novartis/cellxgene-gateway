#!/usr/bin/env bash 
ECRREPO=386834949250.dkr.ecr.us-east-1.amazonaws.com/cellxgene-gateway

if [[ -n "$1" ]]; then
    DEPLOYMENT_ENV=$1
else
    DEPLOYMENT_ENV=$(whoami)
fi

echo Will tag with: ${DEPLOYMENT_ENV}

RED="\033[0;31m"
GREEN="\033[0;32m"
NC="\033[0m"

# ./build_ctxcommon_image_dev.sh
if [[ $? != 0 ]]; then
    echo -e ${RED}Problem building image${NC}
    exit 1
fi

DATE=`date +"%Y%m%d%H%M"`
DATE_TAG=$ECRREPO:$DATE
FINAL_TAG=$ECRREPO:${DEPLOYMENT_ENV}

docker tag cellxgene-gateway:latest $FINAL_TAG
docker tag $FINAL_TAG $DATE_TAG

echo Pushing ${DEPLOYMENT_ENV} tag to ECR
$(aws ecr get-login --no-include-email --region us-east-1)
docker push $DATE_TAG
docker push $FINAL_TAG

echo -e ${GREEN}Done pushing cellxgene-gateway with tag ${DEPLOYMENT_ENV} ${NC}
