# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

from os.path import basename, dirname, join
from typing import List

import s3fs

from cellxgene_gateway import dir_util
from cellxgene_gateway.items.item import ItemTree, ItemType
from cellxgene_gateway.items.item_source import ItemSource, LookupResult
from cellxgene_gateway.items.s3.s3item import S3Item


class S3ItemSource(ItemSource):
    def __init__(
        self,
        bucket,
        name=None,
        h5ad_suffix=dir_util.h5ad_suffix,
        annotation_dir_suffix=dir_util.annotations_suffix,
        annotation_file_suffix=".csv",
    ):
        self._name = name
        self.s3 = s3fs.S3FileSystem()
        if bucket.startswith("s3://"):
            raise Exception(
                f"Bucket name should not include s3:// prefix, got {bucket}"
            )
        self.bucket = bucket
        self.h5ad_suffix = h5ad_suffix
        self.annotation_dir_suffix = annotation_dir_suffix
        self.annotation_file_suffix = annotation_file_suffix

    def url(self, key):
        return "s3://" + self.bucket + "/" + key

    def remove_bucket(self, filepath):
        return filepath[len(self.bucket) :].lstrip("/")

    @property
    def name(self):
        return self._name or f"Items:{self.url('')}"

    def is_h5ad_url(self, s3url: str) -> bool:
        return s3url.endswith(self.h5ad_suffix) and self.s3.exists(s3url)

    def convert_annotation_key_to_h5ad(self, s3key):
        return s3key[: -len(self.annotation_dir_suffix)] + self.h5ad_suffix

    def convert_h5ad_key_to_annotation(self, s3key):
        return s3key[: -len(self.h5ad_suffix)] + self.annotation_dir_suffix

    def get_local_path(self, item: S3Item) -> str:
        return self.url(item.descriptor)

    def get_annotations_subpath(self, item) -> str:
        return self.convert_h5ad_key_to_annotation(item.descriptor)

    def list_items(self, filter: str = None) -> ItemTree:
        item_tree = self.scan_directory("" if filter is None else filter)
        return item_tree

    def scan_directory(self, directory_key="") -> dict:
        url = self.url(directory_key)

        if not self.s3.exists(url):
            raise Exception(f"S3 url '{url}' does not exist.")

        s3key_map = dict(
            (self.remove_bucket(filepath), "s3://" + filepath)
            for filepath in sorted(self.s3.ls(url))
        )

        def is_annotation_dir(dir_s3key):
            return (
                dir_s3key.endswith(self.annotation_dir_suffix)
                and self.convert_annotation_key_to_h5ad(dir_s3key) in h5ad_keys
            )

        h5ad_keys = [
            filepath
            for filepath, item_url in s3key_map.items()
            if self.is_h5ad_url(item_url)
        ]

        subdir_keys = [
            filepath
            for filepath, item_url in s3key_map.items()
            if self.s3.isdir(item_url) and not is_annotation_dir(filepath)
        ]

        items = [self.make_s3item_from_key(basename(key), key) for key in h5ad_keys]
        branches = None
        if len(subdir_keys) > 0:
            branches = [self.scan_directory(key) for key in subdir_keys]

        return ItemTree(directory_key, items, branches)

    def create_annotation(self, item: S3Item, name: str) -> S3Item:
        annotation = self.make_s3item_from_key(
            name, self.get_annotations_subpath(item), is_annotation=True
        )
        item.annotations = (item.annotations or []).append(annotation)
        return annotation

    def update(self, item: S3Item) -> None:
        pass

    def lookup_item(self, descriptor):
        full_path = self.url(descriptor)
        if self.is_h5ad_url(full_path):
            return self.shallowitem_from_descriptor(descriptor)

    def lookup(self, indescriptor: str) -> LookupResult:
        descriptor = indescriptor.strip("/")
        if descriptor.endswith(self.annotation_file_suffix):
            annotation_item = self.shallowitem_from_descriptor(descriptor, True)
            if not self.s3.exists(self.url(annotation_item.s3key)):
                with self.s3.open(self.url(annotation_item.s3key), "w") as f:
                    f.write("")
            h5ad_descriptor = self.convert_annotation_key_to_h5ad(
                dirname(annotation_item.s3key)
            )
            item = self.shallowitem_from_descriptor(h5ad_descriptor)
            return LookupResult(item, annotation_item)
        else:
            item = self.lookup_item(descriptor)
            if item is not None:
                return LookupResult(item)

    def shallowitem_from_descriptor(self, descriptor, is_annotation=False):
        return self.make_s3item_from_key(
            basename(descriptor), descriptor, is_annotation, True
        )

    def make_s3item_from_key(
        self, name, s3key, is_annotation=False, is_shallow=False
    ) -> S3Item:
        item = S3Item(
            s3key=s3key,
            name=name,
            type=ItemType.annotation if is_annotation else ItemType.h5ad,
        )

        if not is_annotation and not is_shallow:
            annotations = self.make_annotations_for_fileitem(item)
            item.annotations = annotations

        return item

    def make_annotations_for_fileitem(self, item: S3Item) -> List[S3Item]:
        annotations_subpath = self.get_annotations_subpath(item)
        annotations_fullpath = self.url(annotations_subpath)
        if self.s3.isdir(annotations_fullpath):
            return [
                self.make_s3item_from_key(
                    basename(annotation), self.remove_bucket(annotation), True
                )
                for annotation in sorted(self.s3.ls(annotations_fullpath))
                if annotation.endswith(self.annotation_file_suffix)
                and self.s3.isfile("s3://" + annotation)
            ]
        else:
            return None
