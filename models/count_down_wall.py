

from dataclasses import dataclass, field
from models.wall import Wall


@dataclass(init=False)
class CountDownWall(Wall):

    __count_down: int = field()

    def __init__(self, countDown: int):
        self.__count_down = countDown

    @property
    def count_down(self):
        return self.__count_down

    def should_dispose(self):
        return self.__count_down <= 0

    def weakening(self):
        if (self.__count_down > 0):
            self.__count_down -= 1
            print(self.__count_down)
