from typing import Set
from models.board import Board
from models.direction_enum import Direction


class Node():
    def __init__(self, state: Board, parent, action: Direction | None, can_redo_action=False):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    def __init__(self):
        self.frontier: list[Node] = []
        self.frontier_hashes: Set[int] = set()

    def add(self, node):
        self.frontier.append(node)
        self.frontier_hashes.add(node.state.h)

    def contains_state(self, h):
        return h not in self.frontier_hashes

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):

        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
