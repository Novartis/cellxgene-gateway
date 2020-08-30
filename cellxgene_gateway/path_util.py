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
from cellxgene_gateway.cache_key import CacheKey
from cellxgene_gateway.cellxgene_exception import CellxgeneException
from cellxgene_gateway.dir_util import make_h5ad


def get_key(path):
    if path == "/" or path == "":
        raise CellxgeneException(
            "No matching dataset found.", status.HTTP_404_NOT_FOUND
        )

    trimmed = path[:-1] if path[-1] == "/" else path
    try:
        # valid paths come in three forms:
        if trimmed.endswith(".h5ad") and data_file_exists(trimmed):
            # 1) somedir/dataset.h5ad: a dataset
            return CacheKey(trimmed, trimmed, None)
        elif trimmed.endswith(".csv"):

            # 2) somedir/dataset_annotations/my_annotations.csv : an actual annotations file.
            annotations_dir = os.path.split(trimmed)[0]
            dataset = make_h5ad(annotations_dir)
            if data_file_exists(dataset):
                data_dir_ensure(annotations_dir)
                return CacheKey(trimmed, dataset, trimmed)
        elif trimmed.endswith("_annotations") and data_dir_exists(trimmed):
            # 3) somedir/dataset_annotations: an annotation directory. The corresponding h5ad must exist, but the directory may not.
            dataset = make_h5ad(trimmed)
            if data_file_exists(dataset):
                return CacheKey(trimmed, dataset, "")
    except CellxgeneException:
        pass
    split = os.path.split(trimmed)
    return get_key(split[0])


def validate_exists(file_path):
    if not os.path.exists(file_path):
        raise CellxgeneException(
            "File does not exist: " + file_path, status.HTTP_400_BAD_REQUEST
        )


def validate_is_file(file_path):
    validate_exists(file_path)
    if not os.path.isfile(file_path):
        raise CellxgeneException(
            "Path is not file: " + file_path, status.HTTP_400_BAD_REQUEST
        )
    return


def validate_is_dir(file_path):
    validate_exists(file_path)
    if not os.path.isdir(file_path):
        raise CellxgeneException(
            "Path is not dir: " + file_path, status.HTTP_400_BAD_REQUEST
        )
    return


def data_file_exists(dataset):
    file_path = os.path.join(env.cellxgene_data, dataset)
    validate_is_file(file_path)
    return True


def data_dir_exists(dataset):
    file_path = os.path.join(env.cellxgene_data, dataset)
    validate_is_dir(file_path)
    return True


def data_dir_ensure(dataset):
    file_path = os.path.join(env.cellxgene_data, dataset)
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def get_file_path(key):
    dataset = key.dataset
    file_path = os.path.join(env.cellxgene_data, dataset)
    validate_is_file(file_path)
    return file_path


def get_annotation_file_path(key):
    if key.annotation_file is None:
        return None
    if key.annotation_file == "":
        return ""
    file_path = os.path.join(env.cellxgene_data, key.annotation_file)
    return file_path
