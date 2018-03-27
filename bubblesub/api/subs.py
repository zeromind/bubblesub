import re
from pathlib import Path

import pysubs2
from PyQt5 import QtCore

import bubblesub.ass
import bubblesub.util


NOTICE = 'Script generated by bubblesub\nhttps://github.com/rr-/bubblesub'

EMPTY_ASS = '''
[Script Info]
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResY: 288

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''


class Meta:
    def __init__(self, note=None, start=None, end=None):
        self.__dict__.update(locals())


def _extract_meta(text):
    meta = Meta(note=None, start=None, end=None)

    match = re.search(r'{NOTE:(?P<note>[^}]*)}', text)
    if match:
        text = text[:match.start()] + text[match.end():]
        meta.note = bubblesub.ass.unescape_ass_tag(match.group('note'))

    match = re.search(r'{TIME:(?P<start>-?\d+),(?P<end>-?\d+)}', text)
    if match:
        text = text[:match.start()] + text[match.end():]
        meta.start = int(match.group('start'))
        meta.end = int(match.group('end'))

    return text, meta


def _pack_meta(text, meta):
    if meta.start is not None or meta.end is not None:
        text = '{TIME:%d,%d}' % (meta.start, meta.end) + text

    if meta.note:
        text += '{NOTE:%s}' % (
            bubblesub.ass.escape_ass_tag(meta.note.replace('\n', '\\N')))

    return text


def _tuple_to_ssa_color(color):
    red, green, blue, alpha = color
    return pysubs2.Color(red, green, blue, alpha)


def _ssa_color_to_tuple(color):
    return (color.r, color.g, color.b, color.a)


class Style(bubblesub.util.ObservableObject):
    prop = {
        'name': bubblesub.util.ObservableObject.REQUIRED,
        'font_name': 'Arial',
        'font_size': 20,
        'primary_color': (255, 255, 255, 0),
        'secondary_color': (255, 0, 0, 0),
        'outline_color': (32, 32, 32, 0),
        'back_color': (32, 32, 32, 127),
        'bold': True,
        'italic': False,
        'underline': False,
        'strike_out': False,
        'scale_x': 100,
        'scale_y': 100,
        'spacing': 0,
        'angle': 0,
        'border_style': 1,
        'outline': 3,
        'shadow': 0,
        'alignment': 2,
        'margin_left': 20,
        'margin_right': 20,
        'margin_vertical': 20,
        'encoding': 1,
    }

    def __init__(self, styles, **kwargs):
        super().__init__(**kwargs)
        self.ssa_style = pysubs2.SSAStyle()
        self._styles = styles
        self._sync_ssa_style()
        self._old_name = None

    @staticmethod
    def from_ssa_style(styles, name, ssa_style):
        return Style(
            styles=styles,
            name=name,
            font_name=ssa_style.fontname,
            font_size=ssa_style.fontsize,
            primary_color=_ssa_color_to_tuple(ssa_style.primarycolor),
            secondary_color=_ssa_color_to_tuple(ssa_style.secondarycolor),
            outline_color=_ssa_color_to_tuple(ssa_style.outlinecolor),
            back_color=_ssa_color_to_tuple(ssa_style.backcolor),
            bold=ssa_style.bold,
            italic=ssa_style.italic,
            underline=ssa_style.underline,
            strike_out=ssa_style.strikeout,
            scale_x=ssa_style.scalex,
            scale_y=ssa_style.scaley,
            spacing=ssa_style.spacing,
            angle=ssa_style.angle,
            border_style=ssa_style.borderstyle,
            outline=ssa_style.outline,
            shadow=ssa_style.shadow,
            alignment=ssa_style.alignment,
            margin_left=ssa_style.marginl,
            margin_right=ssa_style.marginr,
            margin_vertical=ssa_style.marginv,
            encoding=ssa_style.encoding)

    def _sync_ssa_style(self):
        self.ssa_style.fontname = self.font_name
        self.ssa_style.fontsize = self.font_size
        self.ssa_style.primarycolor = _tuple_to_ssa_color(self.primary_color)
        self.ssa_style.secondarycolor = _tuple_to_ssa_color(
            self.secondary_color)
        self.ssa_style.outlinecolor = _tuple_to_ssa_color(self.outline_color)
        self.ssa_style.backcolor = _tuple_to_ssa_color(self.back_color)
        self.ssa_style.bold = self.bold
        self.ssa_style.italic = self.italic
        self.ssa_style.underline = self.underline
        self.ssa_style.strikeout = self.strike_out
        self.ssa_style.scalex = self.scale_x
        self.ssa_style.scaley = self.scale_y
        self.ssa_style.spacing = self.spacing
        self.ssa_style.angle = self.angle
        self.ssa_style.borderstyle = self.border_style
        self.ssa_style.outline = self.outline
        self.ssa_style.shadow = self.shadow
        self.ssa_style.alignment = self.alignment
        self.ssa_style.marginl = self.margin_left
        self.ssa_style.marginr = self.margin_right
        self.ssa_style.marginv = self.margin_vertical
        self.ssa_style.encoding = self.encoding

    def _before_change(self):
        self._old_name = self.name
        self._styles.item_about_to_change.emit(self.name)

    def _after_change(self):
        self._sync_ssa_style()
        self._styles.item_changed.emit(self._old_name)


class StyleList(bubblesub.util.ListModel):
    def insert_one(self, name, index=None, **kwargs):
        style = Style(styles=self, name=name, **kwargs)
        self.insert(len(self) if index is None else index, [style])
        return style

    def get_by_name(self, name):
        for style in self:
            if style.name == name:
                return style
        return None

    def load_from_ass(self, ass_source):
        collection = []
        for name, ssa_style in ass_source.styles.items():
            collection.append(Style.from_ssa_style(self, name, ssa_style))
        self.remove(0, len(self))
        self.insert(0, collection)

    def put_to_ass(self, ass_source):
        ass_source.styles.clear()
        for style in self:
            ass_source.styles[style.name] = style.ssa_style


class Subtitle(bubblesub.util.ObservableObject):
    prop = {
        'start': bubblesub.util.ObservableObject.REQUIRED,
        'end': bubblesub.util.ObservableObject.REQUIRED,
        'style': 'Default',
        'actor': '',
        'text': '',
        'note': '',
        'effect': '',
        'layer': 0,
        'margins': (0, 0, 0),
        'is_comment': False,
    }

    def __init__(self, subtitles, **kwargs):
        super().__init__(**kwargs)
        self.ssa_event = pysubs2.SSAEvent()
        self._subtitles = subtitles
        self._sync_ssa_event()

    @property
    def duration(self):
        return self.end - self.start

    @property
    def id(self):
        # XXX: meh
        for i, item in enumerate(self._subtitles):
            if item == self:
                return i
        return None

    @property
    def number(self):
        id_ = self.id
        if id_ is None:
            return None
        return id_ + 1

    @property
    def prev(self):
        id_ = self.id
        if id_ is None:
            return None
        return self._subtitles.get(id_ - 1, None)

    @property
    def next(self):
        id_ = self.id
        if id_ is None:
            return None
        return self._subtitles.get(id_ + 1, None)

    @staticmethod
    def from_ssa_event(subtitles, ssa_event):
        text, meta = _extract_meta(ssa_event.text)
        return Subtitle(
            subtitles,
            start=ssa_event.start if meta.start is None else meta.start,
            end=ssa_event.end if meta.end is None else meta.end,
            style=ssa_event.style,
            actor=ssa_event.name,
            text=text,
            note=meta.note or '',
            effect=ssa_event.effect,
            layer=ssa_event.layer,
            margins=(ssa_event.marginl, ssa_event.marginv, ssa_event.marginr),
            is_comment=ssa_event.is_comment)

    def _sync_ssa_event(self):
        self.ssa_event.start = self.start
        self.ssa_event.end = self.end
        self.ssa_event.style = self.style
        self.ssa_event.name = self.actor
        self.ssa_event.text = _pack_meta(
            self.text,
            Meta(
                note=self.note,
                start=self.start,
                end=self.end))
        self.ssa_event.effect = self.effect
        self.ssa_event.layer = self.layer
        self.ssa_event.marginl = self.margins[0]
        self.ssa_event.marginv = self.margins[1]
        self.ssa_event.marginr = self.margins[2]
        self.ssa_event.type = 'Comment' if self.is_comment else 'Dialogue'

    def _before_change(self):
        id_ = self.id
        if id_ is not None:
            self._subtitles.item_about_to_change.emit(id_)

    def _after_change(self):
        self._sync_ssa_event()
        id_ = self.id
        if id_ is not None:
            self._subtitles.item_changed.emit(id_)


class SubtitleList(bubblesub.util.ListModel):
    def insert_one(self, idx, **kwargs):
        subtitle = Subtitle(self, **kwargs)
        self.insert(idx, [subtitle])
        return subtitle

    def load_from_ass(self, ass_source):
        collection = []
        for ssa_event in ass_source:
            collection.append(Subtitle.from_ssa_event(self, ssa_event))
        self.remove(0, len(self))
        self.insert(0, collection)

    def put_to_ass(self, ass_source):
        del ass_source[:]
        for subtitle in self:
            ass_source.append(subtitle.ssa_event)


class SubtitlesApi(QtCore.QObject):
    loaded = QtCore.pyqtSignal()
    saved = QtCore.pyqtSignal()
    selection_changed = QtCore.pyqtSignal(list, bool)

    def __init__(self):
        super().__init__()
        self._loaded_video_path = None
        self._selected_indexes = []
        self._ass_source = pysubs2.SSAFile.from_string(
            EMPTY_ASS, format_='ass')
        self._path = None
        self.lines = SubtitleList()
        self.lines.items_about_to_be_removed.connect(
            self._on_items_about_to_be_removed)
        self.styles = StyleList()
        self.styles.insert_one('Default')

    @property
    def info(self):
        return self._ass_source.info

    @property
    def aegisub_project(self):
        return self._ass_source.aegisub_project

    @property
    def remembered_video_path(self):
        path = self._ass_source.aegisub_project.get('Video File', None)
        if not path:
            return None
        if not self._path:
            return None
        return self._path.parent / path

    @remembered_video_path.setter
    def remembered_video_path(self, path):
        self._ass_source.aegisub_project['Video File'] = str(path)
        self._ass_source.aegisub_project['Audio File'] = str(path)

    @property
    def path(self):
        return self._path

    @property
    def has_selection(self):
        return len(self.selected_indexes) > 0

    @property
    def selected_indexes(self):
        return self._selected_indexes

    @property
    def selected_lines(self):
        return [self.lines[idx] for idx in self.selected_indexes]

    @selected_indexes.setter
    def selected_indexes(self, new_selection):
        new_selection = list(sorted(new_selection))
        changed = new_selection != self._selected_indexes
        self._selected_indexes = new_selection
        self.selection_changed.emit(new_selection, changed)

    def unload(self):
        self._path = None
        self._ass_source = pysubs2.SSAFile.from_string(
            EMPTY_ASS, format_='ass')
        self.selected_indexes = []
        self.lines.remove(0, len(self.lines))
        self.styles.remove(0, len(self.styles))
        self.loaded.emit()

    def load_ass(self, path):
        assert path
        try:
            ass_source = pysubs2.load(str(path))
        except Exception:
            raise

        self._path = Path(path)
        self._ass_source = ass_source

        self.selected_indexes = []

        with bubblesub.util.Benchmark('loading subs'):
            self.lines.load_from_ass(self._ass_source)
            self.styles.load_from_ass(self._ass_source)
        self.loaded.emit()

    def save_ass(self, path, remember_path=False):
        with bubblesub.util.Benchmark('saving subs'):
            assert path
            path = Path(path)
            self.lines.put_to_ass(self._ass_source)
            self.styles.put_to_ass(self._ass_source)
            if remember_path:
                self._path = path
            self._ass_source.save(path, header_notice=NOTICE)
            if remember_path:
                self.saved.emit()

    def _on_items_about_to_be_removed(self, idx, count):
        new_indexes = list(sorted(self.selected_indexes))
        for i in reversed(range(idx, idx + count)):
            new_indexes = [
                j - 1 if j > i else j
                for j in new_indexes
                if j != i]
        self.selected_indexes = new_indexes
