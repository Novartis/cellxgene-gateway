# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

# import BaseHTTPServer
import datetime
import os
from threading import Thread

from flask import Flask, redirect, render_template, request, send_from_directory
from flask_api import status
from werkzeug import secure_filename

import env
from backend_cache import BackendCache
from cellxgene_exception import CellxgeneException
from dir_util import create_dir, recurse_dir, render_entries
from extra_scripts import get_extra_scripts
from path_util import get_dataset, get_file_path
from process_exception import ProcessException
from prune_process_cache import PruneProcessCache
from util import current_time_stamp

app = Flask(__name__)
cache = BackendCache()
location = f"{env.gateway_protocol}://{env.gateway_host}"


@app.errorhandler(CellxgeneException)
def handle_invalid_usage(error):

    message = f"{error.http_status} Error : {error.message}"

    return (
        render_template(
            "cellxgene_error.html", extra_scripts=get_extra_scripts(), message=message
        ),
        error.http_status,
    )


@app.errorhandler(ProcessException)
def handle_invalid_process(error):

    message = []

    message.append(error.message)
    message.append(f"{error.http_status} Error.")
    message.append(f"Stdout: {error.stdout}")
    message.append(f"Stderr: {error.stderr}")

    return (
        render_template(
            "process_error.html", extra_scripts=get_extra_scripts(), message=message
        ),
        error.http_status,
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "nibr.ico",
        mimetype="image/vnd.microsof.icon",
    )


@app.route("/")
def index():
    users = [
        name
        for name in os.listdir(env.cellxgene_data)
        if os.path.isdir(os.path.join(env.cellxgene_data, name))
    ]
    return render_template(
        "index.html",
        ip=env.ip,
        cellxgene_data=env.cellxgene_data,
        extra_scripts=get_extra_scripts(),
        users=users,
    )


@app.route("/make_user", methods=["POST"])
def make_user():
    dir_name = request.form["directory"]

    create_dir(env.cellxgene_data, dir_name)

    return redirect(location, code=302)


@app.route("/make_subdir", methods=["POST"])
def make_subdir():
    parent_path = os.path.join(env.cellxgene_data, request.form["usernames"])
    dir_name = request.form["directory"]

    create_dir(parent_path, dir_name)

    return redirect(location, code=302)


@app.route("/upload_file", methods=["POST"])
def upload_file():
    upload_dir = request.form["path"]

    full_upload_path = env.cellxgene_data + "/" + upload_dir
    if os.path.isdir(full_upload_path):
        if request.method == "POST":
            if "file" in request.files:
                f = request.files["file"]
                if f and f.filename.endswith(".h5ad"):
                    f.save(full_upload_path + "/" + secure_filename(f.filename))
                    return redirect("/filecrawl.html", code=302)
                else:
                    raise CellxgeneException(
                        "Uploaded file must be in anndata (.h5ad) format.",
                        status.HTTP_400_BAD_REQUEST,
                    )
            else:
                raise CellxgeneException(
                    "A file must be chosen to upload.", status.HTTP_400_BAD_REQUEST
                )
    else:
        raise CellxgeneException("Invalid directory.", status.HTTP_400_BAD_REQUEST)

    return redirect(env.location, code=302)


@app.route("/filecrawl.html")
def filecrawl():

    entries = recurse_dir(env.cellxgene_data)
    rendered_html = render_entries(entries)
    return render_template(
        "filecrawl.html", extra_scripts=get_extra_scripts(), rendered_html=rendered_html
    )


@app.route("/view/<path:path>", methods=["GET", "PUT", "POST"])
def do_GET(path):

    dataset = get_dataset(path)
    file_path = get_file_path(dataset)
    match = cache.check_entry(dataset)
    if match is None:
        uascripts = get_extra_scripts()
        match = cache.create_entry(dataset, file_path, uascripts)

    match.timestamp = current_time_stamp()

    if match.status == "loaded":
        return match.serve_content(path)
    elif match.status == "loading":
        launch_time = datetime.datetime.fromtimestamp(match.launchtime)
        return render_template(
            "loading.html", launchtime=launch_time, all_output=match.all_output
        )
    elif match.status == "error":
        raise ProcessException.from_pid_object(match)


if __name__ == "__main__":
    background_thread = Thread(target=PruneProcessCache(cache))
    background_thread.start()

    app.run(host="0.0.0.0", port=5005, debug=False)
