# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import os

cellxgene_location = os.environ.get("CELLXGENE_LOCATION")
cellxgene_data = os.environ.get("CELLXGENE_DATA")
gateway_host = os.environ.get("GATEWAY_HOST")
gateway_protocol = os.environ.get("GATEWAY_PROTOCOL")
ip = os.environ.get("GATEWAY_IP")
extra_scripts = os.environ.get("GATEWAY_EXTRA_SCRIPTS")

env_vars = {
    "CELLXGENE_LOCATION": cellxgene_location,
    "CELLXGENE_DATA": cellxgene_data,
    "GATEWAY_HOST": gateway_host,
    "GATEWAY_PROTOCOL": gateway_protocol,
    "GATEWAY_IP": ip,
}

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
    export GATEWAY_HOST=localhost:5005
    export GATEWAY_PROTOCOL=http
    export GATEWAY_IP=127.0.0.1
"""
    )
