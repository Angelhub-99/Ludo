import streamlit as st
import plotly.graph_objects as go
import math
from ludo.board import Board
from ludo.game import Game
from ludo.player import Player
from ludo.utils import roll_dice

# Page configuration
st.set_page_config(
    page_title="Ludo Game",
    page_icon="🎲",
    layout="wide"
)

# Initialize session state for game
if 'game' not in st.session_state:
    st.session_state.game = Game(num_players=4)
if 'dice_value' not in st.session_state:
    st.session_state.dice_value = None
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

game = st.session_state.game

def create_interactive_board():
    """Create an interactive board using Plotly"""
    
    # Create board positions in a square layout (more like real Ludo)
    positions = []
    
    # Define the Ludo board layout (52 positions)
    # Bottom row (left to right): positions 1-6
    for i in range(6):
        positions.append((i, 0))
    
    # Right column (bottom to top): positions 7-12
    for i in range(1, 6):
        positions.append((5, i))
    
    # Top-right section: positions 13-18
    for i in range(6, 11):
        positions.append((i, 5))
    
    # Top row (right to left): positions 19-24
    for i in range(10, 5, -1):
        positions.append((i, 6))
    
    # Top-left section: positions 25-30
    for i in range(6, 11):
        positions.append((5, i))
    
    # Left column (top to bottom): positions 31-36
    for i in range(10, 5, -1):
        positions.append((0, i))
    
    # Bottom-left section: positions 37-42
    for i in range(1, 6):
        positions.append((i, 5))
    
    # Complete the circle: positions 43-52
    remaining_positions = 52 - len(positions)
    for i in range(remaining_positions):
        angle = 2 * math.pi * i / remaining_positions
        x = 6 + 2 * math.cos(angle)
        y = 6 + 2 * math.sin(angle)
        positions.append((x, y))
    
    # Ensure we have exactly 52 positions
    positions = positions[:52]
    
    # Create the plot
    fig = go.Figure()
    
    # Add board track
    x_coords = [pos[0] for pos in positions] + [positions[0][0]]  # Close the loop
    y_coords = [pos[1] for pos in positions] + [positions[0][1]]
    
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='lines',
        line=dict(color='black', width=2),
        name='Board Track',
        showlegend=False
    ))
    
    # Add position markers and tokens
    for pos_idx, (x, y) in enumerate(positions):
        position_num = pos_idx + 1
        
        # Check if any tokens are at this position
        tokens_here = []
        token_colors = []
        
        for player in game.players:
            for token_idx, token in enumerate(player.tokens):
                if token.position == position_num:
                    tokens_here.append(f"{player.name[0]}{token_idx+1}")
                    token_colors.append(player.color)
        
        # Determine marker properties
        if tokens_here:
            marker_color = token_colors[0] if len(token_colors) == 1 else 'purple'
            marker_size = 15
            hover_text = f"Position {position_num}<br>Tokens: {', '.join(tokens_here)}"
        else:
            marker_color = 'lightgray'
            marker_size = 8
            hover_text = f"Position {position_num}<br>Empty"
        
        # Check if it's a safe position
        if position_num in [1, 9, 14, 22, 27, 35, 40, 48]:
            marker_color = 'gold' if not tokens_here else marker_color
            marker_size += 3
        
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(
                size=marker_size,
                color=marker_color,
                line=dict(color='black', width=1)
            ),
            text=str(position_num),
            textposition="middle center",
            textfont=dict(size=8, color='white' if tokens_here else 'black'),
            hovertext=hover_text,
            hoverinfo="text",
            showlegend=False
        ))
    
    # Add home areas for each player
    home_areas = [
        (-2, -2, 'Red Home', 'red'),
        (13, -2, 'Blue Home', 'blue'),
        (13, 13, 'Yellow Home', 'yellow'),
        (-2, 13, 'Green Home', 'green')
    ]
    
    for x, y, label, color in home_areas:
        # Count tokens in home for this color
        player = next((p for p in game.players if p.color == color), None)
        if player:
            tokens_in_home = sum(1 for token in player.tokens if token.position == -1)
            home_text = f"{tokens_in_home}"
        else:
            home_text = "0"
        
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(size=40, color=color, opacity=0.7),
            text=home_text,
            textposition="middle center",
            textfont=dict(size=12, color='white'),
            hovertext=f"{label}<br>Tokens: {home_text}",
            hoverinfo="text",
            showlegend=False
        ))
    
    # Add center finish area
    fig.add_trace(go.Scatter(
        x=[5.5],
        y=[5.5],
        mode='markers+text',
        marker=dict(size=50, color='gold', symbol='star'),
        text='FINISH',
        textposition="middle center",
        textfont=dict(size=10, color='black'),
        hovertext="Finish Area",
        hoverinfo="text",
        showlegend=False
    ))
    
    fig.update_layout(
        title="🎲 Ludo Board - Live Game",
        showlegend=False,
        width=700,
        height=700,
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[-4, 15]
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[-4, 15]
        ),
        plot_bgcolor='lightgreen',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_board_grid():
    """Create a simple HTML grid representation of the board"""
    board_html = """
    <style>
    .board-container {
        display: grid;
        grid-template-columns: repeat(15, 30px);
        gap: 1px;
        margin: 20px auto;
        width: fit-content;
        background: #2d5a27;
        padding: 10px;
        border-radius: 10px;
    }
    .board-square {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 8px;
        font-weight: bold;
        border: 1px solid #333;
        position: relative;
    }
    .empty { background: #f0f0f0; color: #666; }
    .safe { background: #ffd700; color: #000; }
    .start { background: #4caf50; color: white; }
    .home-red { background: #f44336; color: white; }
    .home-blue { background: #2196f3; color: white; }
    .home-yellow { background: #ffeb3b; color: #000; }
    .home-green { background: #4caf50; color: white; }
    .token { font-size: 6px; }
    </style>
    <div class="board-container">
    """
    
    # Get all token positions
    all_positions = {}
    for player in game.players:
        for i, token in enumerate(player.tokens):
            pos = token.position
            if pos > 0:  # Only show tokens on board
                if pos not in all_positions:
                    all_positions[pos] = []
                all_positions[pos].append(f"{player.color[0].upper()}{i+1}")
    
    # Create 15x15 grid
    for row in range(15):
        for col in range(15):
            square_class = "board-square empty"
            square_content = ""
            
            # Determine square type and content
            game_pos = get_game_position_from_grid(row, col)
            
            if game_pos > 0:
                # Check for tokens at this position
                if game_pos in all_positions:
                    tokens = all_positions[game_pos]
                    square_content = "<br>".join(tokens[:2])
                    square_class = "board-square token"
                else:
                    square_content = str(game_pos)
                
                # Apply special styling
                if game_pos in [1, 9, 14, 22, 27, 35, 40, 48]:
                    square_class += " safe"
                elif game_pos in [1, 14, 27, 40]:
                    square_class += " start"
            
            # Home areas
            elif is_home_area(row, col):
                color = get_home_color(row, col)
                square_class = f"board-square home-{color}"
                # Count tokens in home
                player = next((p for p in game.players if p.color == color), None)
                if player:
                    home_count = sum(1 for token in player.tokens if token.position == -1)
                    square_content = str(home_count) if home_count > 0 else ""
            
            board_html += f'<div class="{square_class}">{square_content}</div>'
    
    board_html += "</div>"
    return board_html

