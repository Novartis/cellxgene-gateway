import os
from setuptools import setup

def parse_requirements():
    reqs = []
    with open("requirements.txt", "r") as f:
        for l in f.readlines():
            reqs.append(l.strip("\n"))
    return reqs

with open("README.md", "r") as fh:
    long_description = fh.read()

install_reqs = parse_requirements()

setup(
    # mandatory
    name="cellxgene-gateway",
    # mandatory
    version="0.1.0",
    # mandatory
    author="Niket Patel, Yohann Potier, Alok Saldanha",
    author_email="alok.saldanha@novartis.com",
    description=("Cellxgene Gateway"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="visualization, genomics",
    url="http://github.com/Novartis/cellxgene-gateway",
    packages=["cellxgene_gateway"],
    package_data={
        "cellxgene_gateway": [
            "static/css/homepagestyle.css",
            "static/nibr.ico",
            "templates/*.html"
    ]},
    data_files=[('', ['README.md', 'LICENSE'])],
    install_requires=install_reqs,
    entry_points={
        "console_scripts": ["cellxgene-gateway=cellxgene_gateway.gateway:main"]
    },
    classifiers=["Topic :: Scientific/Engineering :: Visualization"],
    python_requires='>=3.6',
)
