import matplotlib
import matplotlib.pyplot as plt
import flet as ft

from flet import ElevatedButton, Row, Column, ResponsiveRow, UserControl, ListView, PubSub, Text, TextField, Dropdown, dropdown
from flet.matplotlib_chart import MatplotlibChart

from enums import Direction
from model import MapBuilder

matplotlib.use("svg")

class MapManager(UserControl):
    def __init__(self, pubsub : PubSub):
        super().__init__()
        
        self.pubsub : PubSub = pubsub

        self.hab_list = HabList(self.pubsub)
        self.hab_list.col = 4
        
        self.fig, self.ax = plt.subplots()

        self.tile_map = MatplotlibChart(self.fig, col = 8)

        self.pubsub.subscribe(self.update_fig)

    def update_fig(self, game_map : MapBuilder):
        plt.cla()
        plt.gca().invert_yaxis()

        game_map.plot_rooms(self.ax)
        self.update()
    
    def build(self):
        return ResponsiveRow([self.hab_list, self.tile_map], expand = True)
        

class HabList(UserControl):
    def __init__(self, pubsub : PubSub):
        super().__init__()

        self.pubsub : PubSub = pubsub
        self.game_map = MapBuilder()

        self.hab_listview : ListView = ListView()
        self.x_offset : TextField = TextField(label = 'x', width = 64)
        self.y_offset : TextField = TextField(label = 'y', width = 64)
        self.w_offset : TextField = TextField(label = 'w', width = 64)
        self.h_offset : TextField = TextField(label = 'h', width = 64)

        self.directions : Dropdown = Dropdown(options = [dropdown.Option(direction.value, text = direction.name) for direction in Direction], width = 96)
        self.uuids : Dropdown = Dropdown(options = [], width = 96)

        self.uuids_1 : Dropdown = Dropdown(options = [], width = 96)
        self.uuids_2 : Dropdown = Dropdown(options = [], width = 96)
        self.directions_1 : Dropdown = Dropdown(options = [dropdown.Option(direction.value, text = direction.name) for direction in Direction], width = 96)
        self.directions_2 : Dropdown = Dropdown(options = [dropdown.Option(direction.value, text = direction.name) for direction in Direction], width = 96)

        self.buttons : Column = Column([
            Row([ElevatedButton('New Hab', on_click = self.new_hab), self.x_offset, self.y_offset, self.w_offset, self.h_offset]),
            Row([ElevatedButton('Open Door', on_click = self.open_door), self.uuids, self.directions]),
            Row([ElevatedButton('Join Rooms', on_click = self.join_rooms), self.uuids_1, self.directions_1, self.uuids_2, self.directions_2], wrap = True),
        ])

    def new_hab(self, event):
        if self.x_offset.value and self.y_offset.value and self.w_offset.value and self.h_offset.value:
            x = int(self.x_offset.value)
            y = int(self.y_offset.value)
            w = int(self.w_offset.value)
            h = int(self.h_offset.value)

            uuid = self.game_map.create_room(x, y, h, w)
            self.game_map.create_room_walls(uuid)
            
            self._update_layout()

    def rebuild_hab(self, event):
        uuid = event.control.data
        metadata = self.game_map.get_room_metadata(uuid)
        
        self.game_map.create_room_walls(self.game_map.create_room(**metadata))
        
        self._update_layout()
        
    def open_door(self, event):
        if self.uuids.value and self.directions.value:
            self.game_map.create_room_doors(self.uuids.value, [Direction(self.directions.value)], [10])
            self.pubsub.send_all(self.game_map)

    def join_rooms(self, event):
        if self.uuids_1.value and self.directions_1.value and self.uuids_2.value and self.directions_2.value:
            self.game_map.join_rooms(self.uuids_1.value, self.uuids_2.value, Direction(self.directions_1.value), Direction(self.directions_2.value))
            self.pubsub.send_all(self.game_map)

    def _update_layout(self):
        self.hab_listview.controls.clear()
        self.uuids.options.clear()
        self.uuids_1.options.clear()
        self.uuids_2.options.clear()
        
        for uuid in self.game_map.get_room_uuids():
            self.hab_listview.controls.append(Row([Text(str(uuid)), ElevatedButton('Reload', on_click = self.rebuild_hab, data = uuid )]))
            self.uuids.options.append(dropdown.Option(uuid, uuid))
            self.uuids_1.options.append(dropdown.Option(uuid, uuid))
            self.uuids_2.options.append(dropdown.Option(uuid, uuid))
        
        self.update()
        self.pubsub.send_all(self.game_map)

    def build(self):
        return Column([self.hab_listview, self.buttons])


def main(page: ft.Page):

    fig, ax = plt.subplots()
    plt.gca().invert_yaxis()

    page.add(MapManager(page.pubsub))

ft.app(target = main)