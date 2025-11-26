from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from models.position import Position


@dataclass(init=False)
class Player(ABC):

    position: Position = field()
    isAlive: bool = field()
    player_type: str = field()

    def __init__(self, position: Position = Position(0, 0)):

        self.position = position
        self.isAlive = True

    @abstractmethod
    def get_next_action(self, event):
        """
        Get the next action(s) based on an event.

        Args:
            event: pygame event object

        Returns:
            List of Direction enum values (can be empty list)
        """
        pass

    def kill(self):
        self.isAlive = False

    def revive(self):
        self.isAlive = True

    @abstractmethod
    def clone(self):
        pass

    def set_pos(self, position: Position):
        self.position = position
