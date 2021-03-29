# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import os
from typing import List

from cellxgene_gateway import dir_util
from cellxgene_gateway.items.file.fileitem import FileItem
from cellxgene_gateway.items.item import ItemTree, ItemType
from cellxgene_gateway.items.item_source import ItemSource, LookupResult


class FileItemSource(ItemSource):
    def __init__(
        self,
        base_path,
        name=None,
        h5ad_suffix=dir_util.h5ad_suffix,
        annotation_dir_suffix=dir_util.annotations_suffix,
        annotation_file_suffix=".csv",
    ):
        self._name = name
        self.base_path = base_path
        self.h5ad_suffix = h5ad_suffix
        self.annotation_dir_suffix = annotation_dir_suffix
        self.annotation_file_suffix = annotation_file_suffix

    @property
    def name(self):
        return self._name or f"Files:{self.base_path}"

    def is_h5ad_file(self, path: str) -> bool:
        return path.endswith(self.h5ad_suffix) and os.path.isfile(path)

    def convert_annotation_path_to_h5ad(self, path):
        return path[: -len(self.annotation_dir_suffix)] + self.h5ad_suffix

    def convert_h5ad_path_to_annotation(self, path):
        return path[: -len(self.h5ad_suffix)] + self.annotation_dir_suffix

    def get_local_path(self, item: FileItem) -> str:
        return os.path.join(self.base_path, item.descriptor)

    def get_annotations_subpath(self, item) -> str:
        return self.convert_h5ad_path_to_annotation(item.descriptor)

    def list_items(self, filter: str = None) -> ItemTree:
        item_tree = self.scan_directory()

        """def get_items(dir):
            if dir.branches:
                return [*dir.items, *[item for subdir in dir.branches for item in get_items(subdir)]]
            else:
                return dir.items

        return get_items(self.item_tree)"""

        return item_tree

    def scan_directory(self, subpath="") -> dict:
        base_path = os.path.join(self.base_path, subpath)

        if not os.path.exists(base_path):
            raise Exception(f"Path for local files '{base_path}' does not exist.")

        filepath_map = dict(
            (filepath, os.path.join(base_path, filepath))
            for filepath in sorted(os.listdir(base_path))
        )

        def is_annotation_dir(dir):
            return (
                dir.endswith(self.annotation_dir_suffix)
                and self.convert_annotation_path_to_h5ad(dir) in h5ad_paths
            )

        h5ad_paths = [
            filepath
            for filepath, full_path in filepath_map.items()
            if self.is_h5ad_file(full_path)
        ]

        subdirs = [
            filepath
            for filepath, full_path in filepath_map.items()
            if os.path.isdir(full_path) and not is_annotation_dir(filepath)
        ]

        items = [
            self.make_fileitem_from_path(filename, subpath) for filename in h5ad_paths
        ]
        branches = None
        if len(subdirs) > 0:
            branches = [
                self.scan_directory(os.path.join(subpath, subdir)) for subdir in subdirs
            ]

        return ItemTree(subpath, items, branches)

    def create_annotation(self, item: FileItem, name: str) -> FileItem:
        annotation = self.make_fileitem_from_path(
            name, self.get_annotations_subpath(item), is_annotation=True
        )
        item.annotations = (item.annotations or []).append(annotation)
        return annotation

    def update(self, item: FileItem) -> None:
        pass

    def full_path(self, p):
        return os.path.join(self.base_path, p)

    def lookup_item(self, descriptor):
        full_path = self.full_path(descriptor)
        if self.is_h5ad_file(full_path):
            return self.shallowitem_from_descriptor(descriptor)

    def lookup(self, indescriptor: str) -> LookupResult:
        descriptor = indescriptor.strip("/")
        if descriptor.endswith(self.annotation_file_suffix):
            annotation_item = self.shallowitem_from_descriptor(descriptor, True)
            h5ad_descriptor = self.convert_annotation_path_to_h5ad(
                annotation_item.subpath
            )
            item = self.lookup_item(h5ad_descriptor)
            if item is not None:
                dir_util.ensure_dir_exists(self.full_path(annotation_item.subpath))
                return LookupResult(item, annotation_item)
        else:
            item = self.lookup_item(descriptor)
            if item is not None:
                return LookupResult(item)

    def shallowitem_from_descriptor(self, descriptor, is_annotation=False):
        filename = os.path.basename(descriptor)
        subpath = os.path.dirname(descriptor)
        return self.make_fileitem_from_path(
            filename,
            subpath,
            is_annotation,
            True,
        )

    def make_fileitem_from_path(
        self, filename, subpath, is_annotation=False, is_shallow=False
    ) -> FileItem:
        if is_annotation and filename.endswith(self.annotation_file_suffix):
            name = filename[: -len(self.annotation_file_suffix)]
            ext = self.annotation_file_suffix
        else:
            name = filename
            ext = ""
        item = FileItem(
            subpath=subpath,
            name=name,
            ext=ext,
            type=ItemType.annotation if is_annotation else ItemType.h5ad,
        )

        if not is_annotation and not is_shallow:
            annotations = self.make_annotations_for_fileitem(item)
            item.annotations = annotations

        return item

    def make_annotations_for_fileitem(self, item: FileItem) -> List[FileItem]:
        annotations_subpath = self.get_annotations_subpath(item)
        annotations_fullpath = self.full_path(annotations_subpath)
        if os.path.isdir(annotations_fullpath):
            return [
                self.make_fileitem_from_path(annotation, annotations_subpath, True)
                for annotation in sorted(os.listdir(annotations_fullpath))
                if annotation.endswith(self.annotation_file_suffix)
                and os.path.isfile(os.path.join(annotations_fullpath, annotation))
            ]
        else:
            return None
