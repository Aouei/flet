import flet

from flet import Column, Page, TextField, Text, ElevatedButton


def main(page : Page) -> None:
    page.title = 'Greeter'
    page.bgcolor = flet.colors.AMBER_200
    page.window_min_width = 512
    page.window_width = 1024
    page.window_min_height = 160
    page.window_height = 512

    def on_keyboard(e):
        if e.key == 'Enter':
            handle_hello(e)

    page.on_keyboard_event = on_keyboard

    def handle_hello(e):
        if lbl_name.value != '':
            lbl_greeting.value = f'Hello {lbl_name.value}'
            lbl_name.value = ''
            lbl_greeting.visible = True
        else:
            lbl_greeting.value = ''
            lbl_greeting.visible = False
        
        page.update()

    lbl_name = TextField(value = '', label = 'Enter your name please', width = 256)
    lbl_greeting = Text(value = '', color = 'green', visible = False)
    btn_submit = ElevatedButton(text = 'Say Hello', on_click = handle_hello)

    page.add(Column([lbl_name, 
                     btn_submit,
                     lbl_greeting], spacing = 8))


flet.app(target = main)