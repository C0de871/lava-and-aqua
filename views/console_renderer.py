class ConsoleRenderer:
    """Beautiful console renderer for the game board"""
    
    # Unicode box-drawing characters
    BORDER_TL = '╔'
    BORDER_TR = '╗'
    BORDER_BL = '╚'
    BORDER_BR = '╝'
    BORDER_H = '═'
    BORDER_V = '║'
    
    # ANSI color codes
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Background colors
    BG_EMPTY1 = '\033[48;5;236m'  # Dark gray
    BG_EMPTY2 = '\033[48;5;234m'  # Darker gray
    BG_LAVA = '\033[48;5;196m'     # Red
    BG_AQUA = '\033[48;5;39m'      # Cyan
    BG_WALL = '\033[48;5;240m'     # Gray
    
    # Foreground colors
    FG_PLAYER = '\033[38;5;220m'   # Yellow/Gold
    FG_KEY = '\033[38;5;213m'      # Purple
    FG_GATE = '\033[38;5;46m'      # Green
    FG_STONE = '\033[38;5;248m'    # Light gray
    FG_WALL = '\033[38;5;255m'     # White
    FG_PASSWALL = '\033[38;5;147m' # Light blue
    
    # Symbols
    SYMBOL_PLAYER = '●'
    SYMBOL_KEY = '◆'
    SYMBOL_GATE = '▣'
    SYMBOL_STONE = '■'
    SYMBOL_WALL = '█'
    SYMBOL_PASSWALL = '▒'
    SYMBOL_EMPTY = ' '
    
    def render(self, board, move_count):
        """Render the board to console with beautiful formatting"""
        from models.position import Position
        
        # Clear screen (optional - comment out if you want to see history)
        print('\033[2J\033[H', end='')
        
        # Header
        print(f"\n{self.BOLD}╔{'═' * (board.col * 2 + 2)}╗{self.RESET}")
        print(f"{self.BOLD}║{self.RESET}  🎮 GAME BOARD - Move #{move_count}  {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}╚{'═' * (board.col * 2 + 2)}╝{self.RESET}\n")
        
        # Top border
        print(f"  {self.BORDER_TL}{self.BORDER_H * (board.col * 2)}{self.BORDER_TR}")
        
        # Render board
        for y in range(board.row):
            line = f"  {self.BORDER_V}"
            
            for x in range(board.col):
                pos = Position(x, y)
                cell = board.get_cell(pos)
                
                # Determine background color (checkerboard pattern)
                bg_color = self.BG_EMPTY1 if (x + y) % 2 == 0 else self.BG_EMPTY2
                
                # Override background for special ground types
                if cell.startswith('L'):
                    bg_color = self.BG_LAVA
                elif cell.startswith('A'):
                    bg_color = self.BG_AQUA
                
                # Determine symbol and foreground color
                symbol = self.SYMBOL_EMPTY
                fg_color = ''
                
                # Check for player first (highest priority)
                if board.player.position == pos:
                    symbol = self.SYMBOL_PLAYER
                    fg_color = self.BOLD + self.FG_PLAYER
                # Then keys
                elif pos in board.keys:
                    symbol = self.SYMBOL_KEY
                    fg_color = self.BOLD + self.FG_KEY
                # Then gate
                elif pos == board.gate_pos:
                    symbol = self.SYMBOL_GATE
                    fg_color = self.BOLD + self.FG_GATE
                # Then other cell types
                elif cell == 'W':
                    symbol = self.SYMBOL_WALL
                    fg_color = self.FG_WALL
                    bg_color = self.BG_WALL
                elif cell.endswith('P'):
                    symbol = self.SYMBOL_PASSWALL
                    fg_color = self.FG_PASSWALL
                elif cell.startswith('C'):
                    # Numbered wall
                    symbol = cell[1:]  # Get the number
                    fg_color = self.BOLD + self.FG_WALL
                    bg_color = self.BG_WALL
                elif cell == 'S':
                    symbol = self.SYMBOL_STONE
                    fg_color = self.FG_STONE
                
                # Print the cell
                line += f"{bg_color}{fg_color}{symbol}{self.RESET}{bg_color} {self.RESET}"
            
            line += self.BORDER_V
            print(line)
        
        # Bottom border
        print(f"  {self.BORDER_BL}{self.BORDER_H * (board.col * 2)}{self.BORDER_BR}")
        
        # Legend
        print(f"\n  {self.BOLD}Legend:{self.RESET}")
        print(f"    {self.BOLD}{self.FG_PLAYER}{self.SYMBOL_PLAYER}{self.RESET} Player")
        print(f"    {self.BOLD}{self.FG_KEY}{self.SYMBOL_KEY}{self.RESET} Key")
        print(f"    {self.BOLD}{self.FG_GATE}{self.SYMBOL_GATE}{self.RESET} Gate")
        print(f"    {self.FG_STONE}{self.SYMBOL_STONE}{self.RESET} Stone")
        print(f"    {self.FG_WALL}{self.SYMBOL_WALL}{self.RESET} Wall")
        print(f"    {self.FG_PASSWALL}{self.SYMBOL_PASSWALL}{self.RESET} Pass-through Wall")
        print(f"    {self.BG_LAVA}  {self.RESET} Lava")
        print(f"    {self.BG_AQUA}  {self.RESET} Water")
        print()
        
        # Additional info
        print(f"  {self.BOLD}Stats:{self.RESET}")
        print(f"    Board size: {board.col}×{board.row}")
        print()

