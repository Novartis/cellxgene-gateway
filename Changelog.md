# 0.3.12

* #81 List gene set annotations when cell annotations not present
* #86 Upgrade pip within docker image
* #73 Moved new link to front
* #87 Temporarily pin versions of werkzeug and flask


# 0.3.11

* #81 added support for gene sets
* #79 added example for cellxgene-gateway customized docker image
* #78 prune directories that do not contain h5ad files

# 0.3.10

* #65 Added GATEWAY_EXPIRE_SECONDS to set how long cellxgene servers can remain idle before being terminated.
* Added GATEWAY_LOG_LEVEL to set the log level
* #68 Close connections after reading response
* #68 Background thread reads from output of cellxgene process until it exits

# 0.3.9

* Added S3_ENABLE_LISTINGS_CACHE variable (See README.md)

# 0.3.8

* Fixed bug #57 affecting deeply nested subdirectory listing

# 0.3.7

* added back /metadata/ip_address endpoint

# 0.3.6

* pinned version of werkzeug

# 0.3.5

* Pinned flask version to match cellxgene 0.17.0

# 0.3.4

* Fixed bug #50 affecting subdirectory listing

# 0.3.3

* Fixed bug #48 affecting cache pruning

# 0.3.2

 * Fixed bug #45 affecting multi-level S3 folders
 * Added extra_scripts to cache_status page

# 0.3.1

 * Added missing __init__.py

# 0.3.0

 * Added support for itemsource interface, allowing s3 hosting
 * Removed support for http file uploads
 * Only set wsgi.url_scheme when EXTERNAL_PROTOCOL is set (see issue #43) 
 * Dropped flake8 due to conflicts with black
 * Added code coverage metrics

# 0.2.3

 * Added support for ProxyFix

# 0.2.2

  * Fixed bug with annotations (missing annotation.js asset)

# 0.2.1

  * Minor fixes to enable cellxgene 0.16.0
  * Added CELLXGENE_ARGS to enable passing additional arguments to cellxgene
  * added metadata/ip_address endpoint

# 0.2.0

Incrementing minor version since the changes for 0.15 are breaking, and we may want to release bugfixes from 0.1.0 branch.

# 0.1.1

Added support for cellxgene 0.15
