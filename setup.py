import os
from setuptools import setup


def parse_requirements():
    reqs = []
    with open("requirements.txt", "r") as f:
        for l in f.readlines():
            reqs.append(l.strip("\n"))
    return reqs


install_reqs = parse_requirements()

setup(
    # mandatory
    name="cellxgene-gateway",
    # mandatory
    version="0.1",
    # mandatory
    author="Niket Patel, Yohann Potier, Alok Saldanha",
    author_email="alok.saldanha@novartis.com",
    description=("Cellxgene Gateway"),
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
    data_files=[('', ['README.md', 'LICENSE.txt']))
    install_requires=install_reqs,
    entry_points={
        "console_scripts": ["cellxgene-gateway=cellxgene_gateway.gateway:main"]
    },
    classifiers=["Topic :: Scientific/Engineering :: Visualization"],
)
