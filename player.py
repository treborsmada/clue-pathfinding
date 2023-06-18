from map import *

movelist = ["walk", "surge", "bd", "bd_surge", "surge_bd", "bd_escape", "escape_bd", "surge_walk", "bd_walk",
            "escape_walk"]

class Player:
    def __init__(self, map):
        self.map = map
        self.pos = -1
        self.ecd = (0, 0)
        self.scd = (0, 0)
        self.bdcd = 0
        self.direction = 0

    def set_pos(self, x, y):
        if not Map.is_blocked(self.map, x, y):
            self.pos = (x, y)
        else:
            raise Exception("Position blocked")

    def get_bd_tiles(self):
        if not self.pos == -1:
            return self.map.bd_range(self.pos[0], self.pos[1])
        else:
            return -1

    def get_surge_tile(self):
        if not self.pos == -1:
            return self.map.surge_range(self.pos[0], self.pos[1], self.direction)
        else:
            return -1

    def get_escape_tile(self):
        if not self.pos == -1:
            return self.map.escape_range(self.pos[0], self.pos[1], self.direction)
        else:
            return -1



