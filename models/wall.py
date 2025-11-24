from abc import ABC
from dataclasses import dataclass

from models.entity import Entity

@dataclass(init=False)
class Wall(Entity, ABC):
    pass
