import matplotlib
import matplotlib.pyplot as plt
import flet as ft

from flet import ElevatedButton, Row
from flet.matplotlib_chart import MatplotlibChart

from enums import Direction
from model import MapBuilder

matplotlib.use("svg")

def main(page: ft.Page):

    fig, ax = plt.subplots()
    
    plt.gca().invert_yaxis()

    game_map = MapBuilder()

    uuid_1 = game_map.create_room(0, 0, 32, 32)
    game_map.create_room_doors(uuid_1, [Direction.SOUTH], [10])
    game_map.create_room_walls(uuid_1)

    uuid_2 = game_map.create_room(30, 50, 32, 32)
    game_map.create_room_doors(uuid_2, [Direction.NORTH], [10])
    game_map.create_room_walls(uuid_2)

    uuid_3 = game_map.create_room(-50, 50, 32, 32)
    game_map.create_room_doors(uuid_3, [Direction.NORTH], [5])
    game_map.create_room_doors(uuid_3, [Direction.SOUTH], [15])
    game_map.create_room_walls(uuid_3)

    ax = game_map.plot_rooms(ax)

    page.add(MatplotlibChart(fig, expand = True), ElevatedButton('New Room'))


ft.app(target = main)