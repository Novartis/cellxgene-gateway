# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

from flask import request, url_for


def querystring():
    qs = request.query_string.decode()
    return f"?{qs}" if len(qs) > 0 else ""


include_source_in_url = False


def url(endpoint, descriptor, source_name):
    if include_source_in_url:
        return url_for(endpoint, source_name=source_name, path=descriptor)
    else:
        return url_for(endpoint, path=descriptor)


def view_url(descriptor, source_name):
    return url("do_view", descriptor, source_name)


def relaunch_url(descriptor, source_name):
    return url("do_relaunch", descriptor, source_name)
