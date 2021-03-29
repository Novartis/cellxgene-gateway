# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

from abc import ABC, abstractmethod
from enum import Enum
from typing import List


class ItemType(Enum):
    annotation = "annotation"
    h5ad = "h5ad"


class Item(ABC):
    def __init__(self, name: str, type: ItemType, annotations: List["Item"] = None):
        self.name = name
        self.type = type
        self.annotations = annotations

    @property
    @abstractmethod
    def descriptor(self):
        raise Exception('"descriptor" not implemented')


class ItemTree:
    def __init__(
        self,
        descriptor: str,
        items: List[Item] = None,
        branches: List["ItemTree"] = None,
    ):
        self.descriptor = descriptor
        self.items = items
        self.branches = branches
