docker kill cellxgene-gateway > /dev/null 2>&1
docker rm cellxgene-gateway > /dev/null 2>&1
docker run \
    -i -t --entrypoint /bin/bash \
    --name cellxgene-gateway cellxgene-gateway

