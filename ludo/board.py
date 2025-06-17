"""
Board module for Ludo game - handles board logic and positions
"""

class Board:
    def __init__(self):
        self.BOARD_SIZE = 52  # Main track squares
        self.HOME_SIZE = 6    # Home stretch squares per player
        
        # Starting positions for each color on the main track
        self.start_positions = {
            'red': 1,
            'blue': 14,
            'yellow': 27,
            'green': 40
        }
        
        # Safe positions where tokens cannot be captured
        self.safe_positions = {1, 9, 14, 22, 27, 35, 40, 48}
        
        # Home entrance positions for each color
        self.home_entrance = {
            'red': 51,
            'blue': 12,
            'yellow': 25,
            'green': 38
        }
        
        # Color order for turn sequence
        self.color_order = ['red', 'blue', 'yellow', 'green']
    
    def is_safe_position(self, position):
        """Check if a position is safe from capture"""
        return position in self.safe_positions
    
    def get_next_position(self, current_position, steps, color):
        """Calculate next position after moving steps"""
        if current_position == -1:  # Token in home base
            if steps == 6:
                return self.start_positions[color]
            return -1
        
        # Check if token is in home stretch
        if current_position >= 100:  # Home stretch positions (100-105)
            home_pos = current_position - 100
            new_home_pos = home_pos + steps
            if new_home_pos <= 5:  # Valid home stretch position
                return 100 + new_home_pos
            return current_position  # Invalid move
        
        # Regular board movement
        new_position = (current_position + steps - 1) % self.BOARD_SIZE + 1
        
        # Check if entering home stretch
        if current_position <= self.home_entrance[color] < current_position + steps:
            steps_into_home = steps - (self.home_entrance[color] - current_position + 1)
            if steps_into_home <= 5:
                return 100 + steps_into_home
            return current_position  # Overshoot, invalid move
        
        return new_position
    
    def can_capture(self, position, attacking_color, defending_color):
        """Check if a token can capture another token at given position"""
        if self.is_safe_position(position):
            return False
        if attacking_color == defending_color:
            return False
        if position >= 100:  # Home stretch is safe
            return False
        return True
    
    def get_board_representation(self):
        """Return a visual representation of the board"""
        return {
            'main_track': list(range(1, self.BOARD_SIZE + 1)),
            'safe_positions': self.safe_positions,
            'start_positions': self.start_positions,
            'home_entrance': self.home_entrance
        }
