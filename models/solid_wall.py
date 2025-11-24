from dataclasses import dataclass, field
from models.wall import Wall


@dataclass(init=False)
class SolidWall(Wall):

    is_permeable: bool = field()

    def __init__(self, is_permeable: bool):
        self.is_permeable = is_permeable
