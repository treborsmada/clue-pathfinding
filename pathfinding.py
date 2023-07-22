from map import *
import queue as qqueue
from itertools import count

movelist = ["walk", "surge", "bd", "bd_surge", "surge_bd", "bd_escape", "escape_bd", "surge_walk", "bd_walk",
            "escape_walk"]

class State:
    def __init__(self, map, pos, direction, secd=[0, 0, 0], bdcd=0):
        self.map = map
        self.pos = pos
        self.direction = direction
        self.secd = secd.copy()
        self.bdcd = bdcd

    def __eq__(self, other):
        if isinstance(other, State):
            return self.map == other.map and self.pos == other.pos and self.direction == other.direction and self.secd == other.secd and self.bdcd == other.bdcd
        return False

    def __hash__(self):
        return hash((self.pos, self.direction, tuple(self.secd), self.bdcd))

    def update(self):
        new_secd = self.secd.copy()
        new_bdcd = self.bdcd
        for i in range(3):
            if not new_secd[i] == 0:
                new_secd[i] = new_secd[i]-1
        if not new_bdcd == 0:
            new_bdcd = new_bdcd - 1
        return State(self.map, self.pos, self.direction, new_secd, new_bdcd)

    def move(self, x, y, direction):
        return State(self.map, (x, y), direction, self.secd, self.bdcd)

    def surge(self):
        new_secd = self.secd.copy()
        if self.secd[0] == 0:
            new_pos = self.map.surge_range(self.pos[0], self.pos[1], self.direction)
            if new_pos == self.pos:
                return State(self.map, self.pos, self.direction, self.secd, self.bdcd)
            if self.secd[1] < 2:
                return State(self.map, new_pos, self.direction, [17, 2, 17], self.bdcd)
            else:
                return State(self.map, new_pos, self.direction, [17, new_secd[1], 17], self.bdcd)
        elif self.secd[1] == 0:
            new_pos = self.map.surge_range(self.pos[0], self.pos[1], self.direction)
            if new_pos == self.pos:
                return State(self.map, self.pos, self.direction, self.secd, self.bdcd)
            if self.secd[0] < 2:
                return State(self.map, new_pos, self.direction, [2, 17, 2], self.bdcd)
            else:
                return State(self.map, new_pos, self.direction, [new_secd[0], 17, new_secd[2]], self.bdcd)
        else:
            print(self.pos)
            raise Exception("Surge is on cooldown")

    def escape(self):
        new_secd = self.secd.copy()
        if self.secd[0] == 0:
            new_pos = self.map.escape_range(self.pos[0], self.pos[1], self.direction)
            if new_pos == self.pos:
                return State(self.map, self.pos, self.direction, self.secd, self.bdcd)
            if self.secd[2] < 2:
                return State(self.map, new_pos, self.direction, [17, 17, 2], self.bdcd)
            else:
                return State(self.map, new_pos, self.direction, [17, 17, new_secd[2]], self.bdcd)
        elif self.secd[2] == 0:
            new_pos = self.map.escape_range(self.pos[0], self.pos[1], self.direction)
            if new_pos == self.pos:
                return State(self.map, self.pos, self.direction, self.secd, self.bdcd)
            if self.secd[0] < 2:
                return State(self.map, new_pos, self.direction, [2, 2, 17], self.bdcd)
            else:
                return State(self.map, new_pos, self.direction, [new_secd[0], new_secd[1], 17], self.bdcd)
        else:
            print(self.pos)
            raise Exception("Escape is on cooldown")

    def bd(self, x, y, direction):
        if self.bdcd == 0:
            return State(self.map, (x, y), direction, self.secd, 17)

    def can_bd(self):
        return self.bdcd == 0

    def can_surge(self):
        return (self.secd[0] == 0 or self.secd[1] == 0) and self.map.surge_range(self.pos[0], self.pos[1], self.direction) is not None

    def can_escape(self):
        return self.secd[0] == 0 or self.secd[2] == 0

    def min_cd(self):
        cds = [(self.secd[0], "se"), (self.secd[1], "s"), (self.secd[2], "e"), (self.bdcd, "bd")]
        cds = sorted(cds, key=lambda tup: tup[0])
        return cds[0]

