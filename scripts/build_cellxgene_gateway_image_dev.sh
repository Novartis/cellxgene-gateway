#!/usr/bin/env bash

TAG=cellxgene-gateway

if [[ -z ${CTX_HOME} ]]; then
    echo Please set CTX _HOME to the root of your repos.  It will be used as a temporory build environment
    exit 1
fi
echo ""

BUILD_DIR=${CTX_HOME}

CWD=$(pwd)
PID=$$

cd ${BUILD_DIR}

if [[ -f ".dockerignore" ]]; then
    echo Backing up existing .dockerignore
    cp .dockerignore .dockerignore.${PID}
fi


echo "" > .dockerignore

RETAIN="cellxgene-gateway cellxgene_data"

for fname in *; do
    if [[ ${RETAIN} =~ ${fname} ]]; then
        echo Including ${fname} in build context
    else
        echo ${fname} >> .dockerignore
    fi
done

for R in ${RETAIN}
do
    if [[ -f ${R}/.dockerignore ]]; then
        echo Processing .dockerignore in ${R}
        while read p; do
#            echo adding ${R}/${p} to dockerignore
            echo ${R}/${p} >> .dockerignore
        done<${R}/.dockerignore
    fi
done

docker build -t ${TAG} -f cellxgene-gateway/infrastructure/docker/Dockerfile .
RV=$?

if [[ ${RV} == 0 ]]; then
    echo Success, cleaning up
    rm .dockerignore
    if [[ -f ".dockerignore.${PID}" ]]; then
        echo Restoring previous .dockerignore
        mv .dockerignore.${PID} .dockerignore
    fi
else
    echo Problem with build

fi

cd ${CWD}

exit ${RV}
