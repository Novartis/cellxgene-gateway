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
        self.expire_seconds = 3600 if ttl is None else int(ttl)

    def __call__(self):
        while True:
            time.sleep(60)
            self.prune()

    def prune(self):
        timestamp = current_time_stamp()
        cutoff = timestamp - self.expire_seconds
        processes_to_delete = [
            p for p in self.cache.entry_list if p.timestamp < cutoff
        ]
        processes_to_keep = [
            p for p in self.cache.entry_list if not p.timestamp < cutoff
        ]
        logger = logging.getLogger("cellxgene_gateway")
        logger.debug(
            f"Cutoff {cutoff} = timestamp {timestamp} - expire seconds {self.expire_seconds} , keeping {processes_to_keep}"
        )

        for process in processes_to_delete:
            try:
                logger.info(
                    f"pruning process {process.pid} ({process.key.dataset})"
                )
                self.cache.prune(process)
            except Exception:
                logger.exception(
                    "failed to prune process {process.pid} ({process.dataset})"
                )