def walk_path(start, end, map):
    path = [start]
    if start == end:
        return path
    visited = {start}
    queue = [path]
    count = 0
    while queue:
        path = queue.pop(0)
        node = path[-1]
        adj = map.one_tick_walk_dir(node[0], node[1])[0]
        for tile in adj:
            if tile not in visited:
                new_path = list(path)
                new_path.append(tile)
                queue.append(new_path)
                visited.add(tile)
                if tile == end:
                    return new_path

def bfs_path(start_state, end, map):
    path = [(start_state, start_state, start_state)]
    path_moves = []
    if start_state.pos == end:
        return path
    visited_walk = {(start_state.pos, start_state.direction)}
    visited_state = {start_state}
    queue = [(path, path_moves)]
    first = True
    while queue:
        path = queue.pop(0)
        node = path[0][-1][-1]
        if not first:
            node = node.update()
        first = False
        if node.pos == end:
            return path
        #wait
        new_path = path[0].copy()
        new_path_moves = path[1].copy()
        new_path.append((node, node, node))
        new_path_moves.append("wait")
        visited_state.add(node)
        queue.append((new_path, new_path_moves))
        #walk
        walk_adj = map.one_tick_walk_dir(node.pos[0], node.pos[1])
        for i in range(len(walk_adj[0])):
            next1 = node.move(walk_adj[0][i][0], walk_adj[0][i][1], walk_adj[1][i])
            if (next1.pos, next1.direction) not in visited_walk:
                if next1 not in visited_state:
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next1))
                    new_path_moves.append("walk")
                    is_walk_path = True
                    for temp in new_path_moves:
                        if temp != "walk":
                            is_walk_path = False
                    if is_walk_path:
                        visited_walk.add((walk_adj[0][i], walk_adj[1][i]))
                    visited_state.add(next1)
                    queue.append((new_path, new_path_moves))
                    if next1.pos == end:
                        return new_path, new_path_moves
        #surge+bd+walk
        if node.can_surge():
            next1 = node.surge()
            if (next1.pos, next1.direction) not in visited_walk:
                if next1 not in visited_state:
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next1))
                    new_path_moves.append("surge")
                    visited_state.add(next1)
                    queue.append((new_path, new_path_moves))
                    if next1.pos == end:
                        return new_path, new_path_moves
            walk_adj = map.one_tick_walk_dir(next1.pos[0], next1.pos[1])
            for j in range(len(walk_adj[0])):
                next2 = next1.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                if (next2.pos, next2.direction) not in visited_walk:
                    if next2 not in visited_state:
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next1, next2))
                        new_path_moves.append("surge walk")
                        visited_state.add(next2)
                        queue.append((new_path, new_path_moves))
                        if next2.pos == end:
                            return new_path, new_path_moves
            if next1.can_bd():
                bd_adj = map.bd_range_dir(next1.pos[0], next1.pos[1])
                for i in range(len(bd_adj[0])):
                    next2 = next1.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("surge bd")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if next2.pos == end:
                                return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        if (next3.pos, next3.direction) not in visited_walk:
                            if next3 not in visited_state:
                                new_path = path[0].copy()
                                new_path_moves = path[1].copy()
                                new_path.append((next1, next2, next3))
                                new_path_moves.append("surge bd walk")
                                visited_state.add(next3)
                                queue.append((new_path, new_path_moves))
                                if next3.pos == end:
                                    return new_path, new_path_moves
        #bd+surge/escape+walk
        if node.can_bd():
            bd_adj = map.bd_range_dir(node.pos[0], node.pos[1])
            for i in range(len(bd_adj[0])):
                next1 = node.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                if (next1.pos, next1.direction) not in visited_walk:
                    if next1 not in visited_state:
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next1, next1))
                        new_path_moves.append("bd")
                        visited_state.add(next1)
                        queue.append((new_path, new_path_moves))
                        if next1.pos == end:
                            return new_path, new_path_moves
                walk_adj = map.one_tick_walk_dir(next1.pos[0], next1.pos[1])
                for j in range(len(walk_adj[0])):
                    next2 = next1.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("bd walk")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if next2.pos == end:
                                return new_path, new_path_moves
                if next1.can_surge():
                    next2 = next1.surge()
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("bd surge")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if next2.pos == end:
                                return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0],walk_adj[0][j][1], walk_adj[1][j])
                        if (next3.pos, next3.direction) not in visited_walk:
                            if next3 not in visited_state:
                                new_path = path[0].copy()
                                new_path_moves = path[1].copy()
                                new_path.append((next1, next2, next3))
                                new_path_moves.append("bd surge walk")
                                visited_state.add(next3)
                                queue.append((new_path, new_path_moves))
                                if next3.pos == end:
                                    return new_path, new_path_moves
                if next1.can_escape():
                    next2 = next1.escape()
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("bd escape")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if next2.pos == end:
                                return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        if (next3.pos, next3.direction) not in visited_walk:
                            if next3 not in visited_state:
                                new_path = path[0].copy()
                                new_path_moves = path[1].copy()
                                new_path.append((next1, next2, next3))
                                new_path_moves.append("bd escape walk")
                                visited_state.add(next3)
                                queue.append((new_path, new_path_moves))
                                if next3.pos == end:
                                    return new_path, new_path_moves
        #escape+bd+walk
        if node.can_escape():
            next1 = node.escape()
            if (next1.pos, next1.direction) not in visited_walk:
                if next1 not in visited_state:
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next1))
                    new_path_moves.append("escape")
                    visited_state.add(next1)
                    queue.append((new_path, new_path_moves))
                    if next1.pos == end:
                        return new_path, new_path_moves
            walk_adj = map.one_tick_walk_dir(next1.pos[0], next1.pos[1])
            for j in range(len(walk_adj[0])):
                next2 = next1.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                if (next2.pos, next2.direction) not in visited_walk:
                    if next2 not in visited_state:
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next1, next2))
                        new_path_moves.append("escape walk")
                        visited_state.add(next2)
                        queue.append((new_path, new_path_moves))
                        if next2.pos == end:
                            return new_path, new_path_moves
            if next1.can_bd():
                bd_adj = map.bd_range_dir(next1.pos[0], next1.pos[1])
                for i in range(len(bd_adj[0])):
                    next2 = next1.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("escape bd")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if next2.pos == end:
                                return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        if (next3.pos, next3.direction) not in visited_walk:
                            if next3 not in visited_state:
                                new_path = path[0].copy()
                                new_path_moves = path[1].copy()
                                new_path.append((next1, next2, next3))
                                new_path_moves.append("escape bd walk")
                                visited_state.add(next3)
                                queue.append((new_path, new_path_moves))
                                if next3.pos == end:
                                    return new_path, new_path_moves

