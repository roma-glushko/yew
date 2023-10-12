import os
from pathlib import Path
from typing import Iterator, Sequence


class ModFinder:
    """
    Retrieve all Python modules
    """

    def __init__(self) -> None:
        ...

    def find(self, packages: Sequence[Path], *, follow_links: bool = False) -> Iterator[Path]:
        """
        Find all Python files under the given packages
        """
        for package in packages:
            for dirpath, dirs, files in os.walk(package, followlinks=follow_links):
                if "__init__.py" not in files:
                    for d in list(dirs):
                        dirs.remove(d)

                    continue

                dirs_to_remove = [d for d in dirs if self._is_hidden(d)]

                for d in dirs_to_remove:
                    dirs.remove(d)

                for filename in files:
                    if self._ignore_file(filename):
                        print(f"Ignored: {filename}")
                        continue

                    yield Path(dirpath) / filename

    def _ignore_file(self, filename: str) -> bool:
        if self._is_hidden(filename):
            return True

        if filename.count(".") > 1:
            return True

        return not filename.endswith(".py")

    def _is_hidden(self, file: str) -> bool:
        return file.startswith(".")
