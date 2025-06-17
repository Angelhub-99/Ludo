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
if 'dice_rolled' not in st.session_state:
    st.session_state.dice_rolled = False

game = st.session_state.game

def create_traditional_ludo_board():
    """Create a traditional Ludo board layout matching the image"""
    
    fig = go.Figure()
    
    # Define the traditional Ludo board positions
    # The board is 15x15 grid with specific colored areas
    
    # Create the main board structure
    board_size = 15
    
    # Define color zones based on traditional Ludo layout
    red_home = [(i, j) for i in range(1, 6) for j in range(1, 6)]
    blue_home = [(i, j) for i in range(1, 6) for j in range(9, 14)]
    yellow_home = [(i, j) for i in range(9, 14) for j in range(1, 6)]
    green_home = [(i, j) for i in range(9, 14) for j in range(9, 14)]
    
    # Define the main track positions
    main_track = []
    
    # Bottom row (red to blue)
    for j in range(6, 9):
        main_track.append((0, j))
    
    # Right column (blue area)
    for i in range(1, 6):
        main_track.append((i, 8))
    
    # Top-right to top-left
    for j in range(8, 5, -1):
        main_track.append((6, j))
    
    # Continue building the track...
    # This creates the traditional 52-square path
    
    # Add colored home areas
    colors = ['red', 'blue', 'yellow', 'green']
    home_areas = [red_home, blue_home, yellow_home, green_home]
    
    for color, home_area in zip(colors, home_areas):
        x_coords = [pos[1] for pos in home_area]
        y_coords = [14-pos[0] for pos in home_area]  # Flip Y for proper display
        
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=20,
                color=color,
                opacity=0.7,
                symbol='square'
            ),
            name=f'{color.title()} Home',
            showlegend=False
        ))
    
    # Add tokens on the board
    for player in game.players:
        token_positions = []
        for i, token in enumerate(player.tokens):
            if token.position == -1:  # In home
                # Place in home area
                if player.color == 'red':
                    token_positions.append((2, 12))
                elif player.color == 'blue':
                    token_positions.append((11, 12))
                elif player.color == 'yellow':
                    token_positions.append((11, 2))
                elif player.color == 'green':
                    token_positions.append((2, 2))
            elif token.position > 0:
                # Calculate position on main track
                pos = get_board_coordinates(token.position)
                if pos:
                    token_positions.append(pos)
        
        if token_positions:
            x_coords = [pos[0] for pos in token_positions]
            y_coords = [pos[1] for pos in token_positions]
            
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=player.color,
                    line=dict(color='black', width=2),
                    symbol='circle'
                ),
                text=[f'{player.name[0]}{i+1}' for i in range(len(token_positions))],
                textposition="middle center",
                textfont=dict(size=8, color='white'),
                name=f'{player.name} Tokens',
                showlegend=False
            ))
    
    # Add the center finish area
    fig.add_trace(go.Scatter(
        x=[7],
        y=[7],
        mode='markers+text',
        marker=dict(
            size=40,
            color='gold',
            symbol='star'
        ),
        text='FINISH',
        textposition="middle center",
        textfont=dict(size=10, color='black'),
        showlegend=False
    ))
    
    # Add grid lines to show the board structure
    for i in range(16):
        fig.add_shape(
            type="line",
            x0=i-0.5, y0=-0.5, x1=i-0.5, y1=14.5,
            line=dict(color="lightgray", width=1)
        )
        fig.add_shape(
            type="line",
            x0=-0.5, y0=i-0.5, x1=14.5, y1=i-0.5,
            line=dict(color="lightgray", width=1)
        )
    
    fig.update_layout(
        title="🎲 Traditional Ludo Board",
        showlegend=False,
        width=600,
        height=600,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, 15]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, 15]
        ),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def get_board_coordinates(position):
    """Convert game position to board coordinates"""
    # This maps the 52 positions to actual board coordinates
    # Based on traditional Ludo layout
    position_map = {
        1: (6, 1), 2: (6, 2), 3: (6, 3), 4: (6, 4), 5: (6, 5),
        6: (6, 6), 7: (5, 6), 8: (4, 6), 9: (3, 6), 10: (2, 6),
        11: (1, 6), 12: (0, 6), 13: (0, 7), 14: (0, 8),
        # Continue mapping all 52 positions...
    }
    return position_map.get(position, None)

