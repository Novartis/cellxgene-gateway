import logging
import os

import typer
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from cellxgene_gateway import env, flask_util, gateway_blueprint
from cellxgene_gateway.util import current_time_stamp

app = Flask(__name__)


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


def main(prometheus: bool = False):
    logging.basicConfig(
        level=env.log_level,
        format="%(asctime)s:%(name)s:%(levelname)s:%(message)s",
    )
    cellxgene_data = os.environ.get("CELLXGENE_DATA", None)
    cellxgene_bucket = os.environ.get("CELLXGENE_BUCKET", None)

    if cellxgene_bucket is not None:
        from cellxgene_gateway.items.s3.s3item_source import S3ItemSource

        gateway_blueprint.item_sources.append(S3ItemSource(cellxgene_bucket, name="s3"))
        default_item_source = "s3"
    if cellxgene_data is not None:
        from cellxgene_gateway.items.file.fileitem_source import FileItemSource

        gateway_blueprint.item_sources.append(
            FileItemSource(cellxgene_data, name="local")
        )
        default_item_source = "local"
    if len(gateway_blueprint.item_sources) == 0:
        raise Exception("Please specify CELLXGENE_DATA or CELLXGENE_BUCKET")
    flask_util.include_source_in_url = len(gateway_blueprint.item_sources) > 1

    if prometheus:
        from cellxgene_gateway.prometheus import add_metrics

        add_metrics(app)
    app.register_blueprint(gateway_blueprint.gateway_blueprint)
    gateway_blueprint.launch()

    app.launchtime = current_time_stamp()
    app.run(host="0.0.0.0", port=env.gateway_port, debug=False)


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
