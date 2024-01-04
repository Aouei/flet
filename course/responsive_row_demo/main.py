import flet

from flet import Page, Column, ResponsiveRow, Text, Container


def main(page: Page):
    page.add(ResponsiveRow([
        Container(col = {"lg": 6}, margin = 5, border_radius = 5, bgcolor = flet.colors.AMBER_200, content = Text('A'), alignment = flet.alignment.center),
        Container(col = {"lg": 6}, margin = 5, border_radius = 5, bgcolor = flet.colors.AMBER_200, content = Text('A'), alignment = flet.alignment.center)
    ]))


flet.app(target = main)