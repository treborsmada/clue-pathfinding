import time
from pathfinding import *
from map import *
from scaninfo import *
from Qlearning import *
from player import *

if __name__ == '__main__':

    varmap = create_map("varrock")
    varmap.set_goals(varrock_goals)
    varmap.create_image()

    '''cellstest = [[True, False, False], [False, True, False], [False, False, True]]
    wallstest = [[[True, False, False],[True, False, False],[True, False, False],[True, False, False]],[[False, True, False],[False, True, False],[False, True, False],[False, True, False]]]
    maptest = Map(cellstest,wallstest)
    maptest.create_image().show()
    '''
    # testmap = create_blank_grid(31)
    # testmap.create_image()


    # teststate = State(varmap, (0,0), 1, [0, 0, 0], 0)
    # newstate = State(varmap, (0,0), 1, [0, 0, 0], 0)
    # testset = {teststate}
    # print(newstate in testset)
    # print(teststate.secd)
    # print(teststate.bdcd)
    # print(newstate.secd)
    # print(newstate.bdcd)
    # print(newstate.pos)
    # st = time.time()
    varmap.color_tiles([(76, 106)], (255, 0, 255, 255))
    test_state = Gamestate(varmap, (76, 106), 0, [0, 0, 0], 0, None, 0, 0)
    test_state = test_state.update_pulse(3)
    print(test_state.available_goals)
    # test_start = State(varmap, (76, 106), 0, [0, 0, 0], 0)
    # test_path = bfs_path(test_start, (95, 111), varmap)
    # tiles = []
    # directions = []
    # for tup in test_path[0]:
    #     for i in range(3):
    #         tiles.append(tup[i].pos)
    #         directions.append(tup[i].direction)
    # # print(test)
    # et = time.time()
    # print(et - st)
    # print(test_path[1])
    # varmap.arrow_tiles(tiles, directions)
    varmap.image.show()


