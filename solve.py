#!/usr/bin/env python3

import collections
import enum


class Tile(enum.Enum):
    WATER = 1
    LAND = 2
    GRILL = 3


class Direction(enum.Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class SausageOrientation(enum.Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class PlayerState(collections.namedtuple(
    "PlayerState",
    ["pos",
     "direction"]
)):
    __slots__ = ()


class SausageState(collections.namedtuple(
    "SausageState",
    ["orientation",
     "pos",
     "grilled_bottom_1",
     "grilled_bottom_2",
     "grilled_top_1",
     "grilled_top_2"]
)):
    __slots__ = ()

    def grilled_count(self):
        return (self.grilled_bottom_1 + self.grilled_bottom_2 +
                self.grilled_top_1 + self.grilled_top_2)


class GameState(collections.namedtuple(
    "GameState",
    ["player_state",  # PlayerState
     "sausage_states"]  # Tuple of SausageState
)):
    __slots__ = ()

    def grilled_count(self):
        return sum(s.grilled_count() for s in self.sausage_states)


class Level:
    def __init__(self, name, player_pos, player_dir, tiles, initial_sausages):
        self.name = name
        self.tiles = tiles
        self.initial_state = GameState(
            PlayerState(player_pos, player_dir),
            tuple(initial_sausages)
        )

    def draw_level(self):
        return "\n".join(
            "".join(
                {
                    Tile.WATER: " ",
                    Tile.LAND: "#",
                    Tile.GRILL: "!"
                }[self.tiles[x][y]] for x in range(len(self.tiles))
            ) for y in range(len(self.tiles[0]))[::-1]
        )

    def draw_state(self, state):
        def draw_tile(x, y):
            if (state.player_state.pos[0] == x and
                    state.player_state.pos[1] == y):
                return "@"
            if state.player_state.direction == Direction.UP:
                if (state.player_state.pos[0] == x and
                        state.player_state.pos[1] + 1 == y):
                    return "%"
            elif state.player_state.direction == Direction.DOWN:
                if (state.player_state.pos[0] == x and
                        state.player_state.pos[1] - 1 == y):
                    return "%"
            elif state.player_state.direction == Direction.LEFT:
                if (state.player_state.pos[0] - 1 == x and
                        state.player_state.pos[1] == y):
                    return "%"
            elif state.player_state.direction == Direction.RIGHT:
                if (state.player_state.pos[0] + 1 == x and
                        state.player_state.pos[1] == y):
                    return "%"
            for s in state.sausage_states:
                if s.orientation == SausageOrientation.HORIZONTAL:
                    if ((s.pos[0] == x or s.pos[0] + 1 == x) and
                            s.pos[1] == y):
                        return "*"
                else:
                    if (s.pos[0] == x and
                            (s.pos[1] == y or s.pos[1] + 1 == y)):
                        return "*"
            return {
                Tile.WATER: " ",
                Tile.LAND: "#",
                Tile.GRILL: "!"
            }[self.tiles[x][y]]
        return "\n".join(
            "".join(
                draw_tile(x, y) for x in range(len(self.tiles))
            ) for y in range(len(self.tiles[0]))[::-1]
        )

    def is_winning(self, state):
        # TODO: returning back to starting position/orientation
        for sausage_state in state.sausage_states:
            if (sausage_state.grilled_bottom_1 and
                    sausage_state.grilled_bottom_2 and
                    sausage_state.grilled_top_1 and
                    sausage_state.grilled_top_2):
                continue
            else:
                return False
        return True

    def solve(self):
        def heuristic_cost_estimate(state):
            sausage_count = len(state.sausage_states)
            grilled_count = state.grilled_count()
            return 100 * (4 * sausage_count - grilled_count)

        closed_set = set()
        open_set = set((level.initial_state,))
        step_lookup = {}
        g_score = collections.defaultdict(lambda: float("inf"))
        g_score[level.initial_state] = 0
        f_score = collections.defaultdict(lambda: float("inf"))
        heuristic_initial_cost = heuristic_cost_estimate(level.initial_state)
        f_score[level.initial_state] = heuristic_initial_cost
        while open_set:
            current = None
            current_score = float("inf")
            for s in open_set:
                if f_score[s] <= current_score:
                    current = s
                    current_score = f_score[s]

            if self.is_winning(current):
                print("Succeeded")
                back = current
                states = []
                while back in step_lookup:
                    states.insert(0, back)
                    back = step_lookup[back]
                return states

            open_set.remove(current)
            closed_set.add(current)

            for neighbor in self.neighbors(current):
                if neighbor in closed_set:
                    continue
                if neighbor not in open_set:
                    open_set.add(neighbor)

                tentative_g_score = g_score[current] + 1
                if tentative_g_score >= g_score[neighbor]:
                    continue

                step_lookup[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = (g_score[neighbor] +
                                     heuristic_cost_estimate(neighbor))
        print("Failed")

    def neighbors(self, state):
        yield from self.move_up(state)
        yield from self.move_down(state)
        yield from self.move_left(state)
        yield from self.move_right(state)

    def move_up(self, state):
        pushes = []
        old_pos = state.player_state.pos
        if state.player_state.direction == Direction.UP:  # move forward
            next_dir = Direction.UP
            next_pos = (old_pos[0], old_pos[1] + 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                next_pos = old_pos
            elif next_tile == Tile.LAND:
                pushes.append(((old_pos[0], old_pos[1] + 2), (0, 1)))
            elif next_tile == Tile.GRILL:
                pushes.append(((old_pos[0], old_pos[1] + 2), (0, 1)))
                next_pos = old_pos
        elif state.player_state.direction == Direction.DOWN:  # move backward
            next_dir = Direction.DOWN
            next_pos = (old_pos[0], old_pos[1] - 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                next_pos = old_pos
            elif next_tile == Tile.LAND:
                pushes.append(((old_pos[0], old_pos[1] - 1), (0, -1)))
            elif next_tile == Tile.GRILL:
                pushes.append(((old_pos[0], old_pos[1] - 1), (0, -1)))
                next_pos = old_pos
        elif state.player_state.direction == Direction.LEFT:  # turn left
            next_dir = Direction.UP
            pushes.append(((old_pos[0] - 1, old_pos[1] + 1), (-1, 0)))
            pushes.append(((old_pos[0] - 1, old_pos[1]), (0, -1)))
            next_pos = old_pos
        elif state.player_state.direction == Direction.RIGHT:  # turn right
            next_dir = Direction.UP
            pushes.append(((old_pos[0] + 1, old_pos[1] + 1), (1, 0)))
            pushes.append(((old_pos[0] + 1, old_pos[1]), (0, -1)))
            next_pos = old_pos
        yield from self.process_pushes(state, next_pos, next_dir, pushes)

    def move_down(self, state):
        pushes = []
        old_pos = state.player_state.pos
        if state.player_state.direction == Direction.UP:  # move backward
            next_dir = Direction.UP
            next_pos = (old_pos[0], old_pos[1] + 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                next_pos = old_pos
            elif next_tile == Tile.LAND:
                pushes.append(((old_pos[0], old_pos[1] + 1), (0, 1)))
            elif next_tile == Tile.GRILL:
                pushes.append(((old_pos[0], old_pos[1] + 1), (0, 1)))
                next_pos = old_pos
        elif state.player_state.direction == Direction.DOWN:  # move forward
            next_dir = Direction.DOWN
            next_pos = (old_pos[0], old_pos[1] - 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                next_pos = old_pos
            elif next_tile == Tile.LAND:
                pushes.append(((old_pos[0], old_pos[1] - 2), (0, -1)))
            elif next_tile == Tile.GRILL:
                pushes.append(((old_pos[0], old_pos[1] - 2), (0, -1)))
                next_pos = old_pos
        elif state.player_state.direction == Direction.LEFT:  # turn right
            next_dir = Direction.DOWN
            pushes.append(((old_pos[0] - 1, old_pos[1] - 1), (-1, 0)))
            pushes.append(((old_pos[0] - 1, old_pos[1]), (0, 1)))
            next_pos = old_pos
        elif state.player_state.direction == Direction.RIGHT:  # turn left
            next_dir = Direction.DOWN
            pushes.append(((old_pos[0] + 1, old_pos[1] - 1), (1, 0)))
            pushes.append(((old_pos[0] + 1, old_pos[1]), (0, 1)))
            next_pos = old_pos
        yield from self.process_pushes(state, next_pos, next_dir, pushes)

    def move_left(self, state):
        pushes = []
        old_pos = state.player_state.pos
        if state.player_state.direction == Direction.UP:  # turn right
            next_dir = Direction.LEFT
            pushes.append(((old_pos[0] - 1, old_pos[1] + 1), (0, 1)))
            pushes.append(((old_pos[0], old_pos[1] + 1), (1, 0)))
            next_pos = old_pos
        elif state.player_state.direction == Direction.DOWN:  # turn left
            next_dir = Direction.LEFT
            pushes.append(((old_pos[0] - 1, old_pos[1] - 1), (0, -1)))
            pushes.append(((old_pos[0], old_pos[1] - 1), (1, 0)))
            next_pos = old_pos
        elif state.player_state.direction == Direction.LEFT:  # move forward
            next_dir = Direction.LEFT
            next_pos = (old_pos[0] - 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                next_pos = old_pos
            elif next_tile == Tile.LAND:
                pushes.append(((old_pos[0] - 2, old_pos[1]), (-1, 0)))
            elif next_tile == Tile.GRILL:
                pushes.append(((old_pos[0] - 2, old_pos[1]), (-1, 0)))
                next_pos = old_pos
        elif state.player_state.direction == Direction.RIGHT:  # move backward
            next_dir = Direction.RIGHT
            next_pos = (old_pos[0] + 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                next_pos = old_pos
            elif next_tile == Tile.LAND:
                pushes.append(((old_pos[0] + 1, old_pos[1]), (1, 0)))
            elif next_tile == Tile.GRILL:
                pushes.append(((old_pos[0] + 1, old_pos[1]), (1, 0)))
                next_pos = old_pos
        yield from self.process_pushes(state, next_pos, next_dir, pushes)

    def move_right(self, state):
        pushes = []
        old_pos = state.player_state.pos
        if state.player_state.direction == Direction.UP:  # turn left
            next_dir = Direction.RIGHT
            pushes.append(((old_pos[1] + 1, old_pos[1] + 1), (0, 1)))
            pushes.append(((old_pos[1], old_pos[1] + 1), (-1, 0)))
            next_pos = old_pos
        elif state.player_state.direction == Direction.DOWN:  # turn right
            next_dir = Direction.RIGHT
            pushes.append(((old_pos[1] + 1, old_pos[1] - 1), (0, -1)))
            pushes.append(((old_pos[1], old_pos[1] - 1), (-1, 0)))
            next_pos = old_pos
        elif state.player_state.direction == Direction.LEFT:  # move backward
            next_dir = Direction.LEFT
            next_pos = (old_pos[0] - 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                next_pos = old_pos
            elif next_tile == Tile.LAND:
                pushes.append(((old_pos[0] - 1, old_pos[1]), (-1, 0)))
            elif next_tile == Tile.GRILL:
                pushes.append(((old_pos[0] - 1, old_pos[1]), (-1, 0)))
                next_pos = old_pos
        elif state.player_state.direction == Direction.RIGHT:  # move forward
            next_dir = Direction.RIGHT
            next_pos = (old_pos[0] + 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                next_pos = old_pos
            elif next_tile == Tile.LAND:
                pushes.append(((old_pos[0] + 2, old_pos[1]), (1, 0)))
            elif next_tile == Tile.GRILL:
                pushes.append(((old_pos[0] + 2, old_pos[1]), (1, 0)))
                next_pos = old_pos
        yield from self.process_pushes(state, next_pos, next_dir, pushes)

    def process_pushes(self, state, next_pos, next_dir, pushes):
        sausage_lookup = collections.defaultdict(lambda: None)
        for i, s in enumerate(state.sausage_states):
                sausage_lookup[s.pos] = i
                if s.orientation == SausageOrientation.HORIZONTAL:
                    sausage_lookup[(s.pos[0] + 1, s.pos[1])] = i
                else:
                    sausage_lookup[(s.pos[0], s.pos[1] + 1)] = i
        sausage_pushes = [None for _ in state.sausage_states]

        while pushes:
            push = pushes.pop()
            sausage_index = sausage_lookup[push[0]]
            if sausage_index is not None:
                sausage_pushes[sausage_index] = push
                sausage = state.sausage_states[sausage_index]
                if sausage.orientation == SausageOrientation.HORIZONTAL:
                    if push[1][0] != 0:  # push lengthwise
                        pushes.append(((push[0][0] + 2 * push[1][0],
                                      push[0][1]), push[1]))
                    else:  # roll
                        pushes.append(((sausage.pos[0],
                                      sausage.pos[1] + push[1][1]), push[1]))
                        pushes.append(((sausage.pos[0] + 1,
                                      sausage.pos[1] + push[1][1]), push[1]))
                else:  # vertical sausage orientation
                    if push[1][1] != 0:  # push lengthwise
                        pushes.append(((push[0][0],
                                      push[0][1] + 2 * push[1][1]), push[1]))
                    else:  # roll
                        pushes.append(((sausage.pos[0] + push[1][0],
                                      sausage.pos[1]), push[1]))
                        pushes.append(((sausage.pos[0] + push[1][0],
                                      sausage.pos[1] + 1), push[1]))

        burned = False
        new_sausages = [None for _ in state.sausage_states]
        for i, old_sausage in enumerate(state.sausage_states):
            if sausage_pushes[i] is None:
                new_sausages[i] = old_sausage
            else:
                push = sausage_pushes[i]
                sx = old_sausage.pos[0] + push[1][0]
                sy = old_sausage.pos[1] + push[1][1]
                if sausage.orientation == SausageOrientation.HORIZONTAL:
                    if push[1][0] != 0:  # push lengthwise
                        newgb1 = sausage.grilled_bottom_1
                        newgb2 = sausage.grilled_bottom_2
                        newgt1 = sausage.grilled_top_1
                        newgt2 = sausage.grilled_top_2
                    else:  # roll
                        newgb1 = sausage.grilled_top_1
                        newgb2 = sausage.grilled_top_2
                        newgt1 = sausage.grilled_bottom_1
                        newgt2 = sausage.grilled_bottom_2
                    if self.tiles[sx][sy] == Tile.GRILL:
                        if newgb1:
                            burned = True
                            break
                        newgb1 = True
                    if self.tiles[sx + 1][sy] == Tile.GRILL:
                        if newgb2:
                            burned = True
                            break
                        newgb2 = True
                else:  # vertical sausage orientation
                    if push[1][1] != 0:  # push lengthwise
                        newgb1 = sausage.grilled_bottom_1
                        newgb2 = sausage.grilled_bottom_2
                        newgt1 = sausage.grilled_top_1
                        newgt2 = sausage.grilled_top_2
                    else:  # roll
                        newgb1 = sausage.grilled_top_1
                        newgb2 = sausage.grilled_top_2
                        newgt1 = sausage.grilled_bottom_1
                        newgt2 = sausage.grilled_bottom_2
                    if self.tiles[sx][sy] == Tile.GRILL:
                        if newgb1:
                            burned = True
                            break
                        newgb1 = True
                    if self.tiles[sx][sy + 1] == Tile.GRILL:
                        if newgb2:
                            burned = True
                            break
                        newgb2 = True
                new_sausages[i] = SausageState(
                    old_sausage.orientation,
                    (
                        old_sausage.pos[0] + push[1][0],
                        old_sausage.pos[1] + push[1][1]
                    ),
                    newgb1,
                    newgb2,
                    newgt1,
                    newgt2
                )
        if not burned:
            yield GameState(
                PlayerState(next_pos, next_dir),
                tuple(new_sausages)
            )


level = Level(
    "Bay's Neck",
    (4, 2),
    Direction.LEFT,
    [[Tile.WATER, Tile.WATER, Tile.WATER, Tile.WATER, Tile.WATER, Tile.WATER],
     [Tile.WATER, Tile.LAND, Tile.LAND, Tile.WATER, Tile.LAND, Tile.WATER],
     [Tile.WATER, Tile.LAND, Tile.GRILL, Tile.LAND, Tile.LAND, Tile.WATER],
     [Tile.WATER, Tile.LAND, Tile.LAND, Tile.WATER, Tile.GRILL, Tile.WATER],
     [Tile.WATER, Tile.WATER, Tile.LAND, Tile.LAND, Tile.LAND, Tile.WATER],
     [Tile.WATER, Tile.WATER, Tile.WATER, Tile.WATER, Tile.WATER, Tile.WATER]],
    [SausageState(
        SausageOrientation.VERTICAL,
        (1, 1),
        False,
        False,
        False,
        False
     )]
)


def main():
    print(level.draw_level())
    print(level.draw_state(level.initial_state))
    print(level.initial_state)
    for step in level.solve():
        print(level.draw_state(step))
        print(step)


if __name__ == "__main__":
    main()
