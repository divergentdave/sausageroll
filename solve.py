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
                # TODO: read off path from step_lookup and current
                print("Succeeded")
                return

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
        old_pos = state.player_state.pos

        # Up
        if state.player_state.direction == Direction.UP:  # move forward
            next_pos = (old_pos[0], old_pos[1] + 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                pass  # do nothing
            elif next_tile == Tile.LAND:
                pass  # move
            elif next_tile == Tile.GRILL:
                pass  # poke
        elif state.player_state.direction == Direction.DOWN:  # move backward
            next_pos = (old_pos[0], old_pos[1] - 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                pass  # do nothing
            elif next_tile == Tile.LAND:
                pass  # move
            elif next_tile == Tile.GRILL:
                pass  # poke
        elif state.player_state.direction == Direction.LEFT:  # turn left
            next_pos = (old_pos[0] - 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
        elif state.player_state.direction == Direction.RIGHT:  # turn right
            next_pos = (old_pos[0] + 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
        # TODO: process

        # Down
        if state.player_state.direction == Direction.UP:  # move backward
            next_pos = (old_pos[0], old_pos[1] + 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                pass  # do nothing
            elif next_tile == Tile.LAND:
                pass  # move
            elif next_tile == Tile.GRILL:
                pass  # poke
        elif state.player_state.direction == Direction.DOWN:  # move forward
            next_pos = (old_pos[0], old_pos[1] - 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                pass  # do nothing
            elif next_tile == Tile.LAND:
                pass  # move
            elif next_tile == Tile.GRILL:
                pass  # poke
        elif state.player_state.direction == Direction.LEFT:  # turn right
            next_pos = (old_pos[0] - 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
        elif state.player_state.direction == Direction.RIGHT:  # turn left
            next_pos = (old_pos[0] + 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
        # TODO: process

        # Left
        if state.player_state.direction == Direction.UP:  # turn right
            next_pos = (old_pos[0], old_pos[1] + 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
        elif state.player_state.direction == Direction.DOWN:  # turn left
            next_pos = (old_pos[0], old_pos[1] - 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
        elif state.player_state.direction == Direction.LEFT:  # move forward
            next_pos = (old_pos[0] - 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                pass  # do nothing
            elif next_tile == Tile.LAND:
                pass  # move
            elif next_tile == Tile.GRILL:
                pass  # poke
        elif state.player_state.direction == Direction.RIGHT:  # move backward
            next_pos = (old_pos[0] + 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                pass  # do nothing
            elif next_tile == Tile.LAND:
                pass  # move
            elif next_tile == Tile.GRILL:
                pass  # poke
        # TODO: process

        # Right
        if state.player_state.direction == Direction.UP:  # turn left
            next_pos = (old_pos[0], old_pos[1] + 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
        elif state.player_state.direction == Direction.DOWN:  # turn right
            next_pos = (old_pos[0], old_pos[1] - 1)
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
        elif state.player_state.direction == Direction.LEFT:  # move backward
            next_pos = (old_pos[0] - 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                pass  # do nothing
            elif next_tile == Tile.LAND:
                pass  # move
            elif next_tile == Tile.GRILL:
                pass  # poke
        elif state.player_state.direction == Direction.RIGHT:  # move forward
            next_pos = (old_pos[0] + 1, old_pos[1])
            next_tile = self.tiles[next_pos[0]][next_pos[1]]
            if next_tile == Tile.WATER:
                pass  # do nothing
            elif next_tile == Tile.LAND:
                pass  # move
            elif next_tile == Tile.GRILL:
                pass  # poke
        # TODO: process

        return
        yield None


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
    level.solve()


if __name__ == "__main__":
    main()