def bfs_path_end_buffer(start_state, end, map):
    path = [(start_state, start_state, start_state)]
    path_moves = []
    if end[0]-1 <= start_state.pos[0] <= end[0]+1 and end[1]-1 <= start_state.pos[1] <= end[1]+1:
        return path
    visited_walk = {(start_state.pos, start_state.direction)}
    visited_state = {start_state}
    queue = [(path, path_moves)]
    first = True
    while queue:
        path = queue.pop(0)
        node = path[0][-1][-1]
        if not first:
            node = node.update()
        first = False
        if end[0]-1 <= node.pos[0] <= end[0]+1 and end[1]-1 <= node.pos[1] <= end[1]+1:
            return path
        #wait
        new_path = path[0].copy()
        new_path_moves = path[1].copy()
        new_path.append((node, node, node))
        new_path_moves.append("wait")
        visited_state.add(node)
        queue.append((new_path, new_path_moves))
        #walk
        walk_adj = map.one_tick_walk_dir(node.pos[0], node.pos[1])
        for i in range(len(walk_adj[0])):
            next1 = node.move(walk_adj[0][i][0], walk_adj[0][i][1], walk_adj[1][i])
            if (next1.pos, next1.direction) not in visited_walk:
                if next1 not in visited_state:
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next1))
                    new_path_moves.append("walk")
                    is_walk_path = True
                    for temp in new_path_moves:
                        if temp != "walk":
                            is_walk_path = False
                    if is_walk_path:
                        visited_walk.add((walk_adj[0][i], walk_adj[1][i]))
                    visited_state.add(next1)
                    queue.append((new_path, new_path_moves))
                    if end[0]-1 <= next1.pos[0] <= end[0]+1 and end[1]-1 <= next1.pos[1] <= end[1]+1:
                        return new_path, new_path_moves
        #surge+bd+walk
        if node.can_surge():
            next1 = node.surge()
            if (next1.pos, next1.direction) not in visited_walk:
                if next1 not in visited_state:
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next1))
                    new_path_moves.append("surge")
                    visited_state.add(next1)
                    queue.append((new_path, new_path_moves))
                    if end[0]-1 <= next1.pos[0] <= end[0]+1 and end[1]-1 <= next1.pos[1] <= end[1]+1:
                        return new_path, new_path_moves
            walk_adj = map.one_tick_walk_dir(next1.pos[0], next1.pos[1])
            for j in range(len(walk_adj[0])):
                next2 = next1.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                if (next2.pos, next2.direction) not in visited_walk:
                    if next2 not in visited_state:
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next1, next2))
                        new_path_moves.append("surge walk")
                        visited_state.add(next2)
                        queue.append((new_path, new_path_moves))
                        if end[0]-1 <= next2.pos[0] <= end[0]+1 and end[1]-1 <= next2.pos[1] <= end[1]+1:
                            return new_path, new_path_moves
            if next1.can_bd():
                bd_adj = map.bd_range_dir(next1.pos[0], next1.pos[1])
                for i in range(len(bd_adj[0])):
                    next2 = next1.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("surge bd")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if end[0]-1 <= next2.pos[0] <= end[0]+1 and end[1]-1 <= next2.pos[1] <= end[1]+1:
                                return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        if (next3.pos, next3.direction) not in visited_walk:
                            if next3 not in visited_state:
                                new_path = path[0].copy()
                                new_path_moves = path[1].copy()
                                new_path.append((next1, next2, next3))
                                new_path_moves.append("surge bd walk")
                                visited_state.add(next3)
                                queue.append((new_path, new_path_moves))
                                if end[0]-1 <= next3.pos[0] <= end[0]+1 and end[1]-1 <= next3.pos[1] <= end[1]+1:
                                    return new_path, new_path_moves
        #bd+surge/escape+walk
        if node.can_bd():
            bd_adj = map.bd_range_dir(node.pos[0], node.pos[1])
            for i in range(len(bd_adj[0])):
                next1 = node.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                if (next1.pos, next1.direction) not in visited_walk:
                    if next1 not in visited_state:
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next1, next1))
                        new_path_moves.append("bd")
                        visited_state.add(next1)
                        queue.append((new_path, new_path_moves))
                        if end[0]-1 <= next1.pos[0] <= end[0]+1 and end[1]-1 <= next1.pos[1] <= end[1]+1:
                            return new_path, new_path_moves
                walk_adj = map.one_tick_walk_dir(next1.pos[0], next1.pos[1])
                for j in range(len(walk_adj[0])):
                    next2 = next1.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("bd walk")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if end[0]-1 <= next2.pos[0] <= end[0]+1 and end[1]-1 <= next2.pos[1] <= end[1]+1:
                                return new_path, new_path_moves
                if next1.can_surge():
                    next2 = next1.surge()
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("bd surge")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if end[0]-1 <= next2.pos[0] <= end[0]+1 and end[1]-1 <= next2.pos[1] <= end[1]+1:
                                return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0],walk_adj[0][j][1], walk_adj[1][j])
                        if (next3.pos, next3.direction) not in visited_walk:
                            if next3 not in visited_state:
                                new_path = path[0].copy()
                                new_path_moves = path[1].copy()
                                new_path.append((next1, next2, next3))
                                new_path_moves.append("bd surge walk")
                                visited_state.add(next3)
                                queue.append((new_path, new_path_moves))
                                if end[0]-1 <= next3.pos[0] <= end[0]+1 and end[1]-1 <= next3.pos[1] <= end[1]+1:
                                    return new_path, new_path_moves
                if next1.can_escape():
                    next2 = next1.escape()
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("bd escape")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if end[0]-1 <= next2.pos[0] <= end[0]+1 and end[1]-1 <= next2.pos[1] <= end[1]+1:
                                return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        if (next3.pos, next3.direction) not in visited_walk:
                            if next3 not in visited_state:
                                new_path = path[0].copy()
                                new_path_moves = path[1].copy()
                                new_path.append((next1, next2, next3))
                                new_path_moves.append("bd escape walk")
                                visited_state.add(next3)
                                queue.append((new_path, new_path_moves))
                                if end[0]-1 <= next3.pos[0] <= end[0]+1 and end[1]-1 <= next3.pos[1] <= end[1]+1:
                                    return new_path, new_path_moves
        #escape+bd+walk
        if node.can_escape():
            next1 = node.escape()
            if (next1.pos, next1.direction) not in visited_walk:
                if next1 not in visited_state:
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next1))
                    new_path_moves.append("escape")
                    visited_state.add(next1)
                    queue.append((new_path, new_path_moves))
                    if end[0]-1 <= next1.pos[0] <= end[0]+1 and end[1]-1 <= next1.pos[1] <= end[1]+1:
                        return new_path, new_path_moves
            walk_adj = map.one_tick_walk_dir(next1.pos[0], next1.pos[1])
            for j in range(len(walk_adj[0])):
                next2 = next1.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                if (next2.pos, next2.direction) not in visited_walk:
                    if next2 not in visited_state:
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next1, next2))
                        new_path_moves.append("escape walk")
                        visited_state.add(next2)
                        queue.append((new_path, new_path_moves))
                        if end[0]-1 <= next2.pos[0] <= end[0]+1 and end[1]-1 <= next2.pos[1] <= end[1]+1:
                            return new_path, new_path_moves
            if next1.can_bd():
                bd_adj = map.bd_range_dir(next1.pos[0], next1.pos[1])
                for i in range(len(bd_adj[0])):
                    next2 = next1.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                    if (next2.pos, next2.direction) not in visited_walk:
                        if next2 not in visited_state:
                            new_path = path[0].copy()
                            new_path_moves = path[1].copy()
                            new_path.append((next1, next1, next2))
                            new_path_moves.append("escape bd")
                            visited_state.add(next2)
                            queue.append((new_path, new_path_moves))
                            if end[0]-1 <= next2.pos[0] <= end[0]+1 and end[1]-1 <= next2.pos[1] <= end[1]+1:
                                return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        if (next3.pos, next3.direction) not in visited_walk:
                            if next3 not in visited_state:
                                new_path = path[0].copy()
                                new_path_moves = path[1].copy()
                                new_path.append((next1, next2, next3))
                                new_path_moves.append("escape bd walk")
                                visited_state.add(next3)
                                queue.append((new_path, new_path_moves))
                                if end[0]-1 <= next3.pos[0] <= end[0]+1 and end[1]-1 <= next3.pos[1] <= end[1]+1:
                                    return new_path, new_path_moves

