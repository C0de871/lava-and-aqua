
from copy import deepcopy
from dataclasses import dataclass

import pygame

from models.board import Board
from models.player import Player
from models.position import Position
from utils.tree import Node, QueueFrontier


@dataclass(init=False)
class AiPlayer(Player):

    def __init__(self, position: Position = Position(0, 0)):
        super().__init__(position)
        self.solution_path = []  # Will store the calculated path
        self.current_index = 0   # Track position in the solution
        self.is_path_calculated = False

    def get_next_action(self, event, board: Board):

        # Initialize frontier to just the starting position
        start = Node(state=board, parent=None, action=None)
        frontier = QueueFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        explored = set()

        # TODO
        while not frontier.empty():
            # Choose a node from the frontier
            node = frontier.remove()
            # Mark node as explored
            explored.add(node.state)

            actions = board.get_available_actions(node.state)
            for action in actions:
                new_board = deepcopy(board)
                new_board.update(action)
                child = Node(state=new_board, parent=node, action=action)
                if (child.state.is_gate_reached()):
                    while child.parent != None and child.parent.state != child.state:
                        self.solution_path.append(child.action)
                        child = child.parent
                    self.solution_path.reverse()
                if (child.state not in explored):
                    frontier.add(child)


        if event.type != pygame.KEYDOWN:
            return []

        # Space bar: return next single step
        if event.key == pygame.K_SPACE:
            if self.current_index < len(self.solution_path):
                direction = self.solution_path[self.current_index]
                self.current_index += 1
                return [direction]
            return []

        # Enter: return all remaining steps
        elif event.key == pygame.K_RETURN:
            if self.current_index < len(self.solution_path):
                remaining = self.solution_path[self.current_index:]
                self.current_index = len(self.solution_path)
                return remaining
            return []

        return []

    def set_solution_path(self, path):
        """
        Set the AI's solution path.

        Args:
            path: List of Direction enum values representing the path to goal
        """
        self.solution_path = path
        self.current_index = 0

    def reset_progress(self):
        """Reset the AI's progress through the solution"""
        self.current_index = 0
