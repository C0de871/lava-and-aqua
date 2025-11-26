# Lava & Aqua - Pygame GUI

A Pygame-based GUI for the Lava & Aqua puzzle game using MVC architecture.

## Project Structure

```
project/
├── main.py                          # Entry point
├── controllers/
│   └── game_controller.py           # Game loop and state management
├── views/
│   ├── menu_view.py                 # Main menu
│   ├── file_chooser_view.py         # Board file selection
│   ├── game_view.py                 # Game board rendering
│   └── dialog_view.py               # Win/death dialogs
├── models/                          # Your existing game logic
│   ├── board.py
│   ├── player.py
│   ├── aqua.py
│   ├── lava.py
│   ├── position.py
│   └── ... (all your model files)
├── utils/
│   └── board_loader.py              # Board file parser
└── boards/                          # Level files
    ├── tutorial.txt
    ├── level1.txt
    └── level2.txt
```

## Requirements

- Python 3.8+
- Pygame 2.0+

Install dependencies:
```bash
pip install pygame
```

## Running the Game

```bash
python main.py
```

## Controls

### Menu Navigation
- Mouse to click buttons

### In-Game (Human Mode)
- **Arrow Keys** or **WASD**: Move player
- **R**: Restart current level
- **ESC**: Return to menu

## Board File Format

Board files are text files with the following structure:

```
width height
player_x player_y
gate_x gate_y
num_keys
[key_x key_y] (repeated for each key)
[grid rows]
```

### Grid Cell Format

Each cell: `ground:entity`

**Ground Types:**
- `E` = Empty
- `L` = Lava (deadly)
- `A` = Aqua (water)

**Entity Types:**
- `.` = None
- `W` = Solid Wall
- `P` = Permeable Wall (liquids pass through)
- `S` = Stone (pushable box)
- `C<n>` = Countdown Wall (e.g., `C3` = wall with 3 turns)

### Example Board File

```
12 10
2 2
10 8
1
5 5
W:W W:W W:W W:W W:W W:W W:W W:W W:W W:W W:W W:W
W:W . . . . . . . . . . W:W
W:W . . . L L L . . . . W:W
W:W . . . L L L . S . W:W
W:W . . A A A . . . . . W:W
W:W . . . . . . . . . . W:W
W:W W:W W:W W:W W:W W:W W:W W:W W:W W:W W:W W:W
```

## Game Mechanics

### Turn Sequence
Each player move triggers:
1. **Player Movement**: Move player, push stones if needed
2. **Lava Spread**: Lava spreads to adjacent empty tiles
3. **Water-Lava Interaction**: Aqua converts adjacent lava to walls
4. **Aqua Spread**: Aqua spreads to adjacent empty tiles
5. **Countdown Walls**: Decrement and remove when reaching 0
6. **Win/Death Check**: Check if player reached gate or touched lava

### Entities
- **Player**: Controlled character (circle with eyes)
- **Stone**: Pushable boxes (gray with corner dots)
- **Walls**: Impassable barriers
- **Permeable Walls**: Block player but allow liquids (four corner squares)
- **Countdown Walls**: Disappear after N turns (shows number)

### Fluids
- **Lava**: Orange, deadly to player, spreads each turn
- **Aqua**: Blue water, converts adjacent lava to walls, spreads each turn

### Objectives
- **Keys**: Collect all keys (purple circles)
- **Gate**: Reach the gate after collecting keys (purple square ring)

## Visuals

### Tile Rendering
- **Empty**: Checkerboard white pattern
- **Lava**: Orange fill
- **Aqua**: Dark blue fill
- **Solid Wall**: Gray/blue block
- **Permeable Wall**: Four corner squares with center visible
- **Stone**: Gray square with four corner dots
- **Key**: Light purple floating circle
- **Gate**: Purple square ring
- **Player**: Orange circle with two eyes

### HUD
- Move counter
- Control hints

## Architecture (MVC)

### Model
Your existing game logic (`models/` directory):
- Handles all game rules
- Board state management
- Entity behaviors
- Movement validation
- Spread mechanics

### View
Pygame rendering (`views/` directory):
- Menu screens
- Board visualization
- Dialogs
- HUD elements

### Controller
Game flow management (`controllers/` directory):
- Event handling
- State transitions
- Connects model and view
- Game loop coordination

## Creating New Levels

1. Create a new `.txt` file in `boards/` directory
2. Follow the board file format
3. Test the level by loading it through the file chooser

## Extending the Game

### Adding New Tile Types
1. Create model class in `models/`
2. Update `board_loader.py` parser
3. Add rendering code in `game_view.py`

### Adding Assets
Place image files in `assets/` directory and update `game_view._load_assets()` to load them.

## Known Issues

- Border cells (row/col 0 and max) are not playable (treated as boundaries)
- Position validation uses `> 0` and `< max`, making borders inaccessible

## License

- L was here
- Code 871