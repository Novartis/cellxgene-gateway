# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import json
import logging

# import BaseHTTPServer
import os
from threading import Lock, Thread

from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_api import status
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from cellxgene_gateway import env
from cellxgene_gateway.backend_cache import BackendCache
from cellxgene_gateway.cache_entry import CacheEntryStatus
from cellxgene_gateway.cellxgene_exception import CellxgeneException
from cellxgene_gateway.dir_util import create_dir, is_subdir
from cellxgene_gateway.extra_scripts import get_extra_scripts
from cellxgene_gateway.filecrawl import recurse_dir, render_entries
from cellxgene_gateway.path_util import get_key
from cellxgene_gateway.process_exception import ProcessException
from cellxgene_gateway.prune_process_cache import PruneProcessCache
from cellxgene_gateway.util import current_time_stamp

app = Flask(__name__)


def _force_https(app):
    def wrapper(environ, start_response):
        environ["wsgi.url_scheme"] = env.external_protocol
        return app(environ, start_response)

    return wrapper


app.wsgi_app = _force_https(app.wsgi_app)
if (
    env.proxy_fix_for > 0
    or env.proxy_fix_proto > 0
    or env.proxy_fix_host > 0
    or env.proxy_fix_port > 0
    or env.proxy_fix_prefix > 0
):
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=env.proxy_fix_for,
        x_proto=env.proxy_fix_proto,
        x_host=env.proxy_fix_host,
        x_port=env.proxy_fix_port,
        x_prefix=env.proxy_fix_prefix,
    )

cache = BackendCache()


@app.errorhandler(CellxgeneException)
def handle_invalid_usage(error):

    message = f"{error.http_status} Error : {error.message}"

    return (
        render_template(
            "cellxgene_error.html",
            extra_scripts=get_extra_scripts(),
            message=message,
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
            "process_error.html",
            extra_scripts=get_extra_scripts(),
            message=error.message,
            http_status=error.http_status,
            stdout=error.stdout,
            stderr=error.stderr,
            dataset=error.key.dataset,
            annotation_file=error.key.annotation_file,
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
        enable_upload=env.enable_upload,
    )


def make_user():
    dir_name = request.form["directory"]

    create_dir(env.cellxgene_data, dir_name)

    return redirect(url_for("index"), code=302)


def make_subdir():
    parent_path = os.path.join(env.cellxgene_data, request.form["usernames"])
    dir_name = request.form["directory"]

    create_dir(parent_path, dir_name)

    return redirect(url_for("index"), code=302)


def upload_file():
    upload_dir = request.form["path"]

    full_upload_path = os.path.join(env.cellxgene_data, upload_dir)
    if is_subdir(full_upload_path, env.cellxgene_data) and os.path.isdir(
        full_upload_path
    ):
        if request.method == "POST":
            if "file" in request.files:
                f = request.files["file"]
                if f and f.filename.endswith(".h5ad"):
                    f.save(
                        os.path.join(
                            full_upload_path, secure_filename(f.filename)
                        )
                    )
                    return redirect(url_for("filecrawl"), code=302)
                else:
                    raise CellxgeneException(
                        "Uploaded file must be in anndata (.h5ad) format.",
                        status.HTTP_400_BAD_REQUEST,
                    )
            else:
                raise CellxgeneException(
                    "A file must be chosen to upload.",
                    status.HTTP_400_BAD_REQUEST,
                )
    else:
        raise CellxgeneException(
            "Invalid directory.", status.HTTP_400_BAD_REQUEST
        )

    return redirect(url_for("index"), code=302)


if env.enable_upload:
    app.add_url_rule("/make_user", "make_user", make_user, methods=["POST"])
    app.add_url_rule(
        "/make_subdir", "make_subdir", make_subdir, methods=["POST"]
    )
    app.add_url_rule(
        "/upload_file", "upload_file", upload_file, methods=["POST"]
    )


def set_no_cache(resp):
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers["Cache-Control"] = "public, max-age=0"
    return resp


@app.route("/filecrawl.html")
def filecrawl():
    entries = recurse_dir(env.cellxgene_data)
    rendered_html = render_entries(entries)
    resp = make_response(
        render_template(
            "filecrawl.html",
            extra_scripts=get_extra_scripts(),
            rendered_html=rendered_html,
        )
    )
    return set_no_cache(resp)


@app.route("/filecrawl/<path:path>")
def do_filecrawl(path):
    filecrawl_path = os.path.join(env.cellxgene_data, path)
    if not os.path.isdir(filecrawl_path):
        raise CellxgeneException(
            "Path is not directory: " + filecrawl_path,
            status.HTTP_400_BAD_REQUEST,
        )
    entries = recurse_dir(filecrawl_path)
    rendered_html = render_entries(entries)
    return render_template(
        "filecrawl.html",
        extra_scripts=get_extra_scripts(),
        rendered_html=rendered_html,
        path=path,
    )


entry_lock = Lock()


@app.route("/view/<path:path>", methods=["GET", "PUT", "POST"])
def do_view(path):
    key = get_key(path)
    print(
        f"view path={path}, dataset={key.dataset}, annotation_file= {key.annotation_file}, key={key.pathpart}"
    )
    with entry_lock:
        match = cache.check_entry(key)
        if match is None:
            uascripts = get_extra_scripts()
            match = cache.create_entry(key, uascripts)

    match.timestamp = current_time_stamp()

    if (
        match.status == CacheEntryStatus.loaded
        or match.status == CacheEntryStatus.loading
    ):
        return match.serve_content(path)
    elif match.status == CacheEntryStatus.error:
        raise ProcessException.from_cache_entry(match)


@app.route("/cache_status", methods=["GET"])
def do_GET_status():
    return render_template("cache_status.html", entry_list=cache.entry_list)


@app.route("/cache_status.json", methods=["GET"])
def do_GET_status_json():
    return json.dumps(
        {
            "launchtime": app.launchtime,
            "entry_list": [
                {
                    "dataset": entry.key.dataset,
                    "annotation_file": entry.key.annotation_file,
                    "launchtime": entry.launchtime,
                    "last_access": entry.timestamp,
                    "status": entry.status,
                }
                for entry in cache.entry_list
            ],
        }
    )


@app.route("/relaunch/<path:path>", methods=["GET"])
def do_relaunch(path):
    key = get_key(path)
    match = cache.check_entry(key)
    if not match is None:
        match.terminate()
    qs = request.query_string.decode()
    return redirect(
        url_for("do_view", path=path) + (f"?{qs}" if len(qs) > 0 else ""),
        code=302,
    )


@app.route("/terminate/<path:path>", methods=["GET"])
def do_terminate(path):
    key = get_key(path)
    match = cache.check_entry(key)
    if not match is None:
        match.terminate()
    return redirect(url_for("do_GET_status"), code=302)


@app.route("/metadata/ip_address", methods=["GET"])
def ip_address():
    resp = make_response(env.ip)
    return set_no_cache(resp)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:%(name)s:%(levelname)s:%(message)s",
    )
    env.validate()
    pruner = PruneProcessCache(cache)

    background_thread = Thread(target=pruner)
    background_thread.start()

    app.launchtime = current_time_stamp()
    app.run(host="0.0.0.0", port=env.gateway_port, debug=False)


if __name__ == "__main__":
    main()
