from abc import ABC
from dataclasses import dataclass

@dataclass(init=False)
class Spreadable(ABC):
    pass
