# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

from json import loads
from json.decoder import JSONDecodeError

from cellxgene_gateway import env


def get_extra_scripts():
    # can be array of script tags to inject on every page, e.g. for google analytics could be
    # ['https://www.googletagmanager.com/gtag/js?id=UA-123456-2',
    #  f"{env.external_protocol}://{env.external_host}/static/js/google_ua.js"]
    # where google_ua.js is a script you add to the static/js folder prior to deployment.
    try:
        return [] if env.extra_scripts is None else loads(env.extra_scripts)
    except JSONDecodeError as exc:
        raise Exception(
            f'Error parsing GATEWAY_EXTRA_SCRIPTS, expected JSON array e.g. ["https://example.com/path/to/script.js"]'
        ) from exc
