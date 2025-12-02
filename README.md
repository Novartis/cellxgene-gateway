# Overview

Cellxgene Gateway allows you to use the Cellxgene Server provided by the Chan Zuckerberg Institute (https://github.com/chanzuckerberg/cellxgene) with multiple datasets. It displays an index of available h5ad (anndata) files. When a user clicks on a file name, it launches a Cellxgene Server instance that loads that particular data file and once it is available  proxies requests to that server.

[![codecov](https://codecov.io/gh/Novartis/cellxgene-gateway/branch/master/graph/badge.svg?token=ndEFSzRKJn)](https://codecov.io/gh/Novartis/cellxgene-gateway) [![PyPI](https://img.shields.io/pypi/v/cellxgene-gateway)](https://pypi.org/project/cellxgene-gateway/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/cellxgene-gateway)](https://pypistats.org/packages/cellxgene-gateway)

# Running locally

## Prequisites

1. This project requires python 3.6 or higher. Please check your version with

```bash
$ python --version
```

2. It is also a good idea to set up a venv

```bash
python -m venv .cellxgene-gateway
source .cellxgene-gateway/bin/activate # type `deactivate` to deactivate the venv
```

## Install cellxgene-gateway

### Option 1: Pip Install from Github

```bash
pip install git+https://github.com/Novartis/cellxgene-gateway
```
Note: you may need to downgrade h5py with `pip install h5py==2.9.0` due to an [issue](https://github.com/theislab/scanpy/issues/832) in a dependency.
### Option 2: Install from PyPI

```bash
pip install cellxgene-gateway
```

## Running cellxgene gateway

1. Prepare a folder with .h5ad files, for example

```bash
mkdir ../cellxgene_data
wget https://raw.githubusercontent.com/chanzuckerberg/cellxgene/master/example-dataset/pbmc3k.h5ad -O ../cellxgene_data/pbmc3k.h5ad
```


2. Set your environment variables correctly:

```bash
export CELLXGENE_DATA=../cellxgene_data  # change this directory if you put data in a different place.
export CELLXGENE_LOCATION=`which cellxgene`
```

3. Now, execute the cellxgene gateway:

```bash
cellxgene-gateway
```

Here's what the environment variables mean:

* `CELLXGENE_LOCATION` - the location of the cellxgene executable, e.g. `~/anaconda2/envs/cellxgene/bin/cellxgene`

At least one of the following is required:
* `CELLXGENE_DATA` - a directory that can contain subdirectories with `.h5ad` data files, *without* trailing slash, e.g. `/mnt/cellxgene_data`
* `CELLXGENE_BUCKET` - an s3 bucket that can contain keys with `.h5ad` data files, e.g. `my-cellxgene-data-bucket`
Cellxgene Gateway is designed to make it easy to add additional data sources, please see the source code for gateway.py and the ItemSource interface in items/item_source.py

Optional environment variables:
* `CELLXGENE_ARGS` - catch-all variable that can be used to pass additional command line args to cellxgene server
* `EXTERNAL_HOST` - the hostname and port from the perspective of the web browser, typically `localhost:5005` if running locally. Defaults to "localhost:{GATEWAY_PORT}"
* `EXTERNAL_PROTOCOL` - typically http when running locally, can be https when deployed if the gateway is behind a load balancer or reverse proxy that performs https termination. Default value "http"
* `GATEWAY_IP` - ip addess of instance gateway is running on, mostly used to display SSH instructions. Defaults to `socket.gethostbyname(socket.gethostname())`
* `GATEWAY_PORT` - local port that the gateway should bind to, defaults to 5005
* `GATEWAY_EXPIRE_SECONDS` - time in seconds that a cellxgene process will remain idle before being terminated. Defaults to 3600 (one hour)
* `GATEWAY_EXTRA_SCRIPTS` - JSON array of script paths, will be embedded into each page and forwarded with `--scripts` to cellxgene server
* `GATEWAY_ENABLE_ANNOTATIONS` - Set to `true` or to `1` to enable cellxgene annotations and gene sets.
* `GATEWAY_ENABLE_BACKED_MODE` - Set to `true` or to `1` to load AnnData in file-backed mode. This saves memory and speeds up launch time but may reduce overall performance.
* `GATEWAY_LOG_LEVEL` - default is `INFO`. set to `DEBUG` to increase logging and to `WARNING` to decrease logging.
* `S3_ENABLE_LISTINGS_CACHE` - Set to `true` or to `1` to cache listings of S3 folders for performance. If the cache becomes stale, set `filecrawl.html?refresh=true` query parameter to refresh the cache.

If any of the following optional variables are set, [ProxyFix](https://werkzeug.palletsprojects.com/en/1.0.x/middleware/proxy_fix/) will be used.
* `PROXY_FIX_FOR` - Number of upstream proxies setting X-Forwarded-For
* `PROXY_FIX_PROTO` - Number of upstream proxies setting X-Forwarded-Proto
* `PROXY_FIX_HOST` - Number of upstream proxies setting X-Forwarded-Host
* `PROXY_FIX_PORT` - Number of upstream proxies setting X-Forwarded-Port
* `PROXY_FIX_PREFIX` - Number of upstream proxies setting X-Forwarded-Prefix

The defaults should be fine if you set up a venv and cellxgene_data folder as above.

## Running cellxgene-gateway with Docker

First, build Docker image:

```bash
docker build -t cellxgene-gateway .
```

Then, cellxgene-gateway can be launched as such:

```bash
docker run -it --rm \
-v <local_data_dir>:/cellxgene-data \
-p 5005:5005 \
cellxgene-gateway
```

Additional environment variables can be provided with the `-e` parameter:

```bash
docker run -it --rm \
-v ../cellxgene_data:/cellxgene-data \
-e GATEWAY_PORT=8080 \
-p 8080:8080 \
cellxgene-gateway
```
## Running cellxgene gateway with start scripts

For your convenience, we provide start scripts for flask, gunicorn and uwsgi.

First, set up a .env
```bash
cp env_example .env
# edit .env
open .env
```

Then run the scripts in a subshell
```bash
( ./start_flask.sh )
```

# Customization

The current paradigm for customization is to modify files during a build or deployment phase:

* To modify CSS or JS on particular gateway pages, overwrite or append to the templates
* To add script tags such as for user analytics to all pages, set GATEWAY_EXTRA_SCRIPTS
  * these scripts will also be run on the pages served by cellxgene server via the --scripts parameter
  * See https://github.com/chanzuckerberg/cellxgene/pull/680 for details on --scripts parameter

Currently we use a bash script that copies the gateway to a "build" directory before modifying templates with sed and the like. There is probably a better way.

# Development

We’re actively developing.  Please see the "future work" section of the [wiki](https://github.com/Novartis/cellxgene-gateway/wiki#future-work). If you’re interested in being a contributor please reach out to [@alokito](https://github.com/alokito).

## Developer Install

If you want to develop the code, you will need to clone the repo. Make sure you have the prequesite listed above, then:

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

4. Install pre-commit hooks

```bash
conda install -c conda-forge pre-commit
pre-commit install
```

## Dependency Management

This project uses pinned dependencies to ensure reproducible installs and prevent version drift issues.

### Conda Environment (Recommended for Development)

* **`environment.yml`** - High-level conda and pip dependencies
* **`conda-lock.yml`** - Fully locked conda environment for linux-64, osx-64, and osx-arm64 (committed to git)

### Pure Pip Installation

* **`requirements.in`** - High-level dependencies used by setup.py for package installation
* **`requirements.txt`** - Fully pinned lock file for reproducible development environments (generated from requirements.in, committed to git)
* **`uv.lock`** - Alternative lock file for [uv](https://github.com/astral-sh/uv) users (generated from requirements.in, committed to git)

### Installing Dependencies

**For package installation (end users):**
```bash
# setup.py reads requirements.in for flexible dependency resolution
pip install .
# or from PyPI:
pip install cellxgene-gateway
```

**For development with reproducible locked dependencies:**

**With conda (recommended for development):**
```bash
# Install conda-lock if you don't have it
pip install conda-lock
# or: conda install -c conda-forge conda-lock

# Create environment from lock file
conda-lock install --name cellxgene-gateway conda-lock.yml

# Activate the environment
conda activate cellxgene-gateway
```

**With pip only:**
```bash
# Standard pip (uses pinned requirements.txt)
pip install -r requirements.txt

# uv (faster, uses uv.lock)
uv pip install -r requirements.txt
# or
uv pip sync uv.lock
```

### Updating Dependencies

**With conda-lock (recommended for development):**
```bash
pip install conda-lock

# Update environment.yml with new package versions or add new packages
# Then regenerate lock file for all platforms
conda-lock lock -f environment.yml -p linux-64 -p osx-64 -p osx-arm64

# Update your local environment
conda-lock install --name cellxgene-gateway conda-lock.yml
```

**With pip-tools:**
```bash
pip install pip-tools

# Update all dependencies to latest compatible versions
pip-compile --upgrade requirements.in

# Update a specific package only
pip-compile --upgrade-package anndata requirements.in

# After updating, regenerate uv.lock
uv pip compile requirements.in --output-file uv.lock
```

**With uv (faster):**
```bash
# Update all dependencies
uv pip compile --upgrade requirements.in -o requirements.txt
uv pip compile requirements.in --output-file uv.lock

# Update specific package
uv pip compile --upgrade-package anndata requirements.in -o requirements.txt
uv pip compile requirements.in --output-file uv.lock
```

**Adding new dependencies:**
1. Add the package name to `requirements.in`
2. Run `pip-compile requirements.in` or `uv pip compile requirements.in -o requirements.txt`
3. Regenerate `uv.lock` with `uv pip compile requirements.in --output-file uv.lock`

### Why Lock Files?

This project uses a two-tier dependency approach:

1. **`requirements.in`** (used by setup.py) - Specifies high-level dependencies with flexible version constraints. This allows pip to resolve dependencies when installing the package, avoiding over-constraining for end users.

2. **Lock files** (conda-lock.yml, requirements.txt, uv.lock) - Pin all transitive dependencies to exact versions for reproducible development environments. For example, anndata 0.12.4 is currently locked - newer versions may have breaking changes. This ensures the environment that works today will work tomorrow.

**For contributors:** Always commit lock files (conda-lock.yml, requirements.txt, uv.lock) to git and install from them during development. This ensures everyone tests against the same dependency versions.

**For end users:** The package installation (`pip install cellxgene-gateway`) uses `requirements.in` to allow pip's dependency resolver flexibility.


## Running Tests

[![Build Status](https://travis-ci.org/Novartis/cellxgene-gateway.svg?branch=master)](https://travis-ci.org/Novartis/cellxgene-gateway)

```bash
    python -m unittest discover tests
```

## Code Coverage
```bash
    coverage run -m unittest discover tests
    coverage html
```

## Running Linters

pip install isort flake8 black

```bash
isort -rc . # rc means recursive, and was deprecated in dev version of isort
black .
```

# Getting Help

If you need help for any reason, please make a github ticket. One of the contributors should help you out.

# Releasing New Versions

## How to prepare for release

- Update Changelog.md and version number in __init__.py
- Cut a release on github
	- Go to your project homepage on GitHub
	- On right side, you will see [Releases](https://github.com/Novartis/cellxgene-gateway/releases) link. Click on it.
	- Click on Draft a new release
	- Fill in all the details
		- Tag version should be the version number of your package release
		- Release Title can be anything you want, but we use v0.3.11 (the same as the tag to be created on publish)
		- Description should be changelog
	- Click Publish release at the bottom of the page
	- Now under Releases you can view all of your releases.
	- Copy the download link (tar.gz) and save it somewhere

## How to publish to PyPI

Make sure your `.pypirc` is set up for testpypi and pypi index servers.
 

```bash
rm -rf dist
python setup.py sdist bdist_wheel
python -m twine upload --repository testpypi dist/*
python -m twine upload dist/*
```

# Contributors

* Niket Patel - https://github.com/NiketPatel9
* Alok Saldanha - https://github.com/alokito
* Yohann Potier - https://github.com/ypotier
