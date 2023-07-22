from pathfinding import *
from map import *
from player import *
import time
import numpy as np

if __name__ == '__main__':

    map1 = create_map("Braindeath")
    map1.create_image()
    map1.process_move_data()

    # for x in range(map1.heuristic_data.shape[0]):
    #     for y in range(map1.heuristic_data.shape[1]):
    #         if map1.heuristic_data[x][y] != -1:
    #             map1.color_tiles([(x, y)], (0, 255, 0, (int(map1.heuristic_data[x][y]))*20))
    start = (12, 26)
    end = (21, 42)
    map1.color_tiles([start, end], (255, 0, 255, 255))
    test_start = State(map1, start, 0, [0, 0, 0], 1)
    st = time.time()
    map1.process_heuristic_data(end)
    test_path = a_star_end_buffer(test_start, end, map1, walk_dist_cds)
    et = time.time()
    tiles = []
    directions = []
    for tup in test_path[0]:
        for i in range(3):
            tiles.append(tup[i].pos)
            directions.append(tup[i].direction)
    print(test_path[1])
    print("Ticks:" + str(len(test_path[1])))
    print(et-st)
    map1.arrow_tiles(tiles, directions)
    map1.image.show()