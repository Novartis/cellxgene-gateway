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


def get_dataset(path):
    if path == "/" or path == "":
        raise CellxgeneException(
            "No matching dataset found.", status.HTTP_404_NOT_FOUND
        )

    trimmed = path[:-1] if path[-1] == "/" else path

    try:
        get_file_path(trimmed)
        return trimmed
    except CellxgeneException:
        split = os.path.split(trimmed)
        return get_dataset(split[0])


def validate_path(file_path):
    if not os.path.exists(file_path):
        raise CellxgeneException(
            "File does not exist: " + file_path, status.HTTP_400_BAD_REQUEST
        )
    if not os.path.isfile(file_path):
        raise CellxgeneException(
            "Path is not file: " + file_path, status.HTTP_400_BAD_REQUEST
        )
    return


def get_file_path(dataset):
    file_path = os.path.join(env.cellxgene_data, dataset)
    validate_path(file_path)
    return file_path
