"""
Utility functions for the Ludo game
"""

import random

def roll_dice():
    """Roll a six-sided dice and return the result"""
    return random.randint(1, 6)

def get_safe_positions():
    """Return list of safe positions on the board"""
    return [1, 9, 14, 22, 27, 35, 40, 48]

def calculate_position(current_pos, steps, board_size=52):
    """Calculate new position after moving steps on circular board"""
    if current_pos == -1:  # In home
        return -1
    
    new_pos = (current_pos + steps - 1) % board_size + 1
    return new_pos

def get_color_emoji(color):
    """Get emoji representation for player colors"""
    color_emojis = {
        'red': '🔴',
        'blue': '🔵', 
        'yellow': '🟡',
        'green': '🟢'
    }
    return color_emojis.get(color, '⚪')

def format_position(position):
    """Format position for display"""
    if position == -1:
        return "Home"
    elif position >= 100:
        return f"Home Stretch {position - 100}"
    elif position == 105:
        return "Finished"
    else:
        return f"Square {position}"

def validate_move(current_pos, dice_value, color, board):
    """Validate if a move is legal"""
    if current_pos == -1 and dice_value != 6:
        return False, "Need 6 to exit home"
    
    if current_pos >= 100:  # Home stretch
        home_pos = current_pos - 100
        if home_pos + dice_value > 5:
            return False, "Cannot overshoot finish"
    
    return True, "Valid move"

def get_distance_to_finish(position, color, board):
    """Calculate distance from current position to finish"""
    if position == -1:
        return 57  # Need to go around entire board + home stretch
    elif position >= 100:
        return 105 - position
    else:
        home_entrance = board.home_entrance[color]
        if position <= home_entrance:
            return (home_entrance - position) + 6
        else:
            return (52 - position + home_entrance) + 6

def get_game_statistics(players):
    """Generate game statistics"""
    stats = {
        'total_tokens_home': sum(p.tokens_in_home for p in players),
        'total_tokens_play': sum(p.tokens_in_play for p in players),
        'total_tokens_finished': sum(p.tokens_finished for p in players),
        'leading_player': None
    }
    
    # Find leading player
    max_finished = max(p.tokens_finished for p in players)
    for player in players:
        if player.tokens_finished == max_finished:
            stats['leading_player'] = player.name
            break
    
    return stats

def simulate_dice_probability():
    """Return probability distribution for dice outcomes"""
    return {i: 1/6 for i in range(1, 7)}

def get_optimal_token_choice(player, dice_value, board):
    """Suggest optimal token to move (basic AI logic)"""
    movable_tokens = []
    
    for i, token in enumerate(player.tokens):
        if player.can_move_token(i, dice_value):
            # Calculate priority score
            score = 0
            
            # Prioritize getting tokens out of home
            if token.is_in_home() and dice_value == 6:
                score += 10
            
            # Prioritize finishing tokens
            elif token.is_in_home_stretch():
                score += 8
            
            # Prioritize tokens closer to finish
            elif token.is_in_play():
                distance = get_distance_to_finish(token.position, player.color, board)
                score += (60 - distance) / 10
            
            movable_tokens.append((i, score))
    
    if movable_tokens:
        # Return token with highest score
        return max(movable_tokens, key=lambda x: x[1])[0]
    
    return None
