FROM python:3.11

RUN pip install --upgrade pip
RUN pip install "cellxgene-gateway>=0.4"

ENV CELLXGENE_DATA=/cellxgene-data
ENV CELLXGENE_LOCATION=/usr/local/bin/cellxgene

CMD ["cellxgene-gateway"]