def create_dice_display():
    """Create a large, visible dice display for all players"""
    if st.session_state.dice_value:
        # Create a large dice visualization
        dice_faces = {
            1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"
        }
        
        dice_html = f"""
        <div style="
            text-align: center;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            padding: 30px;
            border-radius: 20px;
            margin: 20px 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        ">
            <h2 style="color: white; margin: 0; font-size: 24px;">🎲 DICE ROLLED!</h2>
            <div style="
                font-size: 120px;
                color: white;
                margin: 20px 0;
                text-shadow: 4px 4px 8px rgba(0,0,0,0.5);
            ">
                {dice_faces[st.session_state.dice_value]}
            </div>
            <h3 style="color: white; margin: 0; font-size: 32px;">
                {st.session_state.dice_value}
            </h3>
            <p style="color: white; margin: 10px 0; font-size: 18px;">
                {game.current_player().name}'s Turn
            </p>
        </div>
        """
        return dice_html
    return ""

# Main title
st.title("🎲 Traditional Ludo Game")
st.markdown("---")

# Large dice display visible to all players
dice_display = create_dice_display()
if dice_display:
    st.markdown(dice_display, unsafe_allow_html=True)

# Sidebar for game controls
with st.sidebar:
    st.header("🎮 Game Controls")
    
    # Game setup
    st.subheader("Game Setup")
    num_players = st.selectbox("Number of Players", [2, 3, 4], index=2)
    
    if st.button("🆕 New Game", type="primary"):
        st.session_state.game = Game(num_players=num_players)
        st.session_state.dice_value = None
        st.session_state.dice_rolled = False
        st.session_state.game_started = True
        game = st.session_state.game
        st.rerun()
    
    # Game status
    if st.session_state.game_started:
        st.subheader("🎯 Current Turn")
        current_player = game.current_player()
        
        # Highlight current player with colored background
        player_color = current_player.color
        st.markdown(f"""
        <div style="
            background-color: {player_color};
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
        ">
            <h3 style="margin: 0;">{current_player.name}</h3>
            <p style="margin: 5px 0;">({player_color.title()} Player)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show last dice roll prominently
        if st.session_state.dice_value:
            st.markdown(f"""
            <div style="
                background: gold;
                color: black;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                font-size: 18px;
                font-weight: bold;
            ">
                Last Roll: {st.session_state.dice_value}
            </div>
            """, unsafe_allow_html=True)

# Main game area
if not st.session_state.game_started:
    st.info("👆 Click 'New Game' in the sidebar to start playing!")
    
    # Show game preview
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🎯 Game Preview")
        # Show empty board
        fig = create_traditional_ludo_board()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        ## 🎲 How to Play
        
        1. **Roll Dice** - Click to roll for your turn
        2. **Move Tokens** - Select which token to move
        3. **Capture Opponents** - Land on their tokens
        4. **Reach Finish** - Get all tokens to center
        5. **Win the Game** - First to finish wins!
        
        ### 🏆 Special Rules
        - Roll **6** to get tokens out of home
        - Roll **6** to get an extra turn
        - **Safe zones** protect your tokens
        """)

