from dataclasses import dataclass

import pygame

from models.direction_enum import Direction
from models.player import Player
from models.position import Position


@dataclass(init=False)
class HumanPlayer(Player):
    player_type = 'Human'

    def clone(self):
        return HumanPlayer(self.position.clone())

    def get_next_action(self, event):
        """
        Process keyboard input and return a list with one direction.

        Args:
            event: pygame event object

        Returns:
            List with one Direction if valid movement key pressed, empty list otherwise
        """
        if event.type != pygame.KEYDOWN:
            return []

        direction = None
        if event.key in [pygame.K_UP, pygame.K_w]:
            direction = Direction.UP
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            direction = Direction.DOWN
        elif event.key in [pygame.K_LEFT, pygame.K_a]:
            direction = Direction.LEFT
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            direction = Direction.RIGHT

        return [direction] if direction else []
