import numpy as np
import matplotlib.pyplot as plt
import numpy as np

from typing import List, Tuple, Mapping
from enums import Direction


class Door:
    pass


class Room: # Create a Door Class
    def __init__(self, x : int, y : int, width : int, height : int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.walls : Mapping[str, List[Tuple[int, int]]] = {}
        self.doors : Mapping[str, List[Tuple[int, int]]] = {}
        self.ground : Mapping[str, List[Tuple[int, int]]] = {}
        self.tunnels : Mapping[str, List[Tuple[int, int]]] = {}

        for direction in Direction:
            self.set_door(direction, 0)

    @property
    def uuid(self):
        return f'({self.x},{self.y})'
    
    def set_door(self, direction : Direction, door_size : int) -> None:
        if direction == Direction.NORTH:
            self.doors[direction.value] = self.__get_door_frame(self.width - 1, door_size, y = 0)
        elif direction == Direction.SOUTH:
            self.doors[direction.value] = self.__get_door_frame(self.width - 1, door_size, y = self.height - 1)[::-1]
        elif direction == Direction.EAST:
            self.doors[direction.value] = self.__get_door_frame(self.height - 1, door_size, x = self.width - 1)
        elif direction == Direction.WEST:
            self.doors[direction.value] = self.__get_door_frame(self.height - 1, door_size, x = 0)[::-1]
    
    def close_door(self, direction : Direction) -> None:
        start_point = self.doors[direction.value][-1]
        end_point = self.doors[direction.value][0]

        sort_index = 1 if direction in [Direction.WEST, Direction.EAST] else 0
        self.doors[direction.value] = self.__join_points(start_point, end_point, [], sort_index = sort_index)

        if direction in [Direction.SOUTH, Direction.WEST]:
            self.doors[direction.value] = self.door_size[direction.value][::-1]

    def open_door(self, direction : Direction) -> None:
        self.doors[direction.value] = [self.doors[direction.value][0], self.doors[direction.value][-1]]

    def __get_door_frame(self, limits : int, door_size : int, x : int | None = None, y : int | None = None) -> List[Tuple[int, int]]:
        start = np.random.randint(door_size, limits - door_size)

        if x is None:
            points = [(start + self.x, y + self.y), (start + door_size + self.x, y + self.y)]
        else:
            points = [(x + self.x, start + self.y), (x + self.x, start + door_size + self.y)]
        
        return points

    def join_doors(self, start : Direction, end : Direction) -> None:
        start_point = self.doors[start.value][-1]
        end_point = self.doors[end.value][0]

        self.walls[start.value] = self.__join_points(start_point, end_point, [])

    def __join_points(self, start : Tuple, end : Tuple, list_to_save : List[Tuple], sort_index = None) -> None:
        x_diff = abs(end[0] - start[0]) + 1
        y_diff = abs(end[1] - start[1]) + 1
        x_dir = np.sign(end[0] - start[0])
        y_dir = np.sign(end[1] - start[1])

        list_to_save.extend([start, end])

        while x_dir or y_dir:
            x_offset = np.random.randint(low = 1, high = x_diff // 3) if x_diff // 3 > 1 else 1
            y_offset = np.random.randint(low = 1, high = y_diff // 3) if y_diff // 3 > 1 else 1

            for i in range(x_offset):
                start = (start[0] + x_dir, start[1])
                list_to_save.append(start)
            for i in range(y_offset):
                start = (start[0], start[1] + y_dir)
                list_to_save.append(start)

            x_diff = abs(end[0] - start[0]) + 1
            y_diff = abs(end[1] - start[1]) + 1
            x_dir = np.sign(end[0] - start[0])
            y_dir = np.sign(end[1] - start[1])
        
        list_to_save = list(set(list_to_save))

        if sort_index is not None:
            list_to_save.sort(key = lambda x: x[sort_index])
            
        return list_to_save

    def __unpack_directions(self, points_by_direction : Mapping[str, List[Tuple[int, int]]]) -> List[Tuple[int, int]]:
        points = []

        for direction in points_by_direction:
            points.extend(points_by_direction[direction])

        return list(set(points))
    
    def join_room(self, origin : Direction, destiny : List[Tuple[int, int]]) -> None:
        origin_start, origin_end = self.doors[origin.value][0], self.doors[origin.value][-1]
        destiny_start, destiny_end = destiny[0], destiny[-1]

        self.tunnels[origin.value] = self.__join_points(origin_start, destiny_end, []) + \
                                    self.__join_points(origin_end, destiny_start, [])
        
    def get_data(self) -> Mapping[str, List[Tuple[int, int]]]:
        points = {
            'doors' : self.__unpack_directions(self.doors),
            'walls' : self.__unpack_directions(self.walls),
            'tunnels' : self.__unpack_directions(self.tunnels),
        }

        return points


class MapBuilder:
    def __init__(self) -> None:
        self.rooms : Mapping[str, Room] = {}

    def create_room(self, x : int, y : int, width : int, height : int) -> str:
        room = Room(x, y, width, height)
        self.rooms[room.uuid] = room
        return room.uuid

    def create_room_walls(self, uuid : str) -> None:
        self.rooms[uuid].join_doors(Direction.NORTH, Direction.EAST)
        self.rooms[uuid].join_doors(Direction.EAST, Direction.SOUTH)
        self.rooms[uuid].join_doors(Direction.SOUTH, Direction.WEST)
        self.rooms[uuid].join_doors(Direction.WEST, Direction.NORTH)

    def open_room_door(self, uuid : str, direction : Direction) -> None:
        self.rooms[uuid].open_door(direction)

    def create_room_doors(self, uuid : str, doors : List[Direction], door_sizes : List[int]) -> None:
        for door, door_size in zip(doors, door_sizes):
            self.rooms[uuid].set_door(door, door_size)
        
        self.create_room_walls(uuid) # TODO: improve this
    
    def join_rooms(self, uuid_1 : str, uuid_2 : str, door_1 : Direction, door_2 : Direction):
        self.rooms[uuid_1].join_room(door_1, self.rooms[uuid_2].doors[door_2.value])
        
    def get_room_data(self, uuid : str) -> Mapping[str, List[Tuple[int, int]]]:
        return self.rooms[uuid].get_data()

    def get_room_uuids(self) -> List[str]:
        return list(self.rooms.keys())

    def plot_room(self, data, ax):
        for points in data.values():
            points = np.array(points)
        
            if len(points):
                ax.scatter(points[:, 0], points[:, 1], s = 5)
            
        return ax

    def plot_rooms(self, ax):
        for room in self.rooms:
            ax = self.plot_room(self.get_room_data(room), ax)
        
        return ax