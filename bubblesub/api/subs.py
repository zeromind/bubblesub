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

"""Subtitles API."""

import typing as T
from pathlib import Path

from PyQt5 import QtCore

from bubblesub.cfg import Config
from bubblesub.fmt.ass.event import AssEvent, AssEventList
from bubblesub.fmt.ass.file import AssFile
from bubblesub.fmt.ass.meta import AssMeta
from bubblesub.fmt.ass.reader import load_ass
from bubblesub.fmt.ass.style import AssStyle, AssStyleList
from bubblesub.fmt.ass.writer import write_ass
from bubblesub.util import first


class SubtitlesApi(QtCore.QObject):
    """The subtitles API.

    Encapsulates ASS styles, subtitles and subtitle selection.
    """

    loaded = QtCore.pyqtSignal()
    saved = QtCore.pyqtSignal()
    selection_changed = QtCore.pyqtSignal(list, bool)

    def __init__(self, cfg: Config) -> None:
        """Initialize self.

        :param cfg: program configuration
        """
        super().__init__()
        self._cfg = cfg
        self._selected_indexes: T.List[int] = []
        self._path: T.Optional[Path] = None

        self.ass_file = AssFile()

        self.meta_changed = self.ass_file.meta.changed
        self.events.items_removed.connect(self._on_items_removed)

    @property
    def events(self) -> AssEventList:
        """Return list of ASS events.

        :return: list of events
        """
        return self.ass_file.events

    @property
    def styles(self) -> AssStyleList:
        """Return list of ASS styles.

        :return: list of styles
        """
        return self.ass_file.styles

    @property
    def meta(self) -> AssMeta:
        """Return additional information associated with the ASS file.

        This holds basic information about ASS version, video resolution etc.

        :return: additional information
        """
        return self.ass_file.meta

    @property
    def remembered_video_paths(self) -> T.Iterable[Path]:
        """Return path of the associated video files.

        :return: paths of the associated video files or empty list if none
        """
        for segment in (self.meta.get("Video File") or "").split("|"):
            if segment:
                path = Path(segment)
                yield self._path.parent / path if self._path else path

    @property
    def remembered_audio_paths(self) -> T.Iterable[Path]:
        """Return path of the associated audio files.

        :return: paths of the associated audio files or empty list if none
        """
        for segment in (self.meta.get("Audio File") or "").split("|"):
            if segment:
                path = Path(segment)
                yield self._path.parent / path if self._path else path

    def remember_video_path_if_needed(self, path: Path) -> None:
        """Add given path to associated video files if it's not there yet.

        :param path: path to remember
        """
        paths = list(self.remembered_video_paths)
        if not paths or not any(
            remembered_path.samefile(path) for remembered_path in paths
        ):
            paths.append(path)
            self.meta.update({"Video File": "|".join(map(str, paths))})

    def remember_audio_path_if_needed(self, path: Path) -> None:
        """Add given path to associated audio files if it's not there yet.

        :param path: path to remember
        """
        paths = list(self.remembered_audio_paths)
        if not paths or not any(
            remembered_path.samefile(path) for remembered_path in paths
        ):
            paths.append(path)
            self.meta.update({"Audio File": "|".join(map(str, paths))})

    @property
    def language(self) -> T.Optional[str]:
        """Return the language of the subtitles, in ISO 639-1 form.

        :return: language
        """
        return T.cast(str, self.meta.get("Language") or "") or None

    @language.setter
    def language(self, language: T.Optional[str]) -> None:
        """Set the language of the subtitles, in ISO 639-1 form.

        :param language: language
        """
        if language:
            self.meta.set("Language", language)
        else:
            self.meta.remove("Language")

    @property
    def path(self) -> T.Optional[Path]:
        """Return path of the currently loaded ASS file.

        :return: path of the currently loaded ASS file or None if no file
        """
        return self._path

    @property
    def has_selection(self) -> bool:
        """Return whether there are any selected events.

        :return: whether there are any selected events
        """
        return len(self.selected_indexes) > 0

    @property
    def selected_indexes(self) -> T.List[int]:
        """Return indexes of the selected events.

        :return: indexes of the selected events
        """
        return self._selected_indexes

    @selected_indexes.setter
    def selected_indexes(self, new_selection: T.List[int]) -> None:
        """Update event selection.

        :param new_selection: new list of selected indexes
        """
        new_selection = list(sorted(new_selection))
        changed = new_selection != self._selected_indexes
        self._selected_indexes = new_selection
        self.selection_changed.emit(new_selection, changed)

    @property
    def selected_events(self) -> T.List[AssEvent]:
        """Return list of selected events.

        :return: list of selected events
        """
        return [self.events[idx] for idx in self.selected_indexes]

    @property
    def default_style_name(self) -> str:
        """Return default style name.

        :return: first style name if it exists, otherwise "Default"
        """
        style = first(self.styles)
        if style and style.name:
            return style.name
        return "Default"

    def unload(self) -> None:
        """Load empty ASS file."""
        self._path = None
        self.selected_indexes = []
        self.ass_file.meta.clear()
        self.ass_file.events.clear()
        self.ass_file.styles.clear()
        self.ass_file.styles.append(AssStyle(name=self.default_style_name))
        self.ass_file.meta.update(
            {"Language": self._cfg.opt["gui"]["spell_check"]}
        )
        self.loaded.emit()

    def load_ass(self, path: T.Union[str, Path]) -> None:
        """Load specified ASS file.

        :param path: path to load the file from
        """
        assert path
        path = Path(path)
        with path.open("r") as handle:
            load_ass(handle, self.ass_file)

        self._cfg.opt.add_recent_file(path)

        self.selected_indexes = []
        self._path = path
        self.loaded.emit()

    def save_ass(
        self, path: T.Union[str, Path], remember_path: bool = False
    ) -> None:
        """Save current state to the specified file.

        :param path: path to save the state to
        :param remember_path:
            whether to update `self.path` with the specified `path`
        """
        assert path
        path = Path(path)
        if remember_path:
            self._path = path
        with path.open("w") as handle:
            write_ass(self.ass_file, handle)
        if remember_path:
            self.saved.emit()
            self._cfg.opt.add_recent_file(path)

    def _on_items_removed(self, idx: int, count: int) -> None:
        new_indexes = list(sorted(self.selected_indexes))
        for i in reversed(range(idx, idx + count)):
            new_indexes = [
                j - 1 if j > i else j for j in new_indexes if j != i
            ]
        self.selected_indexes = new_indexes
