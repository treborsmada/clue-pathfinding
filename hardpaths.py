from pathfinding import *
from map import *
from player import *

if __name__ == '__main__':

    map1 = create_map("Alkharid")
    map1.create_image()
    map1.color_tiles([(33, 48)], (255, 0, 255, 255))
    map1.color_tiles([(25, 67)], (255, 0, 255, 255))
    test_start = State(map1, (33, 48), 0, [0, 0, 0], 0)
    test_path = bfs_path_end_buffer(test_start, (25, 67), map1)
    tiles = []
    directions = []
    for tup in test_path[0]:
        for i in range(3):
            tiles.append(tup[i].pos)
            directions.append(tup[i].direction)
    print(test_path[1])
    map1.arrow_tiles(tiles, directions)
    map1.image.show()