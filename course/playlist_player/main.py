import flet
import pandas as pd
import moviepy.editor as mp

from pytube import YouTube
from dataclasses import dataclass
from flet import Page, UserControl, Row, Column, Image, Slider, Audio, IconButton, ListView, Text, PubSub


@dataclass
class Song:
    title : str
    image : str
    src : str


ICONS_PATH = r'C:\Users\sergi\Documents\repos\flet\course\playlist_player\assets\icons'
SONGS_PATH = r'C:\Users\sergi\Documents\repos\flet\course\playlist_player\assets\songs'

PLAY_ICON_PATH = rf'{ICONS_PATH}\play.png'
PAUSE_ICON_PATH = rf'{ICONS_PATH}\pause.png'
PREVIOUS_ICON_PATH = rf'{ICONS_PATH}\previous.png'
NEXT_ICON_PATH = rf'{ICONS_PATH}\next.png'
RANDOM_ICON_PATH = rf'{ICONS_PATH}\shuffle.png'
LOOP_ONE_ICON_PATH = rf'{ICONS_PATH}\replay.png'
LOOP_ALL_ICON_PATH = rf'{ICONS_PATH}\repeat.png'

SONGS = pd.read_csv(r'C:\Users\sergi\Documents\repos\flet\course\playlist_player\assets\music.csv', index_col=0)


class SongPlayer(UserControl):
    def __init__(self, pubsub : PubSub, song : Song):
        super().__init__()

        self.song : Song = song
        self.pubsub : PubSub = pubsub
        self.audio : Audio = Audio(src = self.song.src)

        self.current_state : str | None = None
        self.playing : bool = False

        self.title : Text = Text(self.song.title, style = flet.TextThemeStyle.TITLE_MEDIUM)
        self.cover : Image = Image(self.song.image, width = 256, border_radius = flet.border_radius.all(10))
        self.duration : Slider = Slider(disabled = True, on_change = self.step_to_milisecond)
        self.play_button : IconButton = IconButton(content = Image(PLAY_ICON_PATH), width = 40, 
                                                   height = 40, on_click = self.play)
        self.pause_button : IconButton = IconButton(content=Image(PAUSE_ICON_PATH), width = 40, 
                                                    height = 40, visible = False, on_click = self.pause)
        self.previous_button : IconButton = IconButton(content=Image(PREVIOUS_ICON_PATH), width = 40, height = 40)
        self.next_button : IconButton = IconButton(content=Image(NEXT_ICON_PATH), width = 40, height = 40)

    def _load_song(self):
        stream = YouTube(self.song.src).streams.filter(file_extension = 'mp4').first()
        result = stream.download(output_path = SONGS_PATH)
        mp3_file = ''

        if not result == '':
            clip = mp.VideoFileClip(result)
            mp3_file = result.replace('.mp4', '.mp3')
            clip.audio.write_audiofile(mp3_file)

        return mp3_file

    def _set_duration_slider(self, event):
        self.audio.on_duration_changed = self.update_duration
        self.duration.disabled = False
        self.duration.max = self.audio.get_duration()
        self.update()

    def play(self, event):
        mp3_file = self._load_song()
        
        if mp3_file:
            self.audio.on_loaded = self._set_duration_slider
            self.audio.src = mp3_file
            self.audio.play()
            self.play_button.visible = False
            self.pause_button.visible = True
            self.playing = True
            self.update()

    def resume(self, event):
        self.audio.resume()
        self.play_button.visible = False
        self.pause_button.visible = True
        self.update()

    def pause(self, event):
        self.audio.pause()
        self.play_button.on_click = self.resume
        self.play_button.visible = True
        self.pause_button.visible = False
        self.update()

    def update_duration(self, event):
        self.duration.value = self.audio.get_current_position()
        self.update()

    def step_to_milisecond(self, event):
        self.audio.seek(int(self.duration.value))
        self.update()

    def next_song(self, event):
        pass

    def previous_song(self, event):
        pass

    def build(self):
        return Column([
            self.audio,
            self.title,
            self.cover,
            self.duration,
            Row([self.previous_button,
                 self.play_button,
                 self.pause_button,
                 self.next_button], alignment = 'center')
        ], horizontal_alignment = 'center', width = 768)


class PlaylistPlayer(UserControl):
    def __init__(self, pubsub : PubSub, songs : pd.DataFrame):
        super().__init__()

        self.songs : pd.DataFrame = songs
        self.pubsub : PubSub = pubsub

        self.current_song_index = 0

    def _get_song(self) -> Song:
        return Song(**self.songs.iloc[self.current_song_index].to_dict())

    def build(self):
        return Row([SongPlayer(self.pubsub, self._get_song()), ListView(width = 256)])


def main(page : Page):    
    page.title = 'Playlist Player'
    page.window_width = 1024
    page.window_height = 512
    page.window_resizable = False
    page.window_left = 128
    page.window_top = 64

    page.vertical_alignment = 'center'

    page.add(PlaylistPlayer(page.pubsub, SONGS))


flet.app(target = main)