from pathfinding import *
from map import *
from player import *
import time
import numpy as np

if __name__ == '__main__':

    """
    Map Name: file should be named name + "Map.png"
    """
    name = "PiscNorth"
    map1 = create_map(name)
    map1.create_image()

    """
    Starting State and Goal Location 
    
    surge_escape_cd is the cooldown of the first charge of both surge and escape (this should be set to the same number 
    as either second_surge_cd or second_escape_cd). To make the path only use one surge set both surge_escape_cd and 
    second_escape_cd to a high number (similarly for one escape). To make the path only use one surge or one escape set 
    both second_escape_cd and second_surge_cd to a high number 
    
    direction is a number 0 through 7 where 0 is north and each subsequent number is a rotation of 45 degrees clockwise.
    Generally set direction to be not facing the assumed path to the end location, so as not to allow surges on the 
    first tick in a direction you won't be facing in practice
    """
    start = (104, 46)
    end = (97, 91)
    direction = 0
    surge_escape_cd = 0
    second_surge_cd = 0
    second_escape_cd = 0
    bladed_dive_cd = 0

    """
    Shortcuts
    
    Shortcuts are one-way currently
    
    a - the tile the player is standing on before taking the shortcut
    b - the tile the player is standing on after taking the shortcut
    direction - direction the player is facing after taking the shortcut
    time - time the shortcut takes in ticks
    mandatory - True if the shortcut has to be a part of the path (theres no other way to reach the end location)
                False (work in progress)
    """
    map1.add_shortcut(a=(104, 66), b=(104, 71), direction=0, time=1, mandatory=True)
    map1.add_shortcut(a=(104, 78), b=(104, 79), direction=4, time=1, mandatory=True)
    map1.add_shortcut(a=(103, 78), b=(103, 79), direction=4, time=1, mandatory=True)

    """
    Heuristic for A*
    Generally just use l_inifity_cds 
    
    l_infinity - L∞ norm
                 Fast, suboptimal
    
    l_inifity_cds - L∞ norm but subtracting max distance movement abilities based on cooldowns
                    Slower, optimal
    
    walk_dist_cds - walking distance but subtracting movement abilities based on cooldowns
                    Slower, suboptimal (might change), should work better for very roundabout paths
                    
    uncommenting last line on long paths might speed up the algorithm
    """
    heuristic = l_infinity_cds
    map1.process_move_data()
    map1.process_heuristic_data(end)
    map1.process_bd_data()

    """
    Shouldn't need to change
    """
    map1.color_tiles([start, end], (255, 0, 255, 255))
    test_start = State(map1, start, direction, [surge_escape_cd, second_surge_cd, second_escape_cd], bladed_dive_cd)
    st = time.time()

    test_path = a_star_end_buffer(test_start, end, map1, heuristic)
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

    """
    test stuff
    """
    # for x in range(map1.heuristic_data.shape[0]):
    #     for y in range(map1.heuristic_data.shape[1]):
    #         if map1.heuristic_data[x][y] != -1:
    #             map1.color_tiles([(x, y)], (0, 255, 0, (int(map1.heuristic_data[x][y]))*20))