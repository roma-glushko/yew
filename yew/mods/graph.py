import logging
import tokenize
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Sequence, Set, Tuple

from yew.collection import DirectImport, ModGraph, ModName
from yew.mods.filters import ImportFilter
from yew.mods.finders import ModFinder
from yew.mods.parsers import ModParser

ParsedModuleFile = Tuple[ModName, Path, Set[DirectImport]]

logger = logging.getLogger(__name__)


def build_mod_graph(
    packages: Sequence[Path],
    *,
    include_external: bool = False,
    include_third_party: bool = False,
    workers: int = 5,
) -> ModGraph:
    """
    Build a module import graph
    """
    mod_graph = ModGraph()

    mod_finder = ModFinder()
    mod_parser = ModParser()
    mod_filter = ImportFilter(
        include_external=include_external,
        include_third_party=include_third_party,
    )

    def process_module_file(file_path: Path) -> Optional[ParsedModuleFile]:
        """
        Process an individual module file
        """
        logger.debug(f"Parsing {file_path} file")

        mod_name = ModName.from_path(file_path)

        with tokenize.open(file_path) as file:
            content = file.read()

        try:
            imported_mods = mod_parser.parse(mod_name, content)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path} file at {e.lineno}:{e.offset}: {e.msg}")
            return None

        filtered_imports = mod_filter.filter(imported_mods)

        return mod_name, file_path, filtered_imports

    futures: List[Future[ParsedModuleFile]] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        for file_path in mod_finder.find(packages):
            futures.append(
                executor.submit(process_module_file, file_path),  # type: ignore[arg-type]
            )

        for future in as_completed(futures):
            result = future.result()

            if not result:
                continue

            mod_name, file_path, filtered_imports = result

            mod_graph.add(mod_name, file_path, filtered_imports)

    return mod_graph
