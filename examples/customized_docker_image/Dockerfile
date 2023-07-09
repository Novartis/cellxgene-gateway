FROM python:3.9

RUN pip install cellxgene-gateway 'MarkupSafe<2.1'

COPY customize_ui.sh customize_ui.sh
RUN CELLXGENE_GATEWAY_DIR=/usr/local/lib/python3.9/site-packages/cellxgene_gateway . ./customize_ui.sh

ENV CELLXGENE_DATA=/cellxgene-data
ENV CELLXGENE_LOCATION=/usr/local/bin/cellxgene
EXPOSE 5005

RUN mkdir /cellxgene-data

CMD ["cellxgene-gateway"]
