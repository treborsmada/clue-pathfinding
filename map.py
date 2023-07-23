from PIL import Image, ImageDraw
import math
import numpy as np

img_cell_size = 5

class Map:
    def __init__(self, cells, walls):
        self.cells = np.asarray(cells)
        self.walls = np.asarray(walls)
        self.move_data = []
        self.heuristic_data = []
        self.bd_data = None
        self.radius = 20
        self.goals = []
        self.image = Image.new("RGBA", size=(len(cells)*(img_cell_size+1)-1, len(cells[0])*(img_cell_size+1)-1), color=(255, 255, 255, 255))

    @staticmethod
    def adj_positions(x, y):
        return [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1), (x, y - 1), (x - 1, y - 1), (x - 1, y),
                (x - 1, y + 1)]

    def create_image(self):
        cells = self.cells
        walls = self.walls
        goals = self.goals
        img = Image.new("RGBA", size=(len(cells)*(img_cell_size+1)-1, len(cells[0])*(img_cell_size+1)-1), color=(255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        for x in range(len(cells)):
            draw.line((((img_cell_size+1)*(x+1)-1,0),((img_cell_size+1)*(x+1)-1,img.size[1]-1)), fill=(0,0,0,255))
        for y in range(len(cells[0])):
            draw.line(((0, (img_cell_size+1)*(y+1)-1), (img.size[0]-1, (img_cell_size+1)*(y+1)-1)), fill=(0, 0, 0, 255))
        for x in range(len(cells)):
            for y in range(len(cells[0])):
                if cells[x][len(cells[0])-1-y]:
                    draw.rectangle(((x*(img_cell_size+1),y*(img_cell_size+1)), (x*(img_cell_size+1)+(img_cell_size-1),y*(img_cell_size+1)+(img_cell_size-1))), fill=(255, 0, 0, 255))
        for x in range(len(walls[0])-2):
            for y in range(len(walls[0][0])):
                if walls[0][x+1][len(walls[0][0])-y-1]:
                    draw.line((((x+1)*(img_cell_size+1)-1,y*(img_cell_size+1)-1),((x+1)*(img_cell_size+1)-1,y*(img_cell_size+1)+img_cell_size)),fill=(255, 0, 0, 255))
        for y in range(len(walls[1])-2):
            for x in range(len(walls[1][0])):
                if walls[1][len(walls[1])-y-2][x]:
                    draw.line(((x*(img_cell_size+1)-1,(y+1)*(img_cell_size+1)-1),(x*(img_cell_size+1)+img_cell_size,(y+1)*(img_cell_size+1)-1)),fill=(255, 0, 0, 255))
        for i in range(len(goals)):
            draw.rectangle(((goals[i][0] * (img_cell_size+1), (len(cells[0]) - goals[i][1] - 1) * (img_cell_size+1)), (goals[i][0] * (img_cell_size+1) + (img_cell_size-1),(len(cells[0]) - goals[i][1] - 1) * (img_cell_size+1) + (img_cell_size-1))), fill=(0, 255, 0, 255))
        self.image = img
        return img

    def color_tiles(self, tiles, color):
        cells = self.cells
        img = self.image
        draw = ImageDraw.Draw(img)
        for tile in tiles:
            draw.rectangle(((tile[0] * (img_cell_size+1), (len(cells[0]) - tile[1] - 1) * (img_cell_size+1)), (tile[0] * (img_cell_size+1) + (img_cell_size-1),(len(cells[0]) - tile[1] - 1) * (img_cell_size+1) + (img_cell_size-1))), fill=color)
        self.image = img

    # north clockwise
    def get_pos_walls(self, x, y):
        walls = self.walls
        cells = self.cells
        if x < 0 or x >= len(cells) or y < 0 or y >= len(cells[0]):
            return [True, True, True, True]
        return [walls[1][y+1][x], walls[0][x+1][y], walls[1][y][x], walls[0][x][y]]

    def set_goals(self, x):
        self.goals = x

    def set_radius(self, r):
        self.radius = r

    def is_blocked(self, x, y):
        return self.cells[x][y]

    # north clockwise
    def one_tile_movement(self, x, y):
        tiles = []
        north = self.get_pos_walls(x, y+1)
        east = self.get_pos_walls(x+1, y)
        south = self.get_pos_walls(x, y-1)
        west = self.get_pos_walls(x-1, y)
        # north
        if north[2]:
            tiles.append(False)
        else:
            tiles.append(True)
        # northeast
        if north[1] or north[2] or east[0] or east[3]:
            tiles.append(False)
        else:
            tiles.append(True)
        # east
        if east[3]:
            tiles.append(False)
        else:
            tiles.append(True)
        # southeast
        if south[0] or south[1] or east[2] or east[3]:
            tiles.append(False)
        else:
            tiles.append(True)
        # south
        if south[0]:
            tiles.append(False)
        else:
            tiles.append(True)
        # southwest
        if south[0] or south[3] or west[1] or west[2]:
            tiles.append(False)
        else:
            tiles.append(True)
        # west
        if west[1]:
            tiles.append(False)
        else:
            tiles.append(True)
        # northwest
        if north[2] or north[3] or west[0] or west[1]:
            tiles.append(False)
        else:
            tiles.append(True)
        return tiles

    def bd_range(self, x, y):
        if self.bd_data is not None:
            tiles = []
            info = self.bd_data[x][y]
            for i in range(21):
                for j in range(21):
                    if info & (2**(j + i*21)):
                        u = x - 10 + j
                        v = y + 10 - i
                        tiles.append((u, v))
            return tiles
        else:
            tiles = []
            self.bd_range_recursion(x, y, [1, 2, 0], tiles, (0, 0))
            self.bd_range_recursion(x, y, [3, 2, 4], tiles, (0, 0))
            self.bd_range_recursion(x, y, [5, 6, 4], tiles, (0, 0))
            self.bd_range_recursion(x, y, [7, 6, 0], tiles, (0, 0))
            return [*set(tiles)]

    def bd_range_recursion(self, x, y, prioritylist, tiles, dist):
        currmove = self.move_data[x][y]
        adj = Map.adj_positions(x, y)
        if free_direction(currmove, prioritylist[0]) and dist[0] < 10 and dist[1] < 10:
            next = adj[prioritylist[0]]
            tiles.append(next)
            temp = (x, y)
            tempmove = currmove
            for i in range(10-dist[0]):
                if free_direction(tempmove, prioritylist[1]):
                    temp = Map.adj_positions(temp[0], temp[1])[prioritylist[1]]
                    tiles.append(temp)
                    tempmove = self.move_data[temp[0]][temp[1]]
                else:
                    break
            temp = (x, y)
            tempmove = currmove
            for i in range(10-dist[1]):
                if free_direction(tempmove, prioritylist[2]):
                    temp = Map.adj_positions(temp[0], temp[1])[prioritylist[2]]
                    tiles.append(temp)
                    tempmove = self.move_data[temp[0]][temp[1]]
                else:
                    break
            dist = (dist[0]+1, dist[1]+1)
            self.bd_range_recursion(next[0], next[1], prioritylist, tiles, dist)
        elif free_direction(currmove, prioritylist[1]) and dist[0] < 10:
            next = adj[prioritylist[1]]
            tiles.append(next)
            temp = (x, y)
            tempmove = currmove
            for i in range(10 - dist[1]):
                if free_direction(tempmove, prioritylist[2]):
                    temp = Map.adj_positions(temp[0], temp[1])[prioritylist[2]]
                    tiles.append(temp)
                    tempmove = self.move_data[temp[0]][temp[1]]
                else:
                    break
            dist = (dist[0]+1, dist[1])
            self.bd_range_recursion(next[0], next[1], prioritylist, tiles, dist)
        elif free_direction(currmove, prioritylist[2]) and dist[1] < 10:
            next = adj[prioritylist[2]]
            tiles.append(next)
            dist = (dist[0], dist[1]+1)
            self.bd_range_recursion(next[0], next[1], prioritylist, tiles, dist)

    def dot_tiles(self, tiles):
        img = self.image
        draw = ImageDraw.Draw(img)
        for tile in tiles:
            draw.ellipse([((img_cell_size+1)*tile[0], img.size[1] - tile[1]*(img_cell_size+1) - img_cell_size), ((img_cell_size+1)*tile[0] + (img_cell_size-1), img.size[1] - 1 - tile[1]*(img_cell_size+1))], fill=(0, 0, 255, 255))
        self.image = img

    def arrow_tiles(self, tiles, directions):
        img = self.image
        draw = ImageDraw.Draw(img)
        for i in range(len(tiles)):
            if directions[i] == 0:
                offset = [0, -1, 1, 0, -1, 0]
                points = [((img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[0],
                           img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[1]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[2],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[3]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[4],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 1:
                offset = [1, -1, 0, -1, 1, 0]
                points = [((img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[0],
                           img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[1]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[2],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[3]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[4],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 2:
                offset = [1, 0, 0, -1, 0, 1]
                points = [((img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[0],
                           img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[1]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[2],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[3]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[4],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 3:
                offset = [1, 1, 1, 0, 0, 1]
                points = [((img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[0],
                           img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[1]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[2],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[3]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[4],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 4:
                offset = [0, 1, 1, 0, -1, 0]
                points = [((img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[0],
                           img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[1]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[2],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[3]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[4],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 5:
                offset = [-1, 1, 0, 1, -1, 0]
                points = [((img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[0],
                           img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[1]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[2],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[3]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[4],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 6:
                offset = [-1, 0, 0, 1, 0, -1]
                points = [((img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[0],
                           img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[1]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[2],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[3]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[4],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
            if directions[i] == 7:
                offset = [-1, -1, -1, 0, 0, -1]
                points = [((img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[0],
                           img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[1]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[2],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[3]), (
                          (img_cell_size + 1) * tiles[i][0] + img_cell_size / 2 + offset[4],
                          img.size[1] - (img_cell_size + 1) * tiles[i][1] - img_cell_size / 2 + offset[5])]
                draw.point(points, fill=(0, 0, 255, 255))
        self.image = img

    def surge_range(self, x, y, direction):
        if direction == 0 or direction == 2 or direction == 4 or direction == 6:
            temp = (x, y)
            tempmove = self.move_data[temp[0]][temp[1]]
            for i in range(10):
                if free_direction(tempmove, direction):
                    temp = Map.adj_positions(temp[0], temp[1])[direction]
                    tempmove = self.move_data[temp[0]][temp[1]]
                else:
                    if temp == (x, y):
                        return None
                    return temp
            if temp == (x, y):
                return None
            return temp
        if direction == 1 or direction == 3 or direction == 5 or direction == 7:
            bd = self.bd_range(x, y)
            temp = (x, y)
            adj = Map.adj_positions(temp[0], temp[1])
            result = (x, y)
            for i in range(10):
                if adj[direction] in bd:
                    result = adj[direction]
                temp = adj[direction]
                adj = Map.adj_positions(temp[0], temp[1])
            if result == (x,y):
                return None
            return result

    # facing direction
    def escape_range(self, x, y, direction, weprange=8):
        direction = (direction + 4) % 8
        if direction == 0 or direction == 2 or direction == 4 or direction == 6:
            temp = (x, y)
            tempmove = self.move_data[temp[0]][temp[1]]
            for i in range(weprange-1):
                if free_direction(tempmove, direction):
                    temp = Map.adj_positions(temp[0], temp[1])[direction]
                    tempmove = self.move_data[temp[0]][temp[1]]
                else:
                    return temp
            return temp
        if direction == 1 or direction == 3 or direction == 5 or direction == 7:
            bd = self.bd_range(x, y)
            temp = (x, y)
            adj = Map.adj_positions(temp[0], temp[1])
            result = (x, y)
            for i in range(weprange-1):
                if adj[direction] in bd:
                    result = adj[direction]
                temp = adj[direction]
                adj = Map.adj_positions(temp[0], temp[1])
            return result

    def one_tick_walk(self, x, y):
        tiles = []
        start = self.move_data[x][y]
        adj = Map.adj_positions(x, y)
        for i in range(8):
            if free_direction(start, i):
                tiles.append(adj[i])
                temp = self.move_data[adj[i][0]][adj[i][1]]
                tempadj = Map.adj_positions(adj[i][0], adj[i][1])
                for j in range(8):
                    if free_direction(temp, j):
                        tiles.append(tempadj[j])
        tiles = [*set(tiles)]
        tiles.remove((x, y))
        return tiles

    def one_tick_walk_dir(self, x, y):
        tiles = []
        directions = []
        start = self.move_data[x][y]
        adj = Map.adj_positions(x, y)
        visited = {(x, y)}
        queue = []
        for i in range(8):
            j = (2*i + math.floor(i/4)) % 8
            if free_direction(start, j):
                tiles.append(adj[j])
                directions.append(j)
                visited.add(adj[j])
                queue.append(adj[j])
        while queue:
            current = queue.pop(0)
            move = self.move_data[current[0]][current[1]]
            tempadj = Map.adj_positions(current[0], current[1])
            for i in range(8):
                if free_direction(move, i):
                    if tempadj[i] not in visited:
                        tiles.append(tempadj[i])
                        directions.append(i)
                        visited.add(tempadj[i])
        return tiles, directions

    def one_tile_walk(self, x, y):
        tiles = []
        move = self.move_data[x][y]
        adj = Map.adj_positions(x, y)
        for i in range(8):
            j = (2*i + math.floor(i/4)) % 8
            if free_direction(move, j):
                tiles.append(adj[j])
        return tiles

    def bd_range_dir(self, x, y):
        tiles = self.bd_range(x, y)
        directions = []
        for tile in tiles:
            x_diff = tile[0]-x
            y_diff = tile[1]-y
            if x_diff == 0:
                if y_diff > 0:
                    directions.append(0)
                else:
                    directions.append(4)
            elif y_diff == 0:
                if x_diff > 0:
                    directions.append(2)
                else:
                    directions.append(6)
            elif (abs(x_diff)+0.5)/(abs(y_diff)+0.5) > 7.5/3.5:
                if x_diff > 0:
                    directions.append(2)
                else:
                    directions.append(6)
            elif (abs(y_diff)+0.5)/(abs(x_diff)+0.5) > 7.5/3.5:
                if y_diff > 0:
                    directions.append(0)
                else:
                    directions.append(4)
            elif x_diff > 0:
                if y_diff > 0:
                    directions.append(1)
                else:
                    directions.append(3)
            elif x_diff < 0:
                if y_diff > 0:
                    directions.append(7)
                else:
                    directions.append(5)
        return tiles, directions

    def get_pulse(self, x, y):
        single = []
        double = []
        triple = []
        goals = self.goals
        for i in range(len(goals)):
            if abs(goals[i][0] - x) <= self.radius and abs(goals[i][1] - y) <= self.radius:
                triple.append(i)
            elif abs(goals[i][0] - x) <= self.radius*2 and abs(goals[i][1] - y) <= self.radius*2:
                double.append(i)
            else:
                single.append(i)
        return [single, double, triple]

    def process_move_data(self):
        move_data = []
        cells = self.cells
        for x in range(len(cells)):
            column = []
            for y in range(len(cells[0])):
                adj = self.one_tile_movement(x, y)
                data = 0
                for i in range(len(adj)):
                    if adj[i]:
                        data += 2**i
                column.append(data)
            move_data.append(column)
        self.move_data = np.asarray(move_data)

    def process_heuristic_data(self, goal):
        heuristic_data = np.zeros(self.cells.shape) - 1
        heuristic_data[goal[0]][goal[1]] = 0
        visited = {goal}
        queue = [goal]
        while queue:
            node = queue.pop(0)
            adj = self.one_tick_walk_dir(node[0], node[1])[0]
            for tile in adj:
                if tile not in visited:
                    heuristic_data[tile[0]][tile[1]] = heuristic_data[node[0]][node[1]] + 1
                    queue.append(tile)
                    visited.add(tile)
        self.heuristic_data = heuristic_data

    def process_bd_data(self):
        bd_data = np.zeros(self.cells.shape, dtype=object)
        length, height = self.cells.shape
        for x in range(length):
            for y in range(height):
                bd = self.bd_range(x, y)
                info = 0
                for i in range(21):
                    for j in range(21):
                        u = x + j - 10
                        v = y - i + 10
                        if u >= 0 and v >= 0 and u < length and v < height:
                            if (u,v) in bd:
                                info += 2**(j + i*21)
                bd_data[x][y] = info
        self.bd_data = bd_data




def free_direction(i, direction):
        t = [1, 2, 4, 8, 16, 32, 64, 128]
        return math.floor(i/t[direction]) % 2 != 0


def combine_base_images(name):
    img = Image.new("RGBA", size=(768, 768))
    for y in range(3):
        for x in range(3):
            img.paste(Image.open(
                "Images/0_" + str(49 + x) + "_" + str(54 - y) + ".png"),
                      (0 + x * 256, 0 + y * 256))

    img.save("Images/"+name+"Map.png")

def get_pix(img, x, y):
    return img.getpixel((x, img.size[1] - 1 - y))

def create_map(scanName):
    img = Image.open("Images/"+scanName+"Map.png")
    cells = []
    walls = []
    for x in range(int(img.size[0]/4)):
        column = []
        for y in range(int(img.size[1]/4)):
            center = get_pix(img, x*4+1, y*4+1)[3]
            if center > 100:
                column.append(True)
            else:
                column.append(False)
        cells.append(column)
    #vertical walls
    vwalls = []
    column = []
    for y in range(int(img.size[1] / 4)):
        # west = get_pix(img, 0, y * 4 + 1)[3]
        column.append(True)
    vwalls.append(column)
    for x in range(int(img.size[0] / 4) -1):
        column = []
        for y in range(int(img.size[1] / 4)):
            east = get_pix(img, x * 4 + 3, y * 4 + 1)[3]
            west = get_pix(img, (x+1) * 4, y * 4 + 1)[3]
            if (east > 100) or (west > 100):
                column.append(True)
            else:
                column.append(False)
        vwalls.append(column)
    column = []
    for y in range(int(img.size[1] / 4)):
        # east = get_pix(img, img.size[0] - 1, y * 4 + 1)[3]
        column.append(True)
    vwalls.append(column)
    # horizontal walls
    hwalls = []
    row = []
    for x in range(int(img.size[0] / 4)):
        # south = get_pix(img, x * 4 + 1, 0)[3]
        row.append(True)
    hwalls.append(row)
    for y in range(int(img.size[1] / 4) - 1):
        row = []
        for x in range(int(img.size[0] / 4)):
            north = get_pix(img, x * 4 + 1, y * 4 + 3)[3]
            south = get_pix(img, x * 4 + 1, (y+1) * 4)[3]
            if (north > 100) or (south > 100):
                row.append(True)
            else:
                row.append(False)
        hwalls.append(row)
    row = []
    for x in range(int(img.size[0] / 4)):
        # north = get_pix(img, x * 4 + 1, img.size[1]-1)[3]
        row.append(True)
    hwalls.append(row)
    walls.append(vwalls)
    walls.append(hwalls)
    return Map(cells, walls)

def create_blank_grid(size):
    cells = []
    for i in range(size):
        column = []
        for j in range(size):
            column.append(False)
        cells.append(column)
    walls = []
    vwalls = []
    hwalls = []
    for i in range(size+1):
        column = []
        for j in range(size):
            column.append(False)
        vwalls.append(column)
    for i in range(size+1):
        row = []
        for j in range(size):
            row.append(False)
        hwalls.append(row)
    walls.append(vwalls)
    walls.append(hwalls)
    return Map(cells, walls)