def get_game_position_from_grid(row, col):
    """Map grid coordinates to game board positions"""
    # Top row
    if row == 0 and 6 <= col <= 8:
        return col - 5
    # Right side
    elif col == 14 and 6 <= row <= 8:
        return 13 + (row - 5)
    # Bottom row
    elif row == 14 and 6 <= col <= 8:
        return 26 + (9 - col)
    # Left side
    elif col == 0 and 6 <= row <= 8:
        return 39 + (9 - row)
    return -1

def is_home_area(row, col):
    """Check if grid position is a home area"""
    return ((1 <= row <= 5 and 1 <= col <= 5) or  # Red home
            (1 <= row <= 5 and 9 <= col <= 13) or  # Blue home
            (9 <= row <= 13 and 9 <= col <= 13) or  # Yellow home
            (9 <= row <= 13 and 1 <= col <= 5))  # Green home

def get_home_color(row, col):
    """Get home area color"""
    if 1 <= row <= 5 and 1 <= col <= 5:
        return "red"
    elif 1 <= row <= 5 and 9 <= col <= 13:
        return "blue"
    elif 9 <= row <= 13 and 9 <= col <= 13:
        return "yellow"
    elif 9 <= row <= 13 and 1 <= col <= 5:
        return "green"
    return ""

# Main title
st.title("🎲 Ludo Game")
st.markdown("---")

# Sidebar for game controls
with st.sidebar:
    st.header("🎮 Game Controls")
    
    # Game setup
    st.subheader("Game Setup")
    num_players = st.selectbox("Number of Players", [2, 3, 4], index=2)
    
    if st.button("🆕 New Game", type="primary"):
        st.session_state.game = Game(num_players=num_players)
        st.session_state.dice_value = None
        st.session_state.game_started = True
        game = st.session_state.game
        st.rerun()
    
    # Game status
    if st.session_state.game_started:
        st.subheader("Game Status")
        current_player = game.current_player()
        st.write(f"**Current Player:** {current_player.name}")
        st.write(f"**Player Color:** {current_player.color.title()}")
        
        # Display dice value if rolled
        if st.session_state.dice_value:
            st.write(f"**Last Roll:** 🎲 {st.session_state.dice_value}")
        
        # Game statistics
        st.subheader("📊 Quick Stats")
        for player in game.players:
            emoji = "🔥" if player == current_player else "👤"
            st.write(f"{emoji} {player.name}: Home({player.tokens_in_home}) Play({player.tokens_in_play}) Done({player.tokens_finished})")

