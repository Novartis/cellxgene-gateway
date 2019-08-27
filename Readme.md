# Overview #

Cellxgene Gateway allows you to use the Cellxgene Server provided by the Chan Zuckerberg Institute (https://github.com/chanzuckerberg/cellxgene) with multiple datasets. It displays an index of available h5ad (anndata) files. When a user clicks on a file name, it launches a Cellxgene Server instance that loads that particular data file and once it is available  proxies requests to that server.

# Running locally #

Before running the gateway, make sure you can run the Cellxgene Server from CZI, and that you have a folder with h5ad files ready to view.

The first step is to set up an environment and install requirements:
```
# create an environment for packages
python -m venv .cellxgene-gateway
source .cellxgene-gateway/bin/activate
# install requirements
pip install -r requirements.txt
```
Then copy run.sh.example to run.sh and edit
```
cp run.sh.example run.sh
```

`run.sh` defines various environment variables, you probably only need to edit CELLXGENE_LOCATION and CELLXGENE_DATA:

* DEPLOYMENT_ENV - expects 'dev', 'tst' or 'prd'
* CELLXGENE_LOCATION - the location of the cellxgene executable, e.g. ~/anaconda2/envs/cellxgene/bin/cellxgene
* CELLXGENE_DATA - a directory that can contain subdirectories with .h5ad data files, *without* trailing slash, e.g. /mnt/cellxgene_data
* GATEWAY_HOST - the hostname and port that the gateway will run on, typically localhost:5005 if running locally
* GATEWAY_PROTOCOL - typically http when running locally, can be https when deployed if the gateway is behind a load balancer or reverse proxy.

Finally, execute run.sh:
```
source run.sh
```

# Customization #

The current paradigm for customization is to modify files during a build or deployment phase:

* To modify CSS or JS on particular gateway pages, overwrite or append to the templates
* To add script tags such as for user analytics to all pages, overwrite the extra_scripts.py file.
  * these scripts will also be run on the pages served by cellxgene server via the --scripts parameter
  * See https://github.com/chanzuckerberg/cellxgene/pull/680 for details on --scripts parameter

Currently we use a build.sh that copies the gateway to a "build" directory before modifying with sed and the like.

# Development #

## Running Linters ##

pip install isort flake8 black

```
isort -rc .
```

```
flake8 .
```

```
black .
```

# Getting Help #

If you need help for any reason, please make a github ticket. One of the contributors should help you out.

# Contributors #

* Niket Patel - https://github.com/NiketPatel9
* Alok Saldanha - https://github.com/alokito
* Yohann Potier - https://github.com/ypotier
