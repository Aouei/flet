import flet
import pandas as pd
import moviepy.editor as mp
import numpy as np
import hashlib
import os

from typing import List
from enum import Enum
from pytube import YouTube
from dataclasses import dataclass
from flet import Page, UserControl, Row, Column, Image, Slider, Audio, IconButton, ListView, ListTile, Text, PubSub


@dataclass(slots = True)
class Song:
    title : str
    image : str
    src : str


class Actions(Enum):
    NEXT_SONG : str = 'next'
    PREV_SONG : str = 'previous'
    SEEK : str = 'seek'


class States(Enum):
    COMPLETED : str = 'completed'


ICONS_PATH = r'C:\Users\sergi\Documents\repos\flet\course\playlist_player\assets\icons'
SONGS_PATH = r'C:\Users\sergi\Documents\repos\flet\course\playlist_player\assets\songs'
SONGS_DATABASE_PATH = r'C:\Users\sergi\Documents\repos\flet\course\playlist_player\assets\music.csv'

PLAY_ICON_PATH = rf'{ICONS_PATH}\play.png'
PAUSE_ICON_PATH = rf'{ICONS_PATH}\pause.png'
PREVIOUS_ICON_PATH = rf'{ICONS_PATH}\previous.png'
NEXT_ICON_PATH = rf'{ICONS_PATH}\next.png'
RANDOM_ICON_PATH = rf'{ICONS_PATH}\shuffle.png'
RANDOM_SELECTED_ICON_PATH = rf'{ICONS_PATH}\shuffle_selected.gif'
LOOP_ONE_ICON_PATH = rf'{ICONS_PATH}\replay.png'
LOOP_ONE_SELECTED_ICON_PATH = rf'{ICONS_PATH}\replay_selected.gif'
LOOP_ALL_ICON_PATH = rf'{ICONS_PATH}\repeat.png'
LOOP_ALL_SELECTED_ICON_PATH = rf'{ICONS_PATH}\repeat_selected.gif'

SONGS : List[Song] = [ Song(**row) for _, row in pd.read_csv(SONGS_DATABASE_PATH, index_col = 0).iterrows() ]

class SongPlayer(UserControl):
    def __init__(self, pubsub : PubSub, song : Song):
        super().__init__()

        self.song : Song = song
        self.pubsub : PubSub = pubsub
        self.audio : Audio = Audio(src = self.song.src)
        self.audio.on_state_changed = self._set_state

        self.current_state : str | None = None
        self.playing : bool = False

        self.title : Text = Text(self.song.title, style = flet.TextThemeStyle.TITLE_MEDIUM)
        self.cover : Image = Image(self.song.image, width = 256, border_radius = flet.border_radius.all(10))
        self.duration : Slider = Slider(disabled = True, on_change = self.step_to_milisecond)
        self.play_button : IconButton = IconButton(content = Image(PLAY_ICON_PATH), width = 40, 
                                                   height = 40, on_click = self.play)
        self.pause_button : IconButton = IconButton(content=Image(PAUSE_ICON_PATH), width = 40, 
                                                    height = 40, visible = False, on_click = self.pause)
        self.previous_button : IconButton = IconButton(content=Image(PREVIOUS_ICON_PATH), width = 40, 
                                                       height = 40, on_click = self.previous_song)
        self.next_button : IconButton = IconButton(content=Image(NEXT_ICON_PATH), width = 40, 
                                                   height = 40, on_click = self.next_song)

    def _set_state(self, event):
        self.current_state = event.data

        if event.data == 'completed':
            self.pubsub.send_all_on_topic(States.COMPLETED, '')

    def _load_song(self):
        hash_code = hashlib.sha256(self.song.title.encode('utf-8')).hexdigest()    
        mp3_file = os.path.join(SONGS_PATH, f'{hash_code}.mp3')

        if not os.path.exists(mp3_file):
            stream = YouTube(self.song.src).streams.filter(file_extension = 'mp4').first()
            result = stream.download(output_path = SONGS_PATH, filename = f'{hash_code}.mp4')

            if not result == '':
                clip = mp.VideoFileClip(result)
                clip.audio.write_audiofile(mp3_file)

        return mp3_file

    def _set_duration_slider(self, event):
        self.audio.on_position_changed = self.update_duration
        self.duration.disabled = False
        self.duration.max = self.audio.get_duration()
        self.update()

    def set_song(self, song : Song):
        self.audio.on_position_changed = None
        self.song : Song = song
        
        self.title.value = song.title
        self.cover.src = song.image

        self.audio.release()
        self.duration.disabled = True
        self.duration.value = 0
        
        self.play_button.on_click = self.play
        self.play_button.visible = True
        self.pause_button.visible = False
        self.update()

    def play(self, event):
        mp3_file = self._load_song()
        
        if mp3_file:
            self.audio.on_loaded = self._set_duration_slider
            self.audio.src = mp3_file
            self.audio.play()
            self.play_button.visible = False
            self.pause_button.visible = True
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
        self.pubsub.send_all_on_topic(Actions.NEXT_SONG, '')

    def previous_song(self, event):
        self.pubsub.send_all_on_topic(Actions.PREV_SONG, '')

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
        ], horizontal_alignment = 'center', width = 512 + 128)


