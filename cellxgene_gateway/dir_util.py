# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import os

from flask_api import status

from cellxgene_gateway import env
from cellxgene_gateway.cellxgene_exception import CellxgeneException


def is_subdir(full_path, parent_path):
    subdir = os.path.realpath(full_path)
    parent = os.path.realpath(parent_path)
    return subdir.startswith(parent)


def create_dir(parent_path, dir_name):
    full_path = os.path.join(parent_path, dir_name)

    if "/" in dir_name:
        raise CellxgeneException(
            "Please have no slashes in the intended directory.",
            status.HTTP_400_BAD_REQUEST,
        )
    elif not os.path.exists(parent_path):
        raise CellxgeneException(
            "The selected User directory does not exist.",
            status.HTTP_400_BAD_REQUEST,
        )
    elif os.path.exists(full_path):
        raise CellxgeneException(
            "The provided subdirectory already exists within Directory.",
            status.HTTP_400_BAD_REQUEST,
        )
    elif not is_subdir(full_path, parent_path):
        raise CellxgeneException(
            "The directory must be a subdirectory of the parent path.",
            status.HTTP_400_BAD_REQUEST,
        )
    elif not os.path.isdir(parent_path):
        raise CellxgeneException(
            "The parent is not a directory.", status.HTTP_400_BAD_REQUEST
        )
    else:
        os.mkdir(full_path)


annotations_suffix = "_annotations"
h5ad_suffix = ".h5ad"


def make_h5ad(el):
    return el[: -len(annotations_suffix)] + h5ad_suffix


def make_annotations(el):
    return el[:-5] + annotations_suffix


def ensure_dir_exists(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
