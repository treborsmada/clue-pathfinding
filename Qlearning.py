import numpy as np

class Gamestate:
    def __init__(self, map, pos, direction, secd, bdcd, available_goals, wait_time, time):
        self.map = map
        self.pos = pos
        self.direction = direction
        self.secd = secd.copy()
        self.bdcd = bdcd
        if available_goals is None:
            self.available_goals = [i for i in range(len(self.map.goals))]
        else:
            self.available_goals = available_goals
        self.wait_time = wait_time
        self.time = time

    def __eq__(self, other):
        if isinstance(other, Gamestate):
            return self.map == other.map and self.pos == other.pos and self.direction == other.direction and self.secd == other.secd and self.bdcd == other.bdcd and self.available_goals == other.available_goals and self.wait_time == other.wait_time and self.time == other.time
        return False

    def __hash__(self):
        return hash((self.pos, self.direction, tuple(self.secd), self.bdcd, tuple(self.available_goals), self.wait_time, self.time))

    def update(self):
        new_secd = self.secd.copy()
        new_bdcd = self.bdcd
        for i in range(3):
            if not new_secd[i] == 0:
                new_secd[i] = new_secd[i]-1
        if not new_bdcd == 0:
            new_bdcd = new_bdcd - 1
        return Gamestate(self.map, self.pos, self.direction, new_secd, new_bdcd, self.available_goals.copy(), self.wait_time, abs(self.time - 1))

    def move(self, x, y, direction):
        return Gamestate(self.map, (x, y), direction, self.secd, self.bdcd, self.available_goals, self.wait_time, self.time)

    def surge(self):
        new_secd = self.secd.copy()
        if self.secd[0] == 0:
            new_pos = self.map.surge_range(self.pos[0], self.pos[1], self.direction)
            if new_pos == self.pos:
                return Gamestate(self.map, self.pos, self.direction, self.secd, self.bdcd, self.available_goals, self.wait_time, self.time)
            if self.secd[1] < 2:
                return Gamestate(self.map, new_pos, self.direction, [17, 2, 17], self.bdcd, self.available_goals, self.wait_time, self.time)
            else:
                return Gamestate(self.map, new_pos, self.direction, [17, new_secd[1], 17], self.bdcd, self.available_goals, self.wait_time, self.time)
        elif self.secd[1] == 0:
            new_pos = self.map.surge_range(self.pos[0], self.pos[1], self.direction)
            if new_pos == self.pos:
                return Gamestate(self.map, self.pos, self.direction, self.secd, self.bdcd, self.available_goals, self.wait_time, self.time)
            if self.secd[0] < 2:
                return Gamestate(self.map, new_pos, self.direction, [2, 17, 2], self.bdcd, self.available_goals, self.wait_time, self.time)
            else:
                return Gamestate(self.map, new_pos, self.direction, [new_secd[0], 17, new_secd[2]], self.bdcd, self.available_goals, self.wait_time, self.time)
        else:
            print(self.pos)
            raise Exception("Surge is on cooldown")

    def escape(self):
        new_secd = self.secd.copy()
        if self.secd[0] == 0:
            new_pos = self.map.escape_range(self.pos[0], self.pos[1], self.direction)
            if new_pos == self.pos:
                return Gamestate(self.map, self.pos, self.direction, self.secd, self.bdcd, self.available_goals, self.wait_time, self.time)
            if self.secd[2] < 2:
                return Gamestate(self.map, new_pos, self.direction, [17, 17, 2], self.bdcd, self.available_goals, self.wait_time, self.time)
            else:
                return Gamestate(self.map, new_pos, self.direction, [17, 17, new_secd[2]], self.bdcd, self.available_goals, self.wait_time, self.time)
        elif self.secd[2] == 0:
            new_pos = self.map.escape_range(self.pos[0], self.pos[1], self.direction)
            if new_pos == self.pos:
                return Gamestate(self.map, self.pos, self.direction, self.secd, self.bdcd, self.available_goals, self.wait_time, self.time)
            if self.secd[0] < 2:
                return Gamestate(self.map, new_pos, self.direction, [2, 2, 17], self.bdcd, self.available_goals, self.wait_time, self.time)
            else:
                return Gamestate(self.map, new_pos, self.direction, [new_secd[0], new_secd[1], 17], self.bdcd, self.available_goals, self.wait_time, self.time)
        else:
            print(self.pos)
            raise Exception("Escape is on cooldown")

    def bd(self, x, y, direction):
        if self.bdcd == 0:
            return Gamestate(self.map, (x, y), direction, self.secd, 17, self.available_goals, self.wait_time, self.time)

    def can_bd(self):
        return self.bdcd == 0

    def can_surge(self):
        return (self.secd[0] == 0 or self.secd[1] == 0) and self.map.surge_range(self.pos[0], self.pos[1], self.direction) is not None

    def can_escape(self):
        return self.secd[0] == 0 or self.secd[2] == 0

    def update_pulse(self, n):
        if self.time == 0:
            new_goals = []
            pulses = self.map.get_pulse(self.pos[0], self.pos[1])[n-1]
            for goal in pulses:
                if goal in self.available_goals:
                    new_goals.append(goal)
            return Gamestate(self.map, self.pos, self.direction, self.secd, self.bdcd, new_goals, self.wait_time, self.time)
        else:
            return self



