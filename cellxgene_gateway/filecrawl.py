# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import os
import urllib.parse

from cellxgene_gateway import env, flask_util
from cellxgene_gateway.cache_key import CacheKey
from cellxgene_gateway.dir_util import annotations_suffix, make_annotations, make_h5ad


def render_annotations(item, item_source):
    url = flask_util.view_url(
        item_source.get_annotations_subpath(item), item_source.name
    )
    new_annotation = f"<a class='new' href='{url}'>new</a>"
    annotations = (
        ", ".join(
            [
                f"<a href='{CacheKey(item, item_source, a).view_url}/'>{a.name}</a>"
                for a in item.annotations
            ]
        )
        + ", "
        if item.annotations
        else ""
    )
    return " | annotations: " + annotations + new_annotation


def render_item(item, item_source):
    item_string = f"<li> <a href='{ CacheKey(item, item_source).view_url }/'>{item.name}</a> {render_annotations(item, item_source)}</li>"
    return item_string


def render_item_tree(item_tree, item_source):
    items = (
        "\n".join([render_item(i, item_source) for i in item_tree.items])
        if item_tree.items
        else ""
    )
    branches = (
        "\n".join([render_item_tree(b, item_source) for b in item_tree.branches])
        if item_tree.branches
        else ""
    )
    html = "<ul>" + items + branches + "</ul>"
    if item_tree.descriptor:
        descriptor = item_tree.descriptor.lstrip("/")
        url = f"/filecrawl/{descriptor}?source={item_source.name}"
        name = descriptor.rsplit("/")[1] if descriptor.find("/") >= 0 else descriptor
        return f"<li><a href='{url}'>{name}</a>{html}</li>"
    else:
        return html


def render_item_source(item_source, filter=None):
    item_tree = item_source.list_items(filter)
    filterpart = "" if filter is None else ":" + filter
    heading = f"<h6><a href='/filecrawl.html?source={urllib.parse.quote_plus(item_source.name)}'>{item_source.name}</a>{filterpart}</h6>"
    return heading + render_item_tree(item_tree, item_source)
