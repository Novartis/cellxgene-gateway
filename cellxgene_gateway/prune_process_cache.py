# Copyright 2019 Novartis Institutes for BioMedical Research Inc. Licensed
# under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless
# required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import time
import logging

from cellxgene_gateway.util import current_time_stamp
from cellxgene_gateway.env import ttl


class PruneProcessCache:
    def __init__(self, cache):
        self.cache = cache

    def __call__(self):
        while True:
            time.sleep(60)
            self.prune()

    def prune(self):
        timestamp = current_time_stamp()

        processes_to_delete = []
        for p in self.cache.entry_list:
            if timestamp - p.timestamp > (3600 if ttl is None else ttl):
                processes_to_delete.append(p)
                processes_to_delete

        for process in processes_to_delete:
            try:
                cache.prune(process)
            except Exception:
                logging.getLogger("werkzeug").exception("failed to prune process")

