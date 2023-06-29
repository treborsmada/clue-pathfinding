from pathfinding import *
from map import *
from player import *
import time

if __name__ == '__main__':

    map1 = create_map("PiscNorth")
    map1.create_image()
    map1.color_tiles([(53, 39)], (255, 0, 255, 255))
    map1.color_tiles([(69, 84)], (255, 0, 255, 255))
    test_start = State(map1, (53, 39), 0, [0, 0, 0], 0)
    st = time.time()
    test_path = a_star_end_buffer(test_start, (69, 84), map1, l_infinity)
    et = time.time()
    tiles = []
    directions = []
    for tup in test_path[0]:
        for i in range(3):
            tiles.append(tup[i].pos)
            directions.append(tup[i].direction)
    print(test_path[1])
    print(et-st)
    map1.arrow_tiles(tiles, directions)
    map1.image.show()