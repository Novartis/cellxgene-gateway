ARG FROM_TAG=latest
FROM 386834949250.dkr.ecr.us-east-1.amazonaws.com/rightsize_99_standard_py37:$FROM_TAG

ADD cellxgene-gateway cellxgene-gateway

ADD cellxgene_data cellxgene_data

ENV CELLXGENE_LOCATION="`which cellxgene`"
ENV CELLXGENE_DATA="/home/celsiustx/cellxgene_data"

RUN pip install cellxgene-gateway

ENTRYPOINT ["cellxgene-gateway"]