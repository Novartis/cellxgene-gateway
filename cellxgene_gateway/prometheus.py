from prometheus_flask_exporter import PrometheusMetrics

from cellxgene_gateway import __version__


def add_metrics(app):
    metrics = PrometheusMetrics(app)
    metrics.info("app_info", "Application info", version=__version__)
    return metrics
