# bubblesub - ASS subtitle editor
# Copyright (C) 2018 Marcin Kurczewski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Base config."""

import abc
from pathlib import Path


class ConfigError(RuntimeError):
    """Base config error."""


class SubConfig(abc.ABC):
    """Base config."""

    @abc.abstractmethod
    def load(self, root_dir: Path) -> None:
        """Load internals of this config from the specified directory.

        :param root_dir: directory where to look for the matching config file
        """
        raise NotImplementedError("not implemented")
