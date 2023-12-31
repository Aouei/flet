import flet
import pandas as pd

from dataclasses import dataclass
from flet import Page, UserControl, Row, Column, Image, Slider, Audio, IconButton, ListView, Text


@dataclass
class Song:
    title : str
    image : str
    src : str


ICONS_PATH = r'C:\Users\sergi\Documents\repos\flet\course\playlist_player\assets\icons'

PLAY_ICON_PATH = rf'{ICONS_PATH}\play.png'
PAUSE_ICON_PATH = rf'{ICONS_PATH}\pause.png'
PREVIOUS_ICON_PATH = rf'{ICONS_PATH}\previous.png'
NEXT_ICON_PATH = rf'{ICONS_PATH}\next.png'
RANDOM_ICON_PATH = rf'{ICONS_PATH}\shuffle.png'
LOOP_ONE_ICON_PATH = rf'{ICONS_PATH}\replay.png'
LOOP_ALL_ICON_PATH = rf'{ICONS_PATH}\repeat.png'

SONGS = pd.read_csv(r'C:\Users\sergi\Documents\repos\flet\course\playlist_player\assets\music.csv', index_col=0)


class SongPlayer(UserControl):
    def __init__(self, audio : Audio, song : Song):
        super().__init__()

        self.audio : Audio = audio
        self.song : Song = song

        self.current_state : str | None = None
        self.playing : bool = False

        self.title : Text = Text(self.song.title, style = flet.TextThemeStyle.TITLE_MEDIUM)
        self.cover : Image = Image(self.song.image, width = 256)
        self.duration : Slider = Slider(disabled = True)
        self.play_buttom : IconButton = IconButton(content=Image(PLAY_ICON_PATH), width = 40, height = 40)
        self.pause_buttom : IconButton = IconButton(content=Image(PAUSE_ICON_PATH), width = 40, height = 40, visible = False)
        self.previous_buttom : IconButton = IconButton(content=Image(PREVIOUS_ICON_PATH), width = 40, height = 40)
        self.next_buttom : IconButton = IconButton(content=Image(NEXT_ICON_PATH), width = 40, height = 40)

    def play(self, event):
        pass

    def pause(self, event):
        pass

    def update_duration(self, event):
        pass

    def step_to_milisecond(self, event):
        pass

    def next_song(self, event):
        pass

    def previous_song(self, event):
        pass

    def build(self):
        return Column([
            self.title,
            self.cover,
            self.duration,
            Row([self.previous_buttom,
                 self.play_buttom,
                 self.pause_buttom,
                 self.next_buttom], alignment = 'center')
        ], horizontal_alignment = 'center', width = 768)


class PlaylistPlayer(UserControl):
    def __init__(self, audio : Audio, songs : pd.DataFrame):
        super().__init__()

        self.songs : pd.DataFrame = songs
        self.audio : Audio = audio

        self.current_song_index = 0

    def _get_song(self) -> Song:
        return Song(**self.songs.iloc[self.current_song_index].to_dict())

    def build(self):
        return Row([SongPlayer(self.audio, self._get_song()), ListView(width = 256)])


def main(page : Page):
    audio = Audio(src = 'https://luan.xyz/files/audio/ambient_c_motion.mp3')
    page.overlay.append(audio)
    
    page.title = 'Playlist Player'
    page.window_width = 1024
    page.window_height = 512
    page.window_resizable = False
    page.window_left = 128
    page.window_top = 64

    page.vertical_alignment = 'center'

    page.add(PlaylistPlayer(audio, SONGS))


flet.app(target = main)