import random


class Zobrist:

    row: int
    col: int
    board: list[list[list[int]]]
    keys: list[list[int]]
    player: list[list[int]]

    @classmethod
    def randomInt(cls):
        min = 0
        max = pow(2, 64)
        return random.randint(min, max)

    # This function associates each piece with
    # a number
    @classmethod
    def indexOf(cls, cell: str):
        if cell == '.':
            return -1
        elif cell == 'L':
            return 0
        elif cell == 'A':
            return 1
        elif cell == 'W':
            return 2
        elif cell == 'LP':
            return 3
        elif cell == 'AP':
            return 4
        elif cell == 'L':
            return 6
        elif cell == 'S':
            return 7
        elif cell == 'P':
            return 8
        elif cell.startswith('C'):
            str_num = cell[1:]
            num = int(str_num)
            return 9+num
        else:
            raise ValueError(f"Unknown cell type {cell}")

    @classmethod
    def initTables(cls, row, col):
        # row x col x 68 array
        cls.board = [[[cls.randomInt() for k in range(69)]
                      for i in range(col)] for j in range(row)]


        cls.keys = [[cls.randomInt() for i in range(col)]
                    for j in range(row)]

        cls.player = [[cls.randomInt() for i in range(col)]
                      for j in range(row)]

    # Computes the hash value of a given board
    @classmethod
    def computeHash(cls, grid, keys_positions, player_pos):
        h = 0
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell != '.':
                    piece = cls.indexOf(cell)
                    h ^= cls.board[y][x][piece]
        
        # Only XOR keys at their actual positions
        for key_pos in keys_positions:
            h ^= cls.keys[key_pos.y][key_pos.x]
        
        # Only XOR player at their actual position
        h ^= cls.player[player_pos.y][player_pos.x]
        
        return h

    @classmethod
    def updateBoardHash(cls, row, col, cell: str, h):
        piece = cls.indexOf(cell)
        h ^= cls.board[row][col][piece]
        return h

    @classmethod
    def updateKeysHash(cls, row, col, h):
        h ^= cls.keys[row][col]
        return h

    @classmethod
    def updatePlayerHash(cls, row, col, h):
        h ^= cls.player[row][col]
        return h
