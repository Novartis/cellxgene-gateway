# make the header bright green
find "${CELLXGENE_GATEWAY_DIR}/templates" -name index.html -exec sed -i -e 's/<head>/<head>\
> <style> header h3 {color: #0F0;} <\/style>/g' {} \;
