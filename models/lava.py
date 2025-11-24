from dataclasses import dataclass
from models.ground import Ground
from models.spreadable import Spreadable

@dataclass
class Lava(Ground, Spreadable):

    def is_deadly(self):
        return True
