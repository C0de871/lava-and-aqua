"""
Board Loader - Parses board files and creates Board objects
"""

from models.board import Board
from models.player import Player
from models.position import Position
from utils.zobrist_hash import Zobrist


class BoardLoader:
    """
    Board file format:
    Line 1: width height
    Line 2: player_x player_y
    Line 3: gate_x gate_y
    Line 4: num_keys
    Line 5+: key_x key_y (for each key)

    Then grid (height rows):
    Each cell format: ground:entity

    Ground types:
    - 'E' = Empty
    - 'L' = Lava
    - 'A' = Aqua

    Entity types:
    - '.' = None
    - 'W' = SolidWall (not permeable)
    - 'P' = SolidWall (permeable)
    - 'S' = Stone
    - 'C<n>' = CountDownWall with count n

    Example cell: "." = Empty ground, no entity
    Example cell: "L" = Lava ground, no entity
    Example cell: "W" = Empty ground, solid wall
    Example cell: "A:P" = Aqua ground, permeable wall
    Example cell: "C3" = Empty ground, countdown wall with 3
    """

    def load_from_file(self, filepath, player: Player):
        """Load board from file"""
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        idx = 0

        # Parse dimensions
        width, height = map(int, lines[idx].split())
        idx += 1

        # Parse player position
        player_x, player_y = map(int, lines[idx].split())
        player_pos = Position(player_x, player_y)
        player.set_pos(player_pos)
        idx += 1

        # Parse gate position
        gate_x, gate_y = map(int, lines[idx].split())
        gate_pos = Position(gate_x, gate_y)
        idx += 1

        # Parse keys
        num_keys = int(lines[idx])
        idx += 1

        keys = set()
        for _ in range(num_keys):
            key_x, key_y = map(int, lines[idx].split())
            keys.add(Position(key_x, key_y))
            idx += 1

        # Parse grid
        grid = []
        for y in range(height):
            if idx >= len(lines):
                raise ValueError(
                    f"Not enough grid rows. Expected {height}, got {len(grid)}")

            row_data = lines[idx].split()
            if len(row_data) != width:
                raise ValueError(
                    f"Row {y} has {len(row_data)} cells, expected {width}")

            row = []
            for x, cell_str in enumerate(row_data):
                # ? Parse: W, ., S, P, C, L, A
                row.append(cell_str)

            grid.append(row)
            idx += 1
        Zobrist.initTables(height, width)
        h = Zobrist.computeHash(grid,keys,player_pos)

        # Create board
        board = Board(
            row=height,
            col=width,
            player=player,
            gate_pos=gate_pos,
            grid=grid,
            h=h,
            keys=keys
        )

        return board
