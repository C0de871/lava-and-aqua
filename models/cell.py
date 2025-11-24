
from dataclasses import dataclass, field
from models.count_down_wall import CountDownWall
from models.empty import Empty
from models.entity import Entity
from models.ground import Ground
from models.solid_wall import SolidWall
from models.spreadable import Spreadable

from models.wall import Wall


@dataclass(init=False)
class Cell:
    __ground: Ground = field()
    __entity: Entity | None = field()

    def __init__(self, ground: Ground, entity: Entity | None = None):
        self.__ground = ground
        self.__entity = entity

    @property
    def ground(self):
        return self.__ground

    @ground.setter
    def ground(self, value):
        self.__ground = value

    @property
    def entity(self):
        return self.__entity

    @entity.setter
    def entity(self, value):
        self.__entity = value

    def has_entity(self):
        return self.entity is not None

    def is_deadly(self):
        return self.ground.is_deadly()

    def can_liquid_pass(self):
        return isinstance(self.ground, Empty) and ((isinstance(self.entity, SolidWall) and self.entity.is_permeable) or (not self.has_entity()))

    def is_wall(self):
        return isinstance(self.entity, Wall)

    def is_stone(self):
        from models.stone import Stone
        return isinstance(self.entity, Stone)

    def is_liquid(self):
        return isinstance(self.ground, Spreadable)

    def update_count_down_wall(self):
        if (isinstance(self.entity, CountDownWall)):
            self.entity.weakening()
            if (self.entity.should_dispose()):
                self.entity = None
                self.ground = Empty()
