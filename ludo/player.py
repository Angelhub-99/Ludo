"""
Player module - handles individual player data and tokens
"""

class Token:
    def __init__(self):
        self.position = -1  # -1 means in home base
    
    def is_in_home(self):
        """Check if token is in home base"""
        return self.position == -1
    
    def is_in_play(self):
        """Check if token is on the main board"""
        return 1 <= self.position <= 52
    
    def is_in_home_stretch(self):
        """Check if token is in home stretch"""
        return 100 <= self.position <= 105
    
    def is_finished(self):
        """Check if token has reached the finish"""
        return self.position == 105

class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.tokens = [Token() for _ in range(4)]  # Each player has 4 tokens
        
        # Statistics
        self.tokens_in_home = 4
        self.tokens_in_play = 0
        self.tokens_finished = 0
    
    def get_token_positions(self):
        """Get positions of all tokens"""
        return [token.position for token in self.tokens]
    
    def has_token_at_position(self, position):
        """Check if player has a token at the given position"""
        return any(token.position == position for token in self.tokens)
    
    def get_tokens_in_home(self):
        """Get list of tokens currently in home base"""
        return [i for i, token in enumerate(self.tokens) if token.is_in_home()]
    
    def get_tokens_in_play(self):
        """Get list of tokens currently on the board"""
        return [i for i, token in enumerate(self.tokens) if token.is_in_play()]
    
    def get_tokens_in_home_stretch(self):
        """Get list of tokens in home stretch"""
        return [i for i, token in enumerate(self.tokens) if token.is_in_home_stretch()]
    
    def get_finished_tokens(self):
        """Get list of finished tokens"""
        return [i for i, token in enumerate(self.tokens) if token.is_finished()]
    
    def can_move_token(self, token_index, dice_value):
        """Check if a specific token can be moved"""
        if token_index >= len(self.tokens):
            return False
        
        token = self.tokens[token_index]
        
        # Token in home needs a 6 to come out
        if token.is_in_home():
            return dice_value == 6
        
        # Token in home stretch
        if token.is_in_home_stretch():
            home_pos = token.position - 100
            return home_pos + dice_value <= 5
        
        # Token on main board
        return True
    
    def update_statistics(self):
        """Update player statistics based on current token positions"""
        self.tokens_in_home = len(self.get_tokens_in_home())
        self.tokens_in_play = len(self.get_tokens_in_play())
        self.tokens_finished = len(self.get_finished_tokens())
    
    def __str__(self):
        return f"{self.name} ({self.color})"
    
    def __repr__(self):
        return f"Player(name='{self.name}', color='{self.color}')"
