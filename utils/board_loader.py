"""
Board Loader - Parses board files and creates Board objects
"""

from models.board import Board
from models.cell import Cell
from models.position import Position
from models.empty import Empty
from models.lava import Lava
from models.aqua import Aqua
from models.solid_wall import SolidWall
from models.count_down_wall import CountDownWall
from models.stone import Stone


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

    Example cell: "E:." = Empty ground, no entity
    Example cell: "L:." = Lava ground, no entity
    Example cell: "E:W" = Empty ground, solid wall
    Example cell: "A:P" = Aqua ground, permeable wall
    Example cell: "E:C3" = Empty ground, countdown wall with 3
    """

    def load_from_file(self, filepath, player):
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
                cell = self._parse_cell(cell_str, x, y)
                row.append(cell)

            grid.append(row)
            idx += 1

        # Create board
        board = Board(
            row=height,
            col=width,
            player_pos=player_pos,
            player=player,
            gate_pos=gate_pos,
            grid=grid,
            keys=keys
        )

        return board

    def _parse_cell(self, cell_str, x, y):
        """Parse a single cell string"""
        parts = cell_str.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid cell format at ({x},{y}): {cell_str}")

        ground_char, entity_char = parts

        # Parse ground
        if ground_char == 'E':
            ground = Empty()
        elif ground_char == 'L':
            ground = Lava()
        elif ground_char == 'A':
            ground = Aqua()
        else:
            raise ValueError(
                f"Unknown ground type at ({x},{y}): {ground_char}")

        # Parse entity
        entity = None
        if entity_char == '.':
            entity = None
        elif entity_char == 'W':
            entity = SolidWall(is_permeable=False)
        elif entity_char == 'P':
            entity = SolidWall(is_permeable=True)
        elif entity_char == 'S':
            entity = Stone()
        elif entity_char.startswith('C'):
            count = int(entity_char[1:])
            entity = CountDownWall(count)
        else:
            raise ValueError(
                f"Unknown entity type at ({x},{y}): {entity_char}")

        return Cell(ground, entity)