else:
    # Check for game over
    if game.game_over:
        st.success(f"🎉 Game Over! {game.winner.name} ({game.winner.color}) wins!")
        st.balloons()
        if st.button("🔄 Play Again", type="primary"):
            st.session_state.game = Game(num_players=num_players)
            st.session_state.dice_value = None
            st.session_state.dice_rolled = False
            st.session_state.game_started = True
            st.rerun()
    
    # Create layout columns
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        st.subheader("🎯 Game Board")
        
        # Display the traditional Ludo board
        fig = create_traditional_ludo_board()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎮 Game Actions")
        
        if not game.game_over:
            current_player = game.current_player()
            
            # Dice rolling section - PROMINENT DISPLAY
            st.markdown("### 🎲 Roll Dice")
            
            # Large, prominent dice roll button
            if st.button(
                f"🎲 {current_player.name} - ROLL DICE!", 
                type="primary", 
                use_container_width=True,
                help=f"Click to roll dice for {current_player.name}"
            ):
                st.session_state.dice_value = roll_dice()
                st.session_state.dice_rolled = True
                
                # Show immediate feedback
                st.success(f"🎲 {current_player.name} rolled: **{st.session_state.dice_value}**")
                
                # Add sound effect simulation
                if st.session_state.dice_value == 6:
                    st.info("🔥 LUCKY SIX! You get another turn!")
                
                st.rerun()
            
            # Token movement section
            if st.session_state.dice_value and st.session_state.dice_rolled:
                st.markdown("### 🔄 Move Your Token")
                
                movable_tokens = game.get_movable_tokens(current_player, st.session_state.dice_value)
                
                if movable_tokens:
                    # Show token options with current positions
                    token_options = []
                    for i in movable_tokens:
                        token = current_player.tokens[i]
                        if token.position == -1:
                            pos_text = "🏠 Home"
                        elif token.position >= 100:
                            pos_text = f"🏁 Home Stretch {token.position - 100}/5"
                        else:
                            pos_text = f"🎯 Position {token.position}"
                        token_options.append(f"Token {i+1} - {pos_text}")
                    
                    selected_option = st.selectbox(
                        "Choose your token:",
                        token_options,
                        help="Select which token you want to move"
                    )
                    selected_token_idx = movable_tokens[token_options.index(selected_option)]
                    
                    if st.button("✅ MOVE TOKEN", type="secondary", use_container_width=True):
                        success = game.move_token(current_player, selected_token_idx, st.session_state.dice_value)
                        
                        if success:
                            st.success("🎯 Token moved successfully!")
                            
                            # Check for win condition
                            if game.check_win(current_player):
                                st.balloons()
                                st.success(f"🏆 {current_player.name} WINS THE GAME!")
                            else:
                                # Next turn logic
                                if st.session_state.dice_value != 6:
                                    game.next_turn()
                                    st.info("➡️ Next player's turn!")
                                else:
                                    st.info("🎲 Roll again! (You got a 6)")
                            
                            # Reset dice state
                            st.session_state.dice_value = None
                            st.session_state.dice_rolled = False
                            st.rerun()
                        else:
                            st.error("❌ Invalid move! Try again.")
                else:
                    st.warning("⚠️ No valid moves available!")
                    if st.button("⏭️ Skip Turn", use_container_width=True):
                        game.next_turn()
                        st.session_state.dice_value = None
                        st.session_state.dice_rolled = False
                        st.info("Turn skipped!")
                        st.rerun()
        
        # Player statistics
        st.markdown("### 📊 Player Status")
        for player in game.players:
            is_current = player == game.current_player()
            status_color = "🔥" if is_current else "👤"
            
            with st.expander(f"{status_color} {player.name} ({player.color})", expanded=is_current):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("🏠 Home", player.tokens_in_home)
                    st.metric("🎯 Playing", player.tokens_in_play)
                with col_b:
                    st.metric("🏁 Finished", player.tokens_finished)
                    progress = player.tokens_finished / 4
                    st.progress(progress)

# Game rules section
with st.expander("📜 Ludo Game Rules"):
    st.markdown("""
    ## 🎯 How to Win
    Move all 4 tokens from home to the center finish area!
    
    ## 🎲 Game Rules
    
    ### Starting the Game
    - Roll a **6** to move a token out of home base
    - Tokens move clockwise around the board
    
    ### Moving Tokens
    - Roll dice and move any token the number shown
    - You can choose which token to move
    - Tokens must move the exact number rolled
    
    ### Special Rules
    - **Rolling 6**: Get an extra turn
    - **Capturing**: Land on opponent's token to send it home
    - **Safe Zones**: Golden squares protect from capture
    - **Home Stretch**: Final 5 squares before finish
    
    ### Winning
    - First player to get all 4 tokens to finish wins!
    - Tokens must reach the center by exact count
    """)

# Footer
st.markdown("---")
st.markdown("*🎲 Traditional Ludo Game • Built with Streamlit 🚀*")
