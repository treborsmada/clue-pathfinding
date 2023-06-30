from pathfinding import *
from map import *
from player import *
import time

if __name__ == '__main__':

    map1 = create_map("WestArdy")
    map1.create_image()
    map1.process_move_data()
    map1.color_tiles([(106, 42)], (255, 0, 255, 255))
    map1.color_tiles([(56, 44)], (255, 0, 255, 255))
    test_start = State(map1, (106, 42), 0, [0, 0, 0], 5)
    st = time.time()
    test_path = a_star_end_buffer(test_start, (56, 44), map1, l_infinity_cds)
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