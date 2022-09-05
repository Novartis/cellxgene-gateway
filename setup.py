import codecs
import os
import sys

from setuptools import find_packages, setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    # mandatory
    version=get_version("cellxgene_gateway/__init__.py"),
    # mandatory
    long_description=long_description,
    name="cellxgene-gateway",
    packages=find_packages(),
    package_data={
        "cellxgene_gateway": [
            "static/css/homepagestyle.css",
            "static/js/annotation.js",
            "static/nibr.ico",
            "templates/*.html",
        ]
    },
    data_files=[("", ["README.md", "LICENSE"])],
)
