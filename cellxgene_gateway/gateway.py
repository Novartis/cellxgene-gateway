# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
# import BaseHTTPServer
import json
import logging
import os
import urllib.parse
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
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

from cellxgene_gateway import env, flask_util
from cellxgene_gateway.backend_cache import BackendCache
from cellxgene_gateway.cache_entry import CacheEntryStatus
from cellxgene_gateway.cache_key import CacheKey
from cellxgene_gateway.cellxgene_exception import CellxgeneException
from cellxgene_gateway.extra_scripts import get_extra_scripts
from cellxgene_gateway.filecrawl import render_item_source
from cellxgene_gateway.process_exception import ProcessException
from cellxgene_gateway.prune_process_cache import PruneProcessCache
from cellxgene_gateway.util import current_time_stamp

app = Flask(__name__)

item_sources = []
default_item_source = None


def _force_https(app):
    def wrapper(environ, start_response):
        if env.external_protocol is not None:
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
            relaunch_url=error.key.relaunch_url(),
            annotation_file=error.key.annotation_descriptor,
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
    return render_template(
        "index.html",
        ip=env.ip,
        cellxgene_data=env.cellxgene_data,
        extra_scripts=get_extra_scripts(),
    )


@app.route("/filecrawl.html")
@app.route("/filecrawl/<path:path>")
def filecrawl(path=None):
    source_name = request.args.get("source")
    sources = (
        filter(
            lambda x: x.name == urllib.parse.unquote_plus(source_name),
            item_sources,
        )
        if source_name
        else item_sources
    )
    # loop all data sources --
    rendered_sources = [
        render_item_source(item_source, path) for item_source in sources
    ]  # will we need to make this async in the page???
    rendered_html = "\n".join(rendered_sources)

    resp = make_response(
        render_template(
            "filecrawl.html",
            extra_scripts=get_extra_scripts(),
            rendered_html=rendered_html,
            path=path,
        )
    )
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers["Cache-Control"] = "public, max-age=0"
    return resp


entry_lock = Lock()


def matching_source(source_name):
    if source_name is None:
        source_name = default_item_source.name
    matching = [i for i in item_sources if i.name == source_name]
    if len(matching) != 1:
        raise Exception(f"Could not find matching item source {source_name}")
    source = matching[0]
    return source


@app.route(
    "/source/<path:source_name>/view/<path:path>",
    methods=["GET", "PUT", "POST"],
)
@app.route("/view/<path:path>", methods=["GET", "PUT", "POST"])
def do_view(path, source_name=None):
    source = matching_source(source_name)
    match = cache.check_path(source, path)

    if match is None:
        lookup = source.lookup(path)
        if lookup is None:
            raise CellxgeneException(
                f"Could not find item for path {path} in source {source.name}",
                404,
            )
        key = CacheKey.for_lookup(source, lookup)
        print(
            f"view path={path}, source_name={source_name}, dataset={key.file_path}, annotation_file= {key.annotation_file_path}, key={key.descriptor}, source={key.source_name}"
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
    return render_template(
        "cache_status.html",
        entry_list=cache.entry_list,
        extra_scripts=get_extra_scripts(),
    )


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
    source_name = request.args.get("source_name") or default_item_source.name
    source = matching_source(source_name)
    key = CacheKey.for_lookup(source, source.lookup(path))
    match = cache.check_entry(key)
    if not match is None:
        match.terminate()
    return redirect(
        key.view_url,
        code=302,
    )


@app.route("/terminate/<path:path>", methods=["GET"])
def do_terminate(path):
    source_name = request.args.get("source_name") or default_item_source.name
    source = matching_source(source_name)
    key = CacheKey.for_lookup(source, source.lookup(path))
    match = cache.check_entry(key)
    if not match is None:
        match.terminate()
    return redirect(url_for("do_GET_status"), code=302)


def launch():
    env.validate()
    if not item_sources or not len(item_sources):
        raise Exception("No data sources specified for Cellxgene Gateway")

    global default_item_source
    if default_item_source is None:
        default_item_source = item_sources[0]

    pruner = PruneProcessCache(cache)

    background_thread = Thread(target=pruner)
    background_thread.start()

    app.launchtime = current_time_stamp()
    app.run(host="0.0.0.0", port=env.gateway_port, debug=False)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:%(name)s:%(levelname)s:%(message)s",
    )
    cellxgene_data = os.environ.get("CELLXGENE_DATA", None)
    cellxgene_bucket = os.environ.get("CELLXGENE_BUCKET", None)

    if cellxgene_bucket is not None:
        from cellxgene_gateway.items.s3.s3item_source import S3ItemSource

        item_sources.append(S3ItemSource(cellxgene_bucket, name="s3"))
        default_item_source = "s3"
    if cellxgene_data is not None:
        from cellxgene_gateway.items.file.fileitem_source import FileItemSource

        item_sources.append(FileItemSource(cellxgene_data, name="local"))
        default_item_source = "local"
    if len(item_sources) == 0:
        raise Exception("Please specify CELLXGENE_DATA or CELLXGENE_BUCKET")
    flask_util.include_source_in_url = len(item_sources) > 1

    launch()


if __name__ == "__main__":
    main()
