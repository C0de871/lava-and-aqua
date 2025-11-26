
from enum import Enum


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @classmethod
    def are_opposite(cls, dir1, dir2) -> bool:
        x1, y1 = dir1.value
        x2, y2 = dir2.value
        opp = (x1 + x2, y1 + y2) == (0, 0)
        return opp
