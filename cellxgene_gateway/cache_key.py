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
#    in this case, pathpart == dataset == 'somedir/dataset.h5ad'
# 2) somedir/dataset_annotations/my_annotations.csv : an actual annotaitons file.
#    in this case, pathpart == 'dataset_annotations/my_annotations.csv', dataset == 'somedir/dataset.h5ad'
# 3) somedir/dataset_annotations: an annotation directory. The corresponding h5ad must exist, but the directory may not.
#    in this case, pathpart == 'dataset_annotations', dataset == 'somedir/dataset.h5ad'


class CacheKey:
    def __init__(self, pathpart, dataset, annotation_file):
        self.pathpart = pathpart
        self.dataset = dataset
        self.annotation_file = annotation_file