# Main game area
if not st.session_state.game_started:
    st.info("👆 Click 'New Game' in the sidebar to start playing!")
    
    # Show game preview
    st.subheader("🎯 Game Preview")
    st.markdown("""
    Welcome to **Ludo Game**! 
    
    - 🎲 Roll dice to move your tokens
    - 🏠 Get all tokens from home to finish
    - ⚡ Roll 6 for extra turns
    - 🎯 Capture opponents' tokens
    - 🏆 First to finish all tokens wins!
    """)
else:
    # Check for game over
    if game.game_over:
        st.success(f"🎉 Game Over! {game.winner.name} ({game.winner.color}) wins!")
        st.balloons()
        if st.button("🔄 Play Again"):
            st.session_state.game = Game(num_players=num_players)
            st.session_state.dice_value = None
            st.session_state.game_started = True
            st.rerun()
    
    # Create layout columns
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        st.subheader("🎯 Game Board")
        
        # Board display options
        display_option = st.radio(
            "Board Display:",
            ["Interactive Board", "Grid View"],
            horizontal=True
        )
        
        if display_option == "Interactive Board":
            fig = create_interactive_board()
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(create_board_grid(), unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎮 Game Actions")
        
        if not game.game_over:
            current_player = game.current_player()
            
            # Dice rolling section
            st.markdown("### 🎲 Roll Dice")
            st.write(f"**{current_player.name}'s Turn**")
            
            if st.button("🎲 Roll Dice", type="primary", use_container_width=True):
                st.session_state.dice_value = roll_dice()
                st.success(f"🎲 Rolled: **{st.session_state.dice_value}**")
                st.rerun()
            
            # Token movement section
            if st.session_state.dice_value:
                st.markdown("### 🔄 Move Token")
                
                movable_tokens = game.get_movable_tokens(current_player, st.session_state.dice_value)
                
                if movable_tokens:
                    # Show token options with current positions
                    token_options = []
                    for i in movable_tokens:
                        token = current_player.tokens[i]
                        if token.position == -1:
                            pos_text = "Home"
                        elif token.position >= 100:
                            pos_text = f"Home Stretch {token.position - 100}"
                        else:
                            pos_text = f"Position {token.position}"
                        token_options.append(f"Token {i+1} ({pos_text})")
                    
                    selected_option = st.selectbox("Select token to move:", token_options)
                    selected_token_idx = movable_tokens[token_options.index(selected_option)]
                    
                    if st.button("✅ Move Token", use_container_width=True):
                        success = game.move_token(current_player, selected_token_idx, st.session_state.dice_value)
                        
                        if success:
                            st.success("🎯 Token moved successfully!")
                            
                            # Check for win condition
                            if game.check_win(current_player):
                                st.balloons()
                                st.success(f"🏆 {current_player.name} wins!")
                            else:
                                # Next turn if not a 6
                                if st.session_state.dice_value != 6:
                                    game.next_turn()
                                    st.info("Next player's turn!")
                                else:
                                    st.info("🎲 Roll again! (You got a 6)")
                            
                            st.session_state.dice_value = None
                            st.rerun()
                        else:
                            st.error("❌ Invalid move! Try again.")
                else:
                    st.warning("⚠️ No valid moves available!")
                    if st.button("⏭️ Skip Turn", use_container_width=True):
                        game.next_turn()
                        st.session_state.dice_value = None
                        st.info("Turn skipped!")
                        st.rerun()
        
        # Token positions detail
        st.markdown("### 📍 Token Details")
        for player in game.players:
            with st.expander(f"{player.name} ({player.color}) - {player.tokens_finished}/4 finished"):
                for i, token in enumerate(player.tokens):
                    if token.position == -1:
                        pos_text = "🏠 Home"
                    elif token.position >= 100:
                        pos_text = f"🏁 Home Stretch {token.position - 100}/5"
                    elif token.position == 105:
                        pos_text = "🏆 Finished!"
                    else:
                        pos_text = f"🎯 Position {token.position}"
                    
                    st.write(f"Token {i+1}: {pos_text}")

# Game rules section
with st.expander("📜 How to Play Ludo"):
    st.markdown("""
    ### 🎯 Objective
    Be the first player to move all 4 tokens from home to the finish area!
    
    ### 🎲 Basic Rules
    1. **Starting**: Roll a 6️⃣ to move a token out of home
    2. **Movement**: Tokens move clockwise around the board
    3. **Capturing**: Land on opponent's token to send it back home
    4. **Safe Zones**: 🟡 Golden squares protect tokens from capture
    5. **Extra Turns**: Rolling a 6️⃣ gives you another turn
    6. **Winning**: Get all 4 tokens to the center finish area
    
    ### 🎮 Controls
    - 🎲 **Roll Dice**: Click to roll and see your number
    - 🔄 **Select Token**: Choose which token to move
    - ✅ **Move**: Execute the move
    - 🆕 **New Game**: Start fresh anytime
    
    ### 🏆 Strategy Tips
    - Prioritize getting tokens out of home
    - Use captures to slow opponents
    - Protect tokens in safe zones
    - Plan moves to avoid opponent captures
    """)

# Footer
st.markdown("---")
st.markdown("*🎲 Built with Streamlit • Enjoy your game! 🎉*")
