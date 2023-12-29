import flet as ft
from flet import colors

def main(page: ft.Page):
    page.title = "Drag and Drop example"

    def drag_accept(e):
        # get draggable (source) control by its ID
        src = page.get_control(e.src_id)
        # update text inside draggable control
        aux = src.content.content.value
        src.content.content.value = e.control.content.content.value
        # update text inside drag target control
        e.control.content.content.value = aux
        unwill(e)
        
    def will(event):
        event.control.content.bgcolor = colors.AMBER_200
        event.control.content.border = ft.border.all(2, ft.colors.BLACK45)
        page.update()

    def unwill(event):
        event.control.content.bgcolor = colors.PINK_200
        event.control.content.border = None
        page.update()

    page.add(
        ft.Row(
            [
                ft.Draggable(
                    group="number",
                    content=ft.Container(
                        width=50,
                        height=50,
                        bgcolor=ft.colors.CYAN_200,
                        border_radius=5,
                        content=ft.Text("1", size=20),
                        alignment=ft.alignment.center,
                    ),
                ),
                ft.Container(width=100),
                ft.DragTarget(
                    group="number",
                    content=ft.Container(
                        width=50,
                        height=50,
                        bgcolor=ft.colors.PINK_200,
                        border_radius=5,
                        content=ft.Text("0", size=20),
                        alignment=ft.alignment.center,
                    ),
                    on_accept=drag_accept,
                    on_will_accept=will,
                    on_leave=unwill
                ),
            ]
        )
    )

ft.app(target=main)