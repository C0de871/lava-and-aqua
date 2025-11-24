from abc import ABC
from dataclasses import dataclass


@dataclass
class Ground(ABC):
    def is_deadly(self):
        return False
