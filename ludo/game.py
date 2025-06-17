"""
Game module - main game logic and state management
"""

from .board import Board
from .player import Player
from .utils import roll_dice

class Game:
    def __init__(self, num_players=4):
        self.board = Board()
        self.num_players = num_players
        self.current_player_index = 0
        self.game_over = False
        self.winner = None
        
        # Initialize players
        colors = ['red', 'blue', 'yellow', 'green'][:num_players]
        self.players = []
        
        for i, color in enumerate(colors):
            player_name = f"Player {i+1}"
            self.players.append(Player(player_name, color))
    
    def current_player(self):
        """Get the current player"""
        return self.players[self.current_player_index]
    
    def next_turn(self):
        """Move to the next player's turn"""
        if not self.game_over:
            self.current_player_index = (self.current_player_index + 1) % self.num_players
    
    def get_movable_tokens(self, player, dice_value):
        """Get list of tokens that can be moved with the given dice value"""
        movable_tokens = []
        
        for i, token in enumerate(player.tokens):
            new_position = self.board.get_next_position(token.position, dice_value, player.color)
            
            # Check if move is valid
            if new_position != token.position:  # Position would change
                # Check for blocking by own tokens
                if not self._is_blocked_by_own_token(player, new_position):
                    movable_tokens.append(i)
        
        return movable_tokens
    
    def _is_blocked_by_own_token(self, player, position):
        """Check if position is blocked by player's own token"""
        if position >= 100:  # Home stretch - no blocking
            return False
        
        for token in player.tokens:
            if token.position == position:
                return True
        return False
    
    def move_token(self, player, token_index, dice_value):
        """Move a specific token and handle captures"""
        if token_index >= len(player.tokens):
            return False
        
        token = player.tokens[token_index]
        new_position = self.board.get_next_position(token.position, dice_value, player.color)
        
        if new_position == token.position:  # Invalid move
            return False
        
        # Check for captures
        captured = self._check_captures(player, new_position)
        
        # Update token position
        old_position = token.position
        token.position = new_position
        
        # Update player statistics
        self._update_player_stats(player, old_position, new_position)
        
        return True
    
    def _check_captures(self, attacking_player, position):
        """Check and handle token captures at the given position"""
        captured_tokens = []
        
        for other_player in self.players:
            if other_player == attacking_player:
                continue
            
            for token in other_player.tokens:
                if token.position == position:
                    if self.board.can_capture(position, attacking_player.color, other_player.color):
                        # Send token back to home
                        token.position = -1
                        captured_tokens.append(token)
                        self._update_player_stats(other_player, position, -1)
        
        return captured_tokens
    
    def _update_player_stats(self, player, old_position, new_position):
        """Update player's token statistics"""
        # Reset counters
        player.tokens_in_home = 0
        player.tokens_in_play = 0
        player.tokens_finished = 0
        
        # Count tokens in each state
        for token in player.tokens:
            if token.position == -1:
                player.tokens_in_home += 1
            elif token.position == 105:  # Finished position
                player.tokens_finished += 1
            else:
                player.tokens_in_play += 1
    
    def check_win(self, player):
        """Check if player has won the game"""
        if player.tokens_finished == 4:
            self.game_over = True
            self.winner = player
            return True
        return False
    
    def get_game_state(self):
        """Get current game state"""
        return {
            'current_player': self.current_player().name,
            'current_color': self.current_player().color,
            'game_over': self.game_over,
            'winner': self.winner.name if self.winner else None,
            'players': [
                {
                    'name': p.name,
                    'color': p.color,
                    'tokens_home': p.tokens_in_home,
                    'tokens_play': p.tokens_in_play,
                    'tokens_finished': p.tokens_finished
                } for p in self.players
            ]
        }
