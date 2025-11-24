from dataclasses import dataclass
from models.ground import Ground
from models.spreadable import Spreadable


@dataclass
class Aqua(Ground, Spreadable):
    pass
