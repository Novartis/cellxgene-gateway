# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
import datetime
import logging
import re
import urllib.parse
from enum import Enum

import psutil
from flask import make_response, render_template, request
from flask.wrappers import Response
from requests import get, post, put

from cellxgene_gateway import env
from cellxgene_gateway.cellxgene_exception import CellxgeneException
from cellxgene_gateway.flask_util import querystring
from cellxgene_gateway.util import current_time_stamp


class CacheEntryStatus(Enum):
    loaded = "loaded"
    loading = "loading"
    error = "error"
    terminated = "terminated"


class CacheEntry:
    def __init__(
        self,
        pid,
        key,
        port,
        launchtime,
        timestamp,
        status: CacheEntryStatus,
        message,
        all_output,
        stderr,
        http_status,
    ):
        self.pid = pid
        self.key = key
        self.port = port
        self.launchtime = launchtime
        self.timestamp = timestamp
        self.status = status
        self.message = message
        self.all_output = all_output
        self.stderr = stderr
        self.http_status = http_status

    @classmethod
    def for_key(cls, key, port):

        return cls(
            None,
            key,
            port,
            current_time_stamp(),
            current_time_stamp(),
            CacheEntryStatus.loading,
            None,
            None,
            None,
            None,
        )

    @property
    def source_name(self):
        return self.key.source_name

    def set_loaded(self, pid):
        self.pid = pid
        self.status = CacheEntryStatus.loaded

    def set_error(self, message, stderr, http_status):
        self.message = message
        self.stderr = stderr
        self.http_status = http_status
        self.status = CacheEntryStatus.error

    def append_output(self, output):
        if self.all_output == None:
            self.all_output = output
        else:
            self.all_output += output

    def terminate(self):
        pid = self.pid
        if pid != None and self.status != CacheEntryStatus.terminated:
            terminated = []

            def on_terminate(p):
                terminated.append(p.pid)

            p = psutil.Process(pid)
            children = p.children()
            for child in children:
                child.terminate()
            psutil.wait_procs(children, callback=on_terminate)
            # the parent process may automatically die once its children have --
            try:
                p.terminate()
                psutil.wait_procs([p], callback=on_terminate)
            except psutil.NoSuchProcess:
                pass

            logging.getLogger("cellxgene_gateway").info(f"terminated {terminated}")
        self.status = CacheEntryStatus.terminated

    def rewrite_text_content(self, cellxgene_content):
        # for v0.16.0 compatibility, see issue #24
        gateway_content = (
            re.sub(
                '(="|\()/static/',
                f"\\1{self.key.gateway_basepath()}static/",
                cellxgene_content,
            )
            .replace("http://fonts.gstatic.com", "https://fonts.gstatic.com")
            .replace(self.cellxgene_basepath(), self.key.gateway_basepath())
        )
        return gateway_content

    def cellxgene_basepath(self):
        return f"http://127.0.0.1:{self.port}"

    def serve_content(self, path):
        gateway_basepath = self.key.gateway_basepath()
        subpath = path[len(self.key.descriptor) :]  # noqa: E203
        if len(subpath) == 0:
            r = make_response(f"Redirect to {gateway_basepath}\n", 302)
            r.headers["location"] = gateway_basepath + querystring()
            return r
        elif self.status == CacheEntryStatus.loading:
            launch_time = datetime.datetime.fromtimestamp(self.launchtime)
            return render_template(
                "loading.html",
                launchtime=launch_time,
                all_output=self.all_output,
            )

        headers = {}
        copy_headers = [
            "accept",
            "accept-encoding",
            "accept-language",
            "cache-control",
            "connection",
            "content-length",
            "content-type",
            "cookie",
            "host",
            "origin",
            "pragma",
            "referer",
            "sec-fetch-mode",
            "sec-fetch-site",
            "user-agent",
        ]
        for h in copy_headers:
            if h in request.headers:
                headers[h] = request.headers[h]

        full_path = self.cellxgene_basepath() + subpath + querystring()

        if request.method in ["GET", "HEAD", "OPTIONS"]:
            cellxgene_response = get(full_path, headers=headers)
        elif request.method == "PUT":
            cellxgene_response = put(
                full_path,
                headers=headers,
                data=request.data,
            )
        elif request.method == "POST":
            cellxgene_response = post(
                full_path,
                headers=headers,
                data=request.data,
            )
        else:
            raise CellxgeneException(f"Unexpected method {request.method}", 400)
        content_type = cellxgene_response.headers["content-type"]
        if "text" in content_type:
            gateway_content = self.rewrite_text_content(
                cellxgene_response.content.decode()
            )
        else:
            gateway_content = cellxgene_response.content

        resp_headers = {}
        for h in copy_headers:
            if h in cellxgene_response.headers:
                resp_headers[h] = cellxgene_response.headers[h]

        gateway_response = make_response(
            gateway_content,
            cellxgene_response.status_code,
            resp_headers,
        )
        return gateway_response