class PlaylistPlayer(UserControl):
    def __init__(self, pubsub : PubSub, songs : List[Song]):
        super().__init__()

        self.songs : List[Song] = songs
        self.pubsub : PubSub = pubsub
        self.current_song_index = 0
        self.indexes : np.array = np.arange(len(self.songs))
        np.random.shuffle(self.indexes)

        self.song_player : SongPlayer = SongPlayer(self.pubsub, self._get_song())

        self.title : str = 'Demo Playlist'
        self.pubsub : PubSub = pubsub

        self.random_button : IconButton = IconButton(content = Image(RANDOM_ICON_PATH), width = 40, 
                                                    height = 40, on_click = self.random_action)
        self.loop_current_button : IconButton = IconButton(content = Image(LOOP_ONE_ICON_PATH), width = 40, 
                                                       height = 40, on_click = self.loop_current_action)
        self.loop_all_button : IconButton = IconButton(content = Image(LOOP_ALL_ICON_PATH), width = 40, 
                                                   height = 40, on_click = self.loop_all_action)
        self.songs_list = ListView( [ListTile(leading = Image(src = song.image, width = 64, height = 64, border_radius = flet.border_radius.all(10)),
                                              title = Text(song.title, size = 12, weight = 'bold', no_wrap = False), 
                                              selected = idx == self.current_song_index, 
                                              key = idx, on_click = lambda event : self.select_song(event.control.key)) 
                                              for idx, song in enumerate(self.songs)], height = 512 - 128 - 16, spacing = 8 )

        self.playlist = Column(controls = [
            Text(self.title, style = flet.TextThemeStyle.TITLE_MEDIUM),
            Row([self.random_button, self.loop_current_button, self.loop_all_button]),
            self.songs_list
        ], width = 256 + 128 - 64)

        self.pubsub.subscribe_topic(Actions.NEXT_SONG, self._change_song)
        self.pubsub.subscribe_topic(Actions.PREV_SONG, self._change_song)
        self.pubsub.subscribe_topic(States.COMPLETED, self._finished_song)

    def select_song(self, song_index : int):
        self.songs_list.controls[self.current_song_index].selected = False
        self.current_song_index = song_index
        self.songs_list.controls[self.current_song_index].selected = True
        self.song_player.set_song(self._get_song())
        self.update()

    def random_action(self, event):
        if event.control.selected:
            event.control.selected = False
            event.control.content = Image(RANDOM_ICON_PATH)
        else:
            event.control.content = Image(RANDOM_SELECTED_ICON_PATH)
            event.control.selected = True
        self.update()
    
    def loop_current_action(self, event):
        if event.control.selected:
            event.control.selected = False
            event.control.content = Image(LOOP_ONE_ICON_PATH)
        else:
            event.control.content = Image(LOOP_ONE_SELECTED_ICON_PATH)
            event.control.selected = True
            self.loop_all_button.content = Image(LOOP_ALL_ICON_PATH)
            self.loop_all_button.selected = False
        self.update()
    
    def loop_all_action(self, event):
        if event.control.selected:
            event.control.selected = False
            event.control.content = Image(LOOP_ALL_ICON_PATH)
        else:
            event.control.content = Image(LOOP_ALL_SELECTED_ICON_PATH)
            event.control.selected = True
            self.loop_current_button.content = Image(LOOP_ONE_ICON_PATH)
            self.loop_current_button.selected = False
        self.update()

    def _finished_song(self, topic : States, message):
        if self.loop_current_button.selected:
            self.song_player.play(None)
        elif self.loop_all_button.selected or self.current_song_index != len(self.songs):
            self._change_song(Actions.NEXT_SONG, '')

    def _change_song(self, topic : Actions, message):
        direction : int = 1 if topic == Actions.NEXT_SONG else - 1

        if self.random_button.selected:
            self.select_song(self.indexes[(self.current_song_index + direction) % len(self.songs)])
        else:
            self.select_song((self.current_song_index + direction) % len(self.songs))
        self.song_player.set_song(self._get_song())

        if self.song_player.current_state != 'pause':
            self.song_player.play(None)
        
        self.update()

    def _get_song(self) -> Song:
        return self.songs[self.current_song_index]

    def build(self):
        return Row([self.song_player, self.playlist], wrap = True)


def main(page : Page):    
    page.title = 'Playlist Player'
    page.window_width = 1024
    page.window_height = 512
    page.window_resizable = False
    page.window_left = 128
    page.window_top = 64
    page.scroll = 'always'

    page.add(PlaylistPlayer(page.pubsub, SONGS))


flet.app(target = main)