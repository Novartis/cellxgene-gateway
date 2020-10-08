# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import os

from cellxgene_gateway.items.item import Item


class S3Item(Item):
    """e.g. FileItem(subpath = subpath, name = filename, type = ItemType.h5ad)

    The Item superclass expects a 'name' and 'type'.
    """

    def __init__(self, s3key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s3key = s3key

    @property
    def descriptor(self) -> str:
        return self.s3key
