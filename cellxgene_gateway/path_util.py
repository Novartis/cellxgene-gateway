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

from cellxgene_gateway.cache_key import CacheKey
from cellxgene_gateway.cellxgene_exception import CellxgeneException
from cellxgene_gateway.dir_util import make_h5ad


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
