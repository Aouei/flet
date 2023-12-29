import flet

from flet import Row, Page, TextField, IconButton, icons


def main(page : Page) -> None:
    page.title = 'Counter'
    page.window_min_width = 300
    page.window_width = 1024
    page.window_min_height = 128
    page.window_height = 512
    page.vertical_alignment = 'center'

    txt_number = TextField(value = '0', text_align = 'center', width = 100)

    def minus(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    page.add(Row(
        [
            IconButton(icons.REMOVE, on_click = minus),
            txt_number,
            IconButton(icons.ADD, on_click = plus),
        ],
        alignment = 'center'
    ))


flet.app(target = main)