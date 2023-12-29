import flet as ft
from flet import Page, UserControl, Slider, Image, Audio, Column, Row, IconButton


music_path = r'C:\Users\sergi\Documents\repos\flet\course\music_player\assets\En La Tormenta.mp3'
icon_path = r'C:\Users\sergi\Documents\repos\flet\course\music_player\assets\musica.png'


class Player(UserControl):
    def __init__(self, audio):
        super().__init__()

        self.audio : Audio = audio
        self.playing : bool = False
        self.audio.on_position_changed = self.update_slider
        self.audio.on_state_changed = self.rewind
        self.play_button : IconButton = IconButton(ft.icons.PLAY_ARROW_ROUNDED, on_click = self.play)
        self.pause_button : IconButton = IconButton(ft.icons.PAUSE, on_click = self.pause, visible = False)
        self.duration_slider : Slider = Slider(min = 0, value = 0, on_change = self.step_audio, disabled = True)

    def play(self, event):
        self.play_button.visible = False
        self.pause_button.visible = True

        if self.playing:
            self.audio.resume()
        else:
            self.playing = True
            self.audio.play()
            self.duration_slider.max = self.audio.get_duration()
            self.duration_slider.value = 0
            self.duration_slider.disabled = False

        self.update()

    def pause(self, event):
        self.play_button.visible = True
        self.pause_button.visible = False
        self.audio.pause()
        self.update()
        
    def update_slider(self, event):
        self.duration_slider.value = self.audio.get_current_position()
        self.update()

    def rewind(self, event):
        if event.data == 'completed':
            self.audio.play()
            self.duration_slider.max = self.audio.get_duration()
            self.duration_slider.value = 0
            self.update()

    def step_audio(self, event):
        self.audio.seek(int(self.duration_slider.value))
        self.update()

    def build(self):
        return Column([
            Image(icon_path, width = 128, height = 128),
            Row([self.play_button, self.pause_button, self.duration_slider], width = 256)
            ], horizontal_alignment='center', spacing=0)


def main(page: Page):
    page.title = 'Music Player'
    page.window_width = 1024
    page.window_height = 512
    page.window_resizable = False
    page.window_left = 128
    page.window_top = 64
    
    audio = Audio(src = music_path)
    page.overlay.append(audio)

    page.add(Player(audio))


ft.app(target = main)