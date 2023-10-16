import logging
import site
import sys
from pathlib import Path
from typing import Set

from yew.collection import DirectImport

logger = logging.getLogger(__name__)


class ImportFilter:
    def __init__(self, include_external: bool = False, include_third_party: bool = False) -> None:
        self._include_external = include_external
        self._include_third_party = include_third_party

    def filter(self, imports: Set[DirectImport]) -> Set[DirectImport]:
        return {direct_import for direct_import in imports if not self._is_third_party(direct_import)}

    def _is_third_party(self, direct_import: DirectImport) -> bool:
        if self._include_third_party:
            return False

        mod_name_str = str(direct_import.mod_name)

        if mod_name_str in sys.builtin_module_names:
            logger.debug(f"skipping {mod_name_str} as a built-in module")
            return True

        if mod_name_str in sys.stdlib_module_names:
            logger.debug(f"skipping {mod_name_str} as a stdlib module")
            return True

        for site_path in site.getsitepackages():
            if Path(site_path) in direct_import.path.parents:
                logger.debug(f"skipping {mod_name_str} as a third-party module")
                return True

        return False
