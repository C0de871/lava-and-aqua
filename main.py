"""
Lava & Aqua - Main Entry Point
MVC Pygame GUI for puzzle game
"""

import pygame
import sys
from controllers.game_controller import GameController

def main():
    pygame.init()
    
    # Initialize the game controller
    controller = GameController()
    
    # Run the game
    controller.run()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()