def a_star_end_buffer(start_state, end, map, heuristic):
    unique = count()
    path = [(start_state, start_state, start_state)]
    path_moves = []
    if end[0] - 1 <= start_state.pos[0] <= end[0] + 1 and end[1] - 1 <= start_state.pos[1] <= end[1] + 1:
        return path
    queue = qqueue.PriorityQueue()
    queue.put((0, next(unique), (path, path_moves)))
    cost: dict[State, int] = {start_state: 0}
    first = True
    while not queue.empty():
        path = queue.get()[2]
        current_node = path[0][-1][-1]
        node = path[0][-1][-1]
        if not first:
            node = node.update()
        first = False
        if end[0] - 1 <= node.pos[0] <= end[0] + 1 and end[1] - 1 <= node.pos[1] <= end[1] + 1:
            return path
        # wait
        new_path = path[0].copy()
        new_path_moves = path[1].copy()
        new_path.append((node, node, node))
        new_path_moves.append("wait")
        if node not in cost or cost[current_node] + 1 < cost[node]:
            cost[node] = cost[current_node] + 1
            f = cost[current_node] + 1 + heuristic(node, end)
            queue.put((f, next(unique), (new_path, new_path_moves)))
        # walk
        walk_adj = map.one_tick_walk_dir(node.pos[0], node.pos[1])
        for i in range(len(walk_adj[0])):
            next1 = node.move(walk_adj[0][i][0], walk_adj[0][i][1], walk_adj[1][i])
            new_path = path[0].copy()
            new_path_moves = path[1].copy()
            new_path.append((next1, next1, next1))
            new_path_moves.append("walk")
            if next1 not in cost or cost[current_node] + 1 < cost[next1]:
                cost[next1] = cost[current_node] + 1
                f = cost[current_node] + 1 + heuristic(next1, end)
                queue.put((f, next(unique), (new_path, new_path_moves)))
            if end[0] - 1 <= next1.pos[0] <= end[0] + 1 and end[1] - 1 <= next1.pos[1] <= end[1] + 1:
                return new_path, new_path_moves
        # surge+bd+walk
        if node.can_surge():
            next1 = node.surge()
            new_path = path[0].copy()
            new_path_moves = path[1].copy()
            new_path.append((next1, next1, next1))
            new_path_moves.append("surge")
            if next1 not in cost or cost[current_node] + 1 < cost[next1]:
                cost[next1] = cost[current_node] + 1
                f = cost[current_node] + 1 + heuristic(next1, end)
                queue.put((f, next(unique), (new_path, new_path_moves)))
            if end[0] - 1 <= next1.pos[0] <= end[0] + 1 and end[1] - 1 <= next1.pos[1] <= end[1] + 1:
                return new_path, new_path_moves
            walk_adj = map.one_tick_walk_dir(next1.pos[0], next1.pos[1])
            for j in range(len(walk_adj[0])):
                next2 = next1.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                new_path = path[0].copy()
                new_path_moves = path[1].copy()
                new_path.append((next1, next1, next2))
                new_path_moves.append("surge walk")
                if next2 not in cost or cost[current_node] + 1 < cost[next2]:
                    cost[next2] = cost[current_node] + 1
                    f = cost[current_node] + 1 + heuristic(next2, end)
                    queue.put((f, next(unique), (new_path, new_path_moves)))
                if end[0] - 1 <= next2.pos[0] <= end[0] + 1 and end[1] - 1 <= next2.pos[1] <= end[1] + 1:
                    return new_path, new_path_moves
            if next1.can_bd():
                bd_adj = map.bd_range_dir(next1.pos[0], next1.pos[1])
                for i in range(len(bd_adj[0])):
                    next2 = next1.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next2))
                    new_path_moves.append("surge bd")
                    if next2 not in cost or cost[current_node] + 1 < cost[next2]:
                        cost[next2] = cost[current_node] + 1
                        f = cost[current_node] + 1 + heuristic(next2, end)
                        queue.put((f, next(unique), (new_path, new_path_moves)))
                    if end[0] - 1 <= next2.pos[0] <= end[0] + 1 and end[1] - 1 <= next2.pos[1] <= end[1] + 1:
                        return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next2, next3))
                        new_path_moves.append("surge bd walk")
                        if next3 not in cost or cost[current_node] + 1 < cost[next3]:
                            cost[next3] = cost[current_node] + 1
                            f = cost[current_node] + 1 + heuristic(next3, end)
                            queue.put((f, next(unique), (new_path, new_path_moves)))
                        if end[0] - 1 <= next3.pos[0] <= end[0] + 1 and end[1] - 1 <= next3.pos[1] <= end[1] + 1:
                            return new_path, new_path_moves
        # bd+surge/escape+walk
        if node.can_bd():
            bd_adj = map.bd_range_dir(node.pos[0], node.pos[1])
            for i in range(len(bd_adj[0])):
                next1 = node.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                new_path = path[0].copy()
                new_path_moves = path[1].copy()
                new_path.append((next1, next1, next1))
                new_path_moves.append("bd")
                if next1 not in cost or cost[current_node] + 1 < cost[next1]:
                    cost[next1] = cost[current_node] + 1
                    f = cost[current_node] + 1 + heuristic(next1, end)
                    queue.put((f, next(unique), (new_path, new_path_moves)))
                if end[0] - 1 <= next1.pos[0] <= end[0] + 1 and end[1] - 1 <= next1.pos[1] <= end[1] + 1:
                    return new_path, new_path_moves
                walk_adj = map.one_tick_walk_dir(next1.pos[0], next1.pos[1])
                for j in range(len(walk_adj[0])):
                    next2 = next1.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next2))
                    new_path_moves.append("bd walk")
                    if next2 not in cost or cost[current_node] + 1 < cost[next2]:
                        cost[next2] = cost[current_node] + 1
                        f = cost[current_node] + 1 + heuristic(next2, end)
                        queue.put((f, next(unique), (new_path, new_path_moves)))
                    if end[0] - 1 <= next2.pos[0] <= end[0] + 1 and end[1] - 1 <= next2.pos[1] <= end[1] + 1:
                        return new_path, new_path_moves
                if next1.can_surge():
                    next2 = next1.surge()
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next2))
                    new_path_moves.append("bd surge")
                    if next2 not in cost or cost[current_node] + 1 < cost[next2]:
                        cost[next2] = cost[current_node] + 1
                        f = cost[current_node] + 1 + heuristic(next2, end)
                        queue.put((f, next(unique), (new_path, new_path_moves)))
                    if end[0] - 1 <= next2.pos[0] <= end[0] + 1 and end[1] - 1 <= next2.pos[1] <= end[1] + 1:
                        return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next2, next3))
                        new_path_moves.append("bd surge walk")
                        if next3 not in cost or cost[current_node] + 1 < cost[next3]:
                            cost[next3] = cost[current_node] + 1
                            f = cost[current_node] + 1 + heuristic(next3, end)
                            queue.put((f, next(unique), (new_path, new_path_moves)))
                        if end[0] - 1 <= next3.pos[0] <= end[0] + 1 and end[1] - 1 <= next3.pos[1] <= end[1] + 1:
                            return new_path, new_path_moves
                if next1.can_escape():
                    next2 = next1.escape()
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next2))
                    new_path_moves.append("bd escape")
                    if next2 not in cost or cost[current_node] + 1 < cost[next2]:
                        cost[next2] = cost[current_node] + 1
                        f = cost[current_node] + 1 + heuristic(next2, end)
                        queue.put((f, next(unique), (new_path, new_path_moves)))
                    if end[0] - 1 <= next2.pos[0] <= end[0] + 1 and end[1] - 1 <= next2.pos[1] <= end[1] + 1:
                        return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next2, next3))
                        new_path_moves.append("bd escape walk")
                        if next3 not in cost or cost[current_node] + 1 < cost[next3]:
                            cost[next3] = cost[current_node] + 1
                            f = cost[current_node] + 1 + heuristic(next3, end)
                            queue.put((f, next(unique), (new_path, new_path_moves)))
                        if end[0] - 1 <= next3.pos[0] <= end[0] + 1 and end[1] - 1 <= next3.pos[1] <= end[1] + 1:
                            return new_path, new_path_moves
        # escape+bd+walk
        if node.can_escape():
            next1 = node.escape()
            new_path = path[0].copy()
            new_path_moves = path[1].copy()
            new_path.append((next1, next1, next1))
            new_path_moves.append("escape")
            if next1 not in cost or cost[current_node] + 1 < cost[next1]:
                cost[next1] = cost[current_node] + 1
                f = cost[current_node] + 1 + heuristic(next1, end)
                queue.put((f, next(unique), (new_path, new_path_moves)))
            if end[0] - 1 <= next1.pos[0] <= end[0] + 1 and end[1] - 1 <= next1.pos[1] <= end[1] + 1:
                return new_path, new_path_moves
            walk_adj = map.one_tick_walk_dir(next1.pos[0], next1.pos[1])
            for j in range(len(walk_adj[0])):
                next2 = next1.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                new_path = path[0].copy()
                new_path_moves = path[1].copy()
                new_path.append((next1, next1, next2))
                new_path_moves.append("escape walk")
                if next2 not in cost or cost[current_node] + 1 < cost[next2]:
                    cost[next2] = cost[current_node] + 1
                    f = cost[current_node] + 1 + heuristic(next2, end)
                    queue.put((f, next(unique), (new_path, new_path_moves)))
                if end[0] - 1 <= next2.pos[0] <= end[0] + 1 and end[1] - 1 <= next2.pos[1] <= end[1] + 1:
                    return new_path, new_path_moves
            if next1.can_bd():
                bd_adj = map.bd_range_dir(next1.pos[0], next1.pos[1])
                for i in range(len(bd_adj[0])):
                    next2 = next1.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                    new_path = path[0].copy()
                    new_path_moves = path[1].copy()
                    new_path.append((next1, next1, next2))
                    new_path_moves.append("escape bd")
                    if next2 not in cost or cost[current_node] + 1 < cost[next2]:
                        cost[next2] = cost[current_node] + 1
                        f = cost[current_node] + 1 + heuristic(next2, end)
                        queue.put((f, next(unique), (new_path, new_path_moves)))
                    if end[0] - 1 <= next2.pos[0] <= end[0] + 1 and end[1] - 1 <= next2.pos[1] <= end[1] + 1:
                        return new_path, new_path_moves
                    walk_adj = map.one_tick_walk_dir(next2.pos[0], next2.pos[1])
                    for j in range(len(walk_adj[0])):
                        next3 = next2.move(walk_adj[0][j][0], walk_adj[0][j][1], walk_adj[1][j])
                        new_path = path[0].copy()
                        new_path_moves = path[1].copy()
                        new_path.append((next1, next2, next3))
                        new_path_moves.append("escape bd walk")
                        if next3 not in cost or cost[current_node] + 1 < cost[next3]:
                            cost[next3] = cost[current_node] + 1
                            f = cost[current_node] + 1 + heuristic(next3, end)
                            queue.put((f, next(unique), (new_path, new_path_moves)))
                        if end[0] - 1 <= next3.pos[0] <= end[0] + 1 and end[1] - 1 <= next3.pos[1] <= end[1] + 1:
                            return new_path, new_path_moves
