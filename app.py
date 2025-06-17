import streamlit as st
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
    st.session_state.game = Game(num_players=4)  # Default to 4 players
if 'dice_value' not in st.session_state:
    st.session_state.dice_value = None
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

game = st.session_state.game

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
        st.write(f"**Current Player:** {game.current_player().name}")
        st.write(f"**Player Color:** {game.current_player().color}")
        
        # Display dice value if rolled
        if st.session_state.dice_value:
            st.write(f"**Last Roll:** {st.session_state.dice_value}")

# Main game area
if not st.session_state.game_started:
    st.info("👆 Click 'New Game' in the sidebar to start playing!")
else:
    # Create two columns for game layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Game Board")
        
        # Display board image (placeholder)
        try:
            st.image('assets/ludo_board.png', caption='Ludo Board', use_column_width=True)
        except:
            st.warning("Board image not found. Place 'ludo_board.png' in the 'assets/' folder.")
            # Create a placeholder board representation
            st.markdown("""
            ```
            [LUDO BOARD PLACEHOLDER]
            
            Home Areas:    [R] [B]
                          [G] [Y]
            
            Main Track: 52 squares around the board
            ```
            """)
    
    with col2:
        st.subheader("🎮 Game Actions")
        
        # Dice rolling section
        st.markdown("### 🎲 Roll Dice")
        if st.button("Roll Dice", type="primary", use_container_width=True):
            st.session_state.dice_value = roll_dice()
            st.success(f"🎲 You rolled a **{st.session_state.dice_value}**!")
            st.rerun()
        
        # Token movement section
        if st.session_state.dice_value:
            st.markdown("### 🔄 Move Token")
            
            current_player = game.current_player()
            movable_tokens = game.get_movable_tokens(current_player, st.session_state.dice_value)
            
            if movable_tokens:
                token_options = [f"Token {i+1}" for i in range(len(movable_tokens))]
                selected_token = st.selectbox("Select a token to move:", token_options)
                
                if st.button("Move Selected Token", use_container_width=True):
                    token_index = token_options.index(selected_token)
                    success = game.move_token(current_player, token_index, st.session_state.dice_value)
                    
                    if success:
                        st.success(f"Token moved successfully!")
                        
                        # Check for win condition
                        if game.check_win(current_player):
                            st.balloons()
                            st.success(f"🎉 {current_player.name} wins the game!")
                        else:
                            # Move to next turn if not a 6
                            if st.session_state.dice_value != 6:
                                game.next_turn()
                        
                        st.session_state.dice_value = None
                        st.rerun()
                    else:
                        st.error("Invalid move! Try again.")
            else:
                st.info("No tokens can be moved with this dice value.")
                if st.button("Skip Turn", use_container_width=True):
                    game.next_turn()
                    st.session_state.dice_value = None
                    st.rerun()

# Game information section
if st.session_state.game_started:
    st.markdown("---")
    st.subheader("📊 Player Information")
    
    # Create columns for each player
    player_cols = st.columns(len(game.players))
    
    for i, player in enumerate(game.players):
        with player_cols[i]:
            # Highlight current player
            if player == game.current_player():
                st.markdown(f"### 🔥 {player.name} (Current)")
            else:
                st.markdown(f"### {player.name}")
            
            st.write(f"**Color:** {player.color}")
            st.write(f"**Tokens in Home:** {player.tokens_in_home}")
            st.write(f"**Tokens in Play:** {player.tokens_in_play}")
            st.write(f"**Tokens Finished:** {player.tokens_finished}")

# Game rules section (collapsible)
with st.expander("📜 Game Rules"):
    st.markdown("""
    ### How to Play Ludo:
    
    1. **Starting:** Roll a 6 to move a token out of home
    2. **Movement:** Move tokens clockwise around the board
    3. **Capturing:** Land on opponent's token to send it back home
    4. **Safe Zones:** Colored squares are safe from capture
    5. **Winning:** Get all 4 tokens to the center finish area
    6. **Extra Turn:** Roll a 6 to get another turn
    
    ### Controls:
    - Click "Roll Dice" to roll
    - Select a token from the dropdown
    - Click "Move Selected Token" to move
    - Use sidebar to start a new game
    """)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit 🚀*")
