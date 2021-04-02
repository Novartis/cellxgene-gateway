# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

# There are three kinds of CacheKey:
# 1) somedir/dataset.h5ad: a dataset
#    in this case, descriptor == dataset == 'somedir/dataset.h5ad'
# 2) somedir/dataset_annotations/my_annotations.csv : an actual annotations file.
#    in this case, descriptor == 'somedir/dataset_annotations/my_annotations.csv', dataset == 'somedir/dataset.h5ad'
# 3) somedir/dataset_annotations: an annotation directory. The corresponding h5ad must exist, but the directory may not.
#    in this case, descriptor == 'somedir/dataset_annotations', dataset == 'somedir/dataset.h5ad'

from cellxgene_gateway import flask_util
from cellxgene_gateway.items.item import Item
from cellxgene_gateway.items.item_source import ItemSource, LookupResult


class CacheKey:
    @property
    def descriptor(self):
        if self.annotation_item is None:
            return self.h5ad_item.descriptor
        else:
            return self.annotation_item.descriptor

    @property
    def file_path(self):
        return self.source.get_local_path(self.h5ad_item)

    @property
    def annotation_file_path(self):
        if self.annotation_item is None:
            return None
        else:
            return self.source.get_local_path(self.annotation_item)

    def relaunch_url(self):
        return flask_util.relaunch_url(self.descriptor, self.source_name)

    def gateway_basepath(self):
        return self.view_url + "/"

    @property
    def view_url(self):
        return flask_util.view_url(self.descriptor, self.source_name)

    @property
    def source_name(self):
        return self.source.name

    @property
    def annotation_descriptor(self):
        if self.annotation_item is None:
            return None
        else:
            return self.annotation_item.descriptor

    def equals(self, other):
        return (
            (self.source.name == other.source.name)
            and (self.h5ad_item.descriptor == other.h5ad_item.descriptor)
            and (self.annotation_descriptor == other.annotation_descriptor)
        )

    def __init__(
        self, h5ad_item: Item, source: ItemSource, annotation_item: Item = None
    ):
        assert h5ad_item is not None
        assert source is not None
        self.h5ad_item = h5ad_item
        self.annotation_item = annotation_item
        self.source = source

    @classmethod
    def for_lookup(cls, source: ItemSource, lookup: LookupResult):
        return CacheKey(lookup.h5ad_item, source, lookup.annotation_item)