#heuristic functions
def l_infinity(state, end):
    distance = max(abs(state.pos[0] - end[0]), abs(state.pos[1] - end[1])) - 1
    if distance <= 0:
        return 0
    return distance/22

def l_infinity_cds(state, end):
    state = state.update()
    distance = max(abs(state.pos[0] - end[0]), abs(state.pos[1] - end[1])) - 1
    if distance <= 0:
        return 0
    ticks_left = distance/2
    ticks = 0
    while ticks_left > 0:
        curr = state.min_cd()
        if curr[0] - ticks >= ticks_left:
            ticks += ticks_left
            break
        ticks_left = ticks_left - (curr[0] - ticks)
        ticks = curr[0]
        if curr[1] == "se":
            ticks_left -= 6
            state.secd = [17 + ticks, max(2, state.secd[1]) + ticks, 17 + ticks]
            ticks += 1
        elif curr[1] == "s":
            ticks_left -= 6
            state.secd = [max(2, state.secd[1]) + ticks, 17 + ticks, max(2, state.secd[1]) + ticks]
            ticks += 1
        elif curr[1] == "e":
            ticks_left -= 4.5
            state.secd = [max(2, state.secd[1]) + ticks, max(2, state.secd[1]) + ticks, 17 + ticks]
            ticks += 1
        elif curr[1] == "bd":
            ticks_left -= 6
            state.bdcd = 17 + ticks
            ticks += 1
    return ticks

def walk_dist_cds(state, end):
    state = state.update()
    distance = state.map.heuristic_data[state.pos[0]][state.pos[1]]
    print(distance)
    if distance <= 0:
        return 0
    ticks_left = distance
    ticks = 0
    while ticks_left > 0:
        curr = state.min_cd()
        if curr[0] - ticks >= ticks_left:
            ticks += ticks_left
            break
        ticks_left = ticks_left - (curr[0] - ticks)
        ticks = curr[0]
        if curr[1] == "se":
            ticks_left -= 6
            state.secd = [17 + ticks, max(2, state.secd[1]) + ticks, 17 + ticks]
            ticks += 1
        elif curr[1] == "s":
            ticks_left -= 6
            state.secd = [max(2, state.secd[1]) + ticks, 17 + ticks, max(2, state.secd[1]) + ticks]
            ticks += 1
        elif curr[1] == "e":
            ticks_left -= 4.5
            state.secd = [max(2, state.secd[1]) + ticks, max(2, state.secd[1]) + ticks, 17 + ticks]
            ticks += 1
        elif curr[1] == "bd":
            ticks_left -= 6
            state.bdcd = 17 + ticks
            ticks += 1
    return ticks
