# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

from abc import ABC, abstractmethod
from typing import List

from cellxgene_gateway.items.item import Item


class LookupResult:
    def __init__(self, h5ad_item: Item, annotation_item: Item = None):
        self.h5ad_item = h5ad_item
        self.annotation_item = annotation_item


class ItemSource(ABC):
    @abstractmethod
    def list_items(self, filter: str = None) -> List[Item]:
        raise Exception('"list_items" unimplemented')

    @abstractmethod
    def get_local_path(self, item: Item) -> str:
        raise Exception('"local_path" unimplemented')

    @abstractmethod
    def get_annotations_subpath(self, item) -> str:
        raise Exception('"annotations_path" unimplemented')

    @abstractmethod
    def create_annotation(self, item: Item, name: str) -> Item:
        raise Exception('"annotation" unimplemented')

    @abstractmethod
    def update(self, item: Item) -> None:
        raise Exception('"update" unimplemented')

    @abstractmethod
    def lookup(self, descriptor: str) -> LookupResult:
        raise Exception('"lookup" unimplemented')

    @property
    @abstractmethod
    def name(self):
        pass
