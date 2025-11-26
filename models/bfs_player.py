
from dataclasses import dataclass
import time

import pygame

from models.player import Player
from models.position import Position
from utils.tree import Node, QueueFrontier
from views.console_renderer import ConsoleRenderer


@dataclass(init=False)
class AiPlayer(Player):

    player_type = "Ai"

    def __init__(self, position: Position = Position(0, 0)):
        super().__init__(position)
        self.solution_path = []  # Will store the calculated path
        self.current_index = 0   # Track position in the solution
        self.is_path_calculated = False

    def clone(self):
        return AiPlayer(self.position.clone())

    def get_next_action(self, event):
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

    def solve(self, board):
        start_time = time.time()
        start = Node(state=board, parent=None, action=None)
        frontier = QueueFrontier()
        frontier.add(start)
        explored = set()
        while not frontier.empty():
            node = frontier.remove()

            if node.state.h in explored:
                continue

            explored.add(node.state.h)
            actions = node.state.get_available_actions(
                node.parent.state if node.parent is not None else None, node.action)
            for action in actions:
                new_board = node.state.transition_model(action)
                # ConsoleRenderer().render(new_board,2)
                if new_board.is_player_touch_lava_or_wall():
                    continue

                if new_board.is_gate_reached():
                    # Build solution path
                    path = []
                    current = Node(state=new_board, parent=node, action=action)
                    while current.parent is not None:
                        path.append(current.action)
                        current = current.parent
                    self.solution_path = path[::-1]
                    self.is_path_calculated = True
                    print(f"visited state: {len(explored)}")
                    print(f"generated state: {len(frontier.frontier_hashes)}")
                    end_time = time.time()
                    return (end_time-start_time, self.solution_path, len(explored), len(frontier.frontier_hashes))

                if new_board.h not in explored and frontier.contains_state(new_board.h):
                    child = Node(state=new_board, parent=node, action=action)
                    frontier.add(child)
        print("No solution found")

    def reset_progress(self):
        """Reset the AI's progress through the solution"""
        self.current_index = 0
