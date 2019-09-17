# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
from flask import make_response, request
from requests import get, post, put

from cellxgene_gateway import env
from cellxgene_gateway.cellxgene_exception import CellxgeneException
from cellxgene_gateway.util import current_time_stamp


class CacheEntry:
    def __init__(
        self,
        pid,
        dataset,
        file_path,
        port,
        launchtime,
        timestamp,
        status,
        message,
        all_output,
        stderr,
        http_status,
    ):
        self.pid = pid
        self.dataset = dataset
        self.file_path = file_path
        self.port = port
        self.launchtime = launchtime
        self.timestamp = timestamp
        self.status = status
        self.message = message
        self.all_output = all_output
        self.stderr = stderr
        self.http_status = http_status

    @classmethod
    def for_dataset(cls, dataset, file_path, port):
        return cls(
            None,
            dataset,
            file_path,
            port,
            current_time_stamp(),
            current_time_stamp(),
            "loading",
            None,
            None,
            None,
            None,
        )

    def set_loaded(self, pid):
        self.pid = pid
        self.status = "loaded"

    def set_error(self, message, stderr, http_status):
        self.message = message
        self.stderr = stderr
        self.http_status = http_status
        self.status = "error"
    
    def append_output(self, output):
        if self.all_output == None:
            self.all_output = output
        else:
            self.all_output += output

    def terminate(self, process):
        if pid != None and self.status != "terminated":
            p = psutil.Process(pid)
            p.terminate()
            p = psutil.Process(pid + 2)
            p.terminate()
        self.status = "terminated"


    def serve_content(self, path):
        dataset = self.dataset

        gateway_basepath = (
            f"{env.gateway_protocol}://{env.gateway_host}/view/{dataset}/"
        )
        subpath = path[len(dataset) :]  # noqa: E203

        if len(subpath) == 0:
            r = make_response(f"Redirect to {gateway_basepath}\n", 301)
            r.headers["location"] = gateway_basepath
            return r

        port = self.port
        cellxgene_basepath = f"http://127.0.0.1:{port}"

        headers = {}

        if "accept" in request.headers:
            headers["accept"] = request.headers["accept"]
        if "user-agent" in request.headers:
            headers["user-agent"] = request.headers["user-agent"]
        if "content-type" in request.headers:
            headers["content-type"] = request.headers["content-type"]

        if request.method in ["GET", "HEAD", "OPTIONS"]:
            cellxgene_response = get(
                cellxgene_basepath + subpath, headers=headers
            )
        elif request.method == "PUT":
            cellxgene_response = put(
                cellxgene_basepath + subpath,
                headers=headers,
                data=request.data.decode(),
            )
        elif request.method == "POST":
            cellxgene_response = post(
                cellxgene_basepath + subpath,
                headers=headers,
                data=request.data.decode(),
            )
        else:
            raise CellxgeneException(
                f"Unexpected method {request.method}", 400
            )
        content_type = cellxgene_response.headers["content-type"]
        if "text" in content_type:
            cellxgene_content = cellxgene_response.content.decode()
            gateway_content = cellxgene_content.replace(
                "http://fonts.gstatic.com", "https://fonts.gstatic.com"
            ).replace(cellxgene_basepath, gateway_basepath)
        else:
            gateway_content = cellxgene_response.content

        gateway_response = make_response(
            gateway_content,
            cellxgene_response.status_code,
            {"Content-Type": content_type},
        )

        return gateway_response
