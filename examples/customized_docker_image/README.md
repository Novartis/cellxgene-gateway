# Purpose

This is a simple example of how to make a small script to customize the UI of cellxgene-gateway. The script that does the customization is `customize_ui.sh`, it simply makes the main header green using CSS but you could do anything you want there (including adding more script tags, etc).

# Usage

```
docker build -t cellxgene_custom .
CELLXGENE_DATA=`pwd`/../../../cellxgene_data
docker run -p 5005:5005 --mount src=$CELLXGENE_DATA,target=/cellxgene-data,type=bind cellxgene_custom
```

If you now open http://localhost:5005 you should see a green cellxgene gateway header.

