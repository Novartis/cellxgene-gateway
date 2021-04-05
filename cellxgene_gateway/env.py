# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import logging
import os
import socket

cellxgene_location = os.environ.get("CELLXGENE_LOCATION")
cellxgene_data = os.environ.get("CELLXGENE_DATA", "")
cellxgene_args = os.environ.get("CELLXGENE_ARGS", None)
gateway_port = int(os.environ.get("GATEWAY_PORT", "5005"))
external_host = os.environ.get(
    "EXTERNAL_HOST",
    os.environ.get("GATEWAY_HOST", f"localhost:{gateway_port}"),
)
external_protocol = os.environ.get(
    "EXTERNAL_PROTOCOL", os.environ.get("GATEWAY_PROTOCOL", None)
)
ip = os.environ.get("GATEWAY_IP")
extra_scripts = os.environ.get("GATEWAY_EXTRA_SCRIPTS")
ttl = os.environ.get("GATEWAY_TTL")
enable_annotations = os.environ.get("GATEWAY_ENABLE_ANNOTATIONS", "").lower() in [
    "true",
    "1",
]
enable_backed_mode = os.environ.get("GATEWAY_ENABLE_BACKED_MODE", "").lower() in [
    "true",
    "1",
]

env_vars = {
    "CELLXGENE_LOCATION": cellxgene_location,
}

proxy_fix_for = int(os.environ.get("PROXY_FIX_FOR", "0"))
proxy_fix_proto = int(os.environ.get("PROXY_FIX_PROTO", "0"))
proxy_fix_host = int(os.environ.get("PROXY_FIX_HOST", "0"))
proxy_fix_port = int(os.environ.get("PROXY_FIX_PORT", "0"))
proxy_fix_prefix = int(os.environ.get("PROXY_FIX_PREFIX", "0"))

optional_env_vars = {
    "EXTERNAL_HOST": external_host,
    "EXTERNAL_PROTOCOL": external_protocol,
    "GATEWAY_IP": ip,
    "GATEWAY_PORT": gateway_port,
    "GATEWAY_EXTRA_SCRIPTS": extra_scripts,
    "GATEWAY_TTL": ttl,
    "GATEWAY_ENABLE_ANNOTATIONS": enable_annotations,
    "GATEWAY_ENABLE_BACKED_MODE": enable_backed_mode,
    "CELLXGENE_ARGS": cellxgene_args,
    "CELLXGENE_DATA": cellxgene_data,
    "PROXY_FIX_FOR": proxy_fix_for,
    "PROXY_FIX_PROTO": proxy_fix_proto,
    "PROXY_FIX_HOST": proxy_fix_host,
    "PROXY_FIX_PORT": proxy_fix_port,
    "PROXY_FIX_PREFIX": proxy_fix_prefix,
}


def validate():
    if not all(env_vars.values()):
        raise ValueError(
            f"""
    Please ensure that environment variables are set correctly.
    The ones with None below are missing and need to be set.

    {env_vars}

    Set them at the terminal before running the gateway.
    An example is:

        export CELLXGENE_LOCATION=~/anaconda/envs/cellxgene-dev/bin/cellxgene
        export CELLXGENE_DATA=../cellxgene_data
    """
        )
    else:
        logging.getLogger("cellxgene_gateway").info(
            f"Got required env: {env_vars}",
        )
        logging.getLogger("cellxgene_gateway").info(
            f"Got optional env: {optional_env_vars}"
        )
