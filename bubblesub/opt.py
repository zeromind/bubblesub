import json


class Serializer:
    def __init__(self, location):
        self._location = location

    @property
    def _hotkeys_path(self):
        return self._location / 'hotkey.json'

    @property
    def _menu_path(self):
        return self._location / 'menu.json'

    @property
    def _general_path(self):
        return self._location / 'general.json'

    def load(self):
        hotkeys = None
        menu = None
        general = None
        if self._hotkeys_path.exists():
            hotkeys = json.loads(self._hotkeys_path.read_text())
        if self._menu_path.exists():
            menu = json.loads(self._menu_path.read_text())
        if self._general_path.exists():
            general = json.loads(self._general_path.read_text())
        return hotkeys, menu, general

    def write(self, hotkeys, menu, general):
        self._location.mkdir(parents=True, exist_ok=True)
        self._hotkeys_path.write_text(json.dumps(hotkeys, indent=4))
        self._menu_path.write_text(json.dumps(menu, indent=4))
        self._general_path.write_text(json.dumps(general, indent=4))


class Options:
    def __init__(self):
        self.general = {
            'convert_newlines': True,
            'fonts': {
                'editor': None,
            },
            'subs': {
                'max_characters_per_second': 15,
                'default_duration': 2000,
            },
            'video': {
                'subs_sync_interval': 65,
            },
            'audio': {
                'spectrogram_resolution': 10,
                'spectrogram_sync_interval': 65,
            },
        }

        self.hotkeys = {
            'global': [
                ('Ctrl+Shift+N', 'file/new'),
                ('Ctrl+O', 'file/open'),
                ('Ctrl+S', 'file/save'),
                ('Ctrl+Shift+S', 'file/save-as'),
                ('Ctrl+Q', 'file/quit'),
                ('Ctrl+G', 'grid/jump-to-line'),
                ('Ctrl+Shift+G', 'grid/jump-to-time'),
                ('Ctrl+K', 'grid/select-prev-sub'),
                ('Ctrl+J', 'grid/select-next-sub'),
                ('Ctrl+A', 'grid/select-all'),
                ('Ctrl+Shift+A', 'grid/select-nothing'),
                ('Alt+1', 'video/play-around-sel-start', -500, 0),
                ('Alt+2', 'video/play-around-sel-start', 0, 500),
                ('Alt+3', 'video/play-around-sel-end', -500, 0),
                ('Alt+4', 'video/play-around-sel-end', 0, 500),
                ('Ctrl+R', 'video/play-around-sel', 0, 0),
                ('Ctrl+,', 'video/step-frame', -1),
                ('Ctrl+.', 'video/step-frame', 1),
                ('Ctrl+Shift+,', 'video/step-frame', -10),
                ('Ctrl+Shift+.', 'video/step-frame', 10),
                ('Ctrl+T', 'video/play-current-line'),
                ('Ctrl+P', 'video/toggle-pause'),
                ('Ctrl+Z', 'edit/undo'),
                ('Ctrl+Y', 'edit/redo'),
                ('Alt+C', 'edit/copy'),  # TODO
                ('Ctrl+Return', 'edit/insert-below'),
                ('Ctrl+Delete', 'edit/delete'),
                ('Ctrl+Shift+1', 'edit/move-sel-start', -250),
                ('Ctrl+Shift+2', 'edit/move-sel-start', 250),
                ('Ctrl+Shift+3', 'edit/move-sel-end', -250),
                ('Ctrl+Shift+4', 'edit/move-sel-end', 250),
                ('Ctrl+1', 'edit/move-sel-start', -25),
                ('Ctrl+2', 'edit/move-sel-start', 25),
                ('Ctrl+3', 'edit/move-sel-end', -25),
                ('Ctrl+4', 'edit/move-sel-end', 25),
                ('Ctrl+B', 'edit/snap-sel-start-to-video'),
                ('Ctrl+N', 'edit/snap-sel-to-video'),
                ('Ctrl+M', 'edit/snap-sel-end-to-video'),
                ('Ctrl+[', 'video/set-playback-speed', 0.5),
                ('Ctrl+]', 'video/set-playback-speed', 1),
            ],

            'audio': [
                ('Shift+1', 'edit/move-sel-start', -250),
                ('Shift+2', 'edit/move-sel-start', 250),
                ('Shift+3', 'edit/move-sel-end', -250),
                ('Shift+4', 'edit/move-sel-end', 250),
                ('1', 'edit/move-sel-start', -25),
                ('2', 'edit/move-sel-start', 25),
                ('3', 'edit/move-sel-end', -25),
                ('4', 'edit/move-sel-end', 25),
                ('C', 'edit/commit-sel'),
                ('K', 'edit/insert-above'),
                ('J', 'edit/insert-below'),
                ('R', 'video/play-around-sel', 0, 0),
                ('T', 'video/play-current-line'),
                ('P', 'video/toggle-pause'),
                ('Shift+K', 'grid/select-prev-sub'),
                ('Shift+J', 'grid/select-next-sub'),
                ('A', 'audio/scroll', -1),
                ('F', 'audio/scroll', 1),
                (',', 'video/step-frame', -1),
                ('.', 'video/step-frame', 1),
                ('Shift+,', 'video/step-frame', -10),
                ('Shift+.', 'video/step-frame', 10),
                ('B', 'edit/snap-sel-start-to-video'),
                ('N', 'edit/snap-sel-to-video'),
                ('M', 'edit/snap-sel-end-to-video'),
                ('[', 'video/set-playback-speed', 0.5),
                (']', 'video/set-playback-speed', 1),
            ],
        }

        self.menu = [
            ('&File', [
                ('New', 'file/new'),
                ('Open', 'file/open'),
                ('Save', 'file/save'),
                ('Save as', 'file/save-as'),
                None,
                ('Load video', 'file/load-video'),
                None,
                ('Quit', 'file/quit'),
            ]),

            ('&Grid', [
                ('Jump to line...', 'grid/jump-to-line'),
                ('Jump to time...', 'grid/jump-to-time'),
                ('Select previous subtitle', 'grid/select-prev-sub'),
                ('Select next subtitle', 'grid/select-next-sub'),
                ('Select all subtitles', 'grid/select-all'),
                ('Clear selection', 'grid/select-nothing'),
            ]),

            ('&Playback', [
                ('Play around selection', [
                    ('Play 500 ms before selection start', 'video/play-around-sel-start', -500, 0),
                    ('Play 500 ms after selection start', 'video/play-around-sel-start', 0, 500),
                    ('Play 500 ms before selection end', 'video/play-around-sel-end', -500, 0),
                    ('Play 500 ms after selection end', 'video/play-around-sel-end', 0, 500),
                ]),
                ('Play selection', 'video/play-around-sel', 0, 0),
                ('Play current line', 'video/play-current-line'),
                ('Play until end of the file', 'video/unpause'),
                None,
                ('Step 1 frame backward', 'video/step-frame', -1),
                ('Step 1 frame forward', 'video/step-frame', 1),
                ('Step 10 frames backward', 'video/step-frame', -10),
                ('Step 10 frames forward', 'video/step-frame', 10),
                None,
                ('Pause playback', 'video/pause'),
                ('Toggle pause', 'video/toggle-pause'),
                None,
                ('Set playback speed to 0.5x', 'video/set-playback-speed', 0.5),
                ('Set playback speed to 1x', 'video/set-playback-speed', 1),
            ]),

            ('&Timing', [
                ('Snap selection to subtitles', [
                    ('Snap start to previous subtitle', 'edit/snap-sel-start-to-prev-sub'),
                    ('Snap end to next subtitle', 'edit/snap-sel-end-to-next-sub'),
                ]),
                ('Snap selection to video frame', [
                    ('Snap start', 'edit/snap-sel-start-to-video'),
                    ('Snap end', 'edit/snap-sel-end-to-video'),
                    ('Snap both', 'edit/snap-sel-to-video'),
                ]),
                ('Shift selection', [
                    ('Shift start (-250 ms)', 'edit/move-sel-start', -250),
                    ('Shift start (+250 ms)', 'edit/move-sel-start', 250),
                    ('Shift end (-250 ms)', 'edit/move-sel-end', -250),
                    ('Shift end (+250 ms)', 'edit/move-sel-end', 250),
                    ('Shift start (-25 ms)', 'edit/move-sel-start', -25),
                    ('Shift start (+25 ms)', 'edit/move-sel-start', 25),
                    ('Shift end (-25 ms)', 'edit/move-sel-end', -25),
                    ('Shift end (+25 ms)', 'edit/move-sel-end', 25),
                ]),
                ('Commit selection to subtitle', 'edit/commit-sel'),
                None,
                ('Shift times...', 'edit/shift-subs-times-with-gui'),
                None,
                ('Scroll waveform backward', 'audio/scroll', -1),
                ('Scroll waveform forward', 'audio/scroll', 1),
            ]),

            ('&Edit', [
                ('Undo', 'edit/undo'),
                ('Redo', 'edit/redo'),
                None,
                # ('Copy to clipboard', 'edit/copy'),  # TODO
                None,
                ('Add new subtitle above current line', 'edit/insert-above'),
                ('Add new subtitle below current line', 'edit/insert-below'),
                ('Duplicate selected subtitles', 'edit/duplicate'),
                ('Delete selected subtitles', 'edit/delete'),
                None,
                ('Swap notes with subtitle text', 'edit/swap-text-and-notes'),
                ('Split at video frame', 'edit/split-sub-at-video'),
                # ('Split as karaoke', 'edit/split-karaoke'),  # TODO
                # ('Split as karaoke', 'edit/join-karaoke'),  # TODO
                ('Join (keep first)', 'edit/join-subs/keep-first'),
                ('Join (concatenate)', 'edit/join-subs/concatenate'),
                None,
                # ('Style editor', 'edit/style-editor'),  # TODO
            ]),
        ]

    def load(self, location):
        serializer = Serializer(location)
        hotkeys, menu, general = serializer.load()
        if hotkeys:
            self.hotkeys = hotkeys
        if menu:
            self.menu = menu
        if general:
            self.general = general

    def save(self, location):
        serializer = Serializer(location)
        serializer.write(self.hotkeys, self.menu, self.general)
