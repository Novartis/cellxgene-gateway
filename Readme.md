# Overview

Cellxgene Gateway allows you to use the Cellxgene Server provided by the Chan Zuckerberg Institute (https://github.com/chanzuckerberg/cellxgene) with multiple datasets. It displays an index of available h5ad (anndata) files. When a user clicks on a file name, it launches a Cellxgene Server instance that loads that particular data file and once it is available  proxies requests to that server.

# Running locally

## Prequisites

0. This project requires python 3.6 or higher. Please check your version with

```bash
$ python --version
```

1. It is also a good idea to set up a venv

```bash
python -m venv .cellxgene-gateway
source .cellxgene-gateway/bin/activate # type `deactivate` to deactivate the venv
```

## Install cellxgene-gateway

### Option 1: Pip Install from Github

```bash
pip install git+https://github.com/Novartis/cellxgene-gateway
```

### Option 2: Install from PyPI

```bash
# NOT YET DONE, COMING! STAY TUNED
```

### Option 3: Developer Install

If you want to develop the code, you will need to clone the repo.

1. Clone the repo

```bash
    git clone https://github.com/Novartis/cellxgene-gateway.git
    cd cellxgene-gateway
```

2. Install requirements with

```bash
pip install -r requirements.txt
```

3. Install the gateway in developer mode

```bash
python setup.py develop
```

For convenience, the code repo includes a `run.sh.example` shell script to run the gateway.

## Running cellxgene gateway

1. Prepare a folder with .h5ad files, for example

```bash
mkdir ../cellxgene_data
wget https://github.com/chanzuckerberg/cellxgene/raw/master/example-dataset/pbmc3k.h5ad -O ../cellxgene_data/pbmc3k.h5ad
```


2. Set your environment variables correctly:

```bash
export CELLXGENE_LOCATION=`which cellxgene`
export CELLXGENE_DATA=../cellxgene_data  # change this directory if you put data in a different place.
export GATEWAY_HOST=localhost:5005
export GATEWAY_PROTOCOL=http
export GATEWAY_IP=127.0.0.1
```

3. Now, execute the cellxgene gateway:

```bash
cellxgene-gateway
```

Here's what the environment variables mean:

* `CELLXGENE_LOCATION` - the location of the cellxgene executable, e.g. `~/anaconda2/envs/cellxgene/bin/cellxgene`
* `CELLXGENE_DATA` - a directory that can contain subdirectories with `.h5ad` data files, *without* trailing slash, e.g. `/mnt/cellxgene_data`
* `GATEWAY_HOST` - the hostname and port that the gateway will run on, typically `localhost:5005` if running locally
* `GATEWAY_PROTOCOL` - typically http when running locally, can be https when deployed if the gateway is behind a load balancer or reverse proxy.

The defaults should be fine if you set up a venv and cellxgene_data folder as above.

# Customization

The current paradigm for customization is to modify files during a build or deployment phase:

* To modify CSS or JS on particular gateway pages, overwrite or append to the templates
* To add script tags such as for user analytics to all pages, overwrite the extra_scripts.py file.
  * these scripts will also be run on the pages served by cellxgene server via the --scripts parameter
  * See https://github.com/chanzuckerberg/cellxgene/pull/680 for details on --scripts parameter

Currently we use a build.sh that copies the gateway to a "build" directory before modifying with sed and the like.

# Development

## Running Linters

pip install isort flake8 black

```bash
isort -rc .
flake8 .
black -l 79 .
```

# Getting Help

If you need help for any reason, please make a github ticket. One of the contributors should help you out.

# Contributors

* Niket Patel - https://github.com/NiketPatel9
* Alok Saldanha - https://github.com/alokito
* Yohann Potier - https://github.com/ypotier
