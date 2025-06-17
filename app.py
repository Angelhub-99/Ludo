import streamlit as st
import random
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="🐦 Flappy Bird Game",
    page_icon="🐦",
    layout="wide"
)

# Game constants
BIRD_SIZE = 20
PIPE_WIDTH = 60
PIPE_GAP = 120
PIPE_SPEED = 3
GRAVITY = 0.8
JUMP_STRENGTH = -12
GAME_WIDTH = 800
GAME_HEIGHT = 600

# Initialize game state
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'menu'  # menu, playing, game_over
if 'bird_y' not in st.session_state:
    st.session_state.bird_y = GAME_HEIGHT // 2
if 'bird_velocity' not in st.session_state:
    st.session_state.bird_velocity = 0
if 'pipes' not in st.session_state:
    st.session_state.pipes = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'high_score' not in st.session_state:
    st.session_state.high_score = 0
if 'game_loop' not in st.session_state:
    st.session_state.game_loop = 0

def create_pipe(x_position):
    """Create a new pipe with random gap position"""
    gap_y = random.randint(100, GAME_HEIGHT - PIPE_GAP - 100)
    return {
        'x': x_position,
        'gap_y': gap_y,
        'passed': False
    }

def update_bird():
    """Update bird position and velocity"""
    st.session_state.bird_velocity += GRAVITY
    st.session_state.bird_y += st.session_state.bird_velocity
    
    # Keep bird within bounds
    if st.session_state.bird_y < 0:
        st.session_state.bird_y = 0
        st.session_state.bird_velocity = 0
    elif st.session_state.bird_y > GAME_HEIGHT - BIRD_SIZE:
        st.session_state.bird_y = GAME_HEIGHT - BIRD_SIZE
        st.session_state.game_state = 'game_over'

def bird_jump():
    """Make the bird jump"""
    st.session_state.bird_velocity = JUMP_STRENGTH

def update_pipes():
    """Update pipe positions and create new ones"""
    # Move existing pipes
    for pipe in st.session_state.pipes:
        pipe['x'] -= PIPE_SPEED
    
    # Remove pipes that are off screen
    st.session_state.pipes = [pipe for pipe in st.session_state.pipes if pipe['x'] > -PIPE_WIDTH]
    
    # Add new pipes
    if not st.session_state.pipes or st.session_state.pipes[-1]['x'] < GAME_WIDTH - 300:
        st.session_state.pipes.append(create_pipe(GAME_WIDTH))

def check_collisions():
    """Check for collisions with pipes or boundaries"""
    bird_x = 100
    bird_rect = {
        'left': bird_x,
        'right': bird_x + BIRD_SIZE,
        'top': st.session_state.bird_y,
        'bottom': st.session_state.bird_y + BIRD_SIZE
    }
    
    for pipe in st.session_state.pipes:
        pipe_rect_top = {
            'left': pipe['x'],
            'right': pipe['x'] + PIPE_WIDTH,
            'top': 0,
            'bottom': pipe['gap_y']
        }
        
        pipe_rect_bottom = {
            'left': pipe['x'],
            'right': pipe['x'] + PIPE_WIDTH,
            'top': pipe['gap_y'] + PIPE_GAP,
            'bottom': GAME_HEIGHT
        }
        
        # Check collision with top pipe
        if (bird_rect['right'] > pipe_rect_top['left'] and 
            bird_rect['left'] < pipe_rect_top['right'] and
            bird_rect['bottom'] > pipe_rect_top['top'] and
            bird_rect['top'] < pipe_rect_top['bottom']):
            st.session_state.game_state = 'game_over'
            return
        
        # Check collision with bottom pipe
        if (bird_rect['right'] > pipe_rect_bottom['left'] and 
            bird_rect['left'] < pipe_rect_bottom['right'] and
            bird_rect['bottom'] > pipe_rect_bottom['top'] and
            bird_rect['top'] < pipe_rect_bottom['bottom']):
            st.session_state.game_state = 'game_over'
            return
        
        # Check if bird passed the pipe (for scoring)
        if pipe['x'] + PIPE_WIDTH < bird_x and not pipe['passed']:
            pipe['passed'] = True
            st.session_state.score += 1

def create_game_visual():
    """Create the game visualization using Plotly"""
    fig = go.Figure()
    
    # Add background
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=GAME_WIDTH, y1=GAME_HEIGHT,
        fillcolor="lightblue",
        line=dict(width=0)
    )
    
    # Add pipes
    for pipe in st.session_state.pipes:
        # Top pipe
        fig.add_shape(
            type="rect",
            x0=pipe['x'], y0=0,
            x1=pipe['x'] + PIPE_WIDTH, y1=pipe['gap_y'],
            fillcolor="green",
            line=dict(color="darkgreen", width=2)
        )
        
        # Bottom pipe
        fig.add_shape(
            type="rect",
            x0=pipe['x'], y0=pipe['gap_y'] + PIPE_GAP,
            x1=pipe['x'] + PIPE_WIDTH, y1=GAME_HEIGHT,
            fillcolor="green",
            line=dict(color="darkgreen", width=2)
        )
    
    # Add bird
    fig.add_trace(go.Scatter(
        x=[100 + BIRD_SIZE//2],
        y=[GAME_HEIGHT - st.session_state.bird_y - BIRD_SIZE//2],
        mode='markers',
        marker=dict(
            size=BIRD_SIZE,
            color='yellow',
            symbol='circle',
            line=dict(color='orange', width=2)
        ),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add ground
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=GAME_WIDTH, y1=20,
        fillcolor="brown",
        line=dict(width=0)
    )
    
    fig.update_layout(
        width=GAME_WIDTH,
        height=GAME_HEIGHT,
        xaxis=dict(
            range=[0, GAME_WIDTH],
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            range=[0, GAME_HEIGHT],
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        plot_bgcolor='lightblue',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    
    return fig

def reset_game():
    """Reset game to initial state"""
    st.session_state.bird_y = GAME_HEIGHT // 2
    st.session_state.bird_velocity = 0
    st.session_state.pipes = []
    st.session_state.score = 0
    st.session_state.game_state = 'playing'

def game_over():
    """Handle game over state"""
    if st.session_state.score > st.session_state.high_score:
        st.session_state.high_score = st.session_state.score

# Main game title
st.title("🐦 Flappy Bird Game")
st.markdown("---")

# Game state handling
if st.session_state.game_state == 'menu':
    st.markdown("""
    ## 🎮 Welcome to Flappy Bird!
    
    ### How to Play:
    - Click **"FLAP!"** button to make the bird jump
    - Avoid hitting the green pipes
    - Try to get the highest score possible!
    
    ### Controls:
    - **FLAP Button**: Make the bird jump upward
    - **Start Game**: Begin playing
    - **Reset**: Start over anytime
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 START GAME", type="primary", use_container_width=True):
            reset_game()
            st.rerun()

elif st.session_state.game_state == 'playing':
    # Game controls
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("🐦 FLAP!", type="primary", use_container_width=True):
            bird_jump()
            st.rerun()
    
    with col2:
        st.metric("Score", st.session_state.score)
    
    with col3:
        st.metric("High Score", st.session_state.high_score)
    
    with col4:
        if st.button("🔄 RESET", use_container_width=True):
            st.session_state.game_state = 'menu'
            st.rerun()
    
    # Update game logic
    update_bird()
    update_pipes()
    check_collisions()
    
    # Display game
    fig = create_game_visual()
    st.plotly_chart(fig, use_container_width=True)
    
    # Auto-refresh for continuous gameplay
    if st.session_state.game_state == 'playing':
        time.sleep(0.1)
        st.rerun()

elif st.session_state.game_state == 'game_over':
    st.error("💥 GAME OVER!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Final Score", st.session_state.score)
    with col2:
        st.metric("High Score", st.session_state.high_score)
    
    if st.session_state.score == st.session_state.high_score and st.session_state.score > 0:
        st.success("🏆 NEW HIGH SCORE!")
        st.balloons()
    
    # Show final game state
    fig = create_game_visual()
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 PLAY AGAIN", type="primary", use_container_width=True):
            reset_game()
            st.rerun()
    
    with col2:
        if st.button("🏠 MAIN MENU", use_container_width=True):
            st.session_state.game_state = 'menu'
            st.rerun()

# Game instructions
with st.expander("📖 Game Instructions"):
    st.markdown("""
    ### 🎯 Objective
    Navigate the yellow bird through the green pipes without crashing!
    
    ### 🎮 Controls
    - **FLAP Button**: Makes the bird jump upward
    - The bird falls down due to gravity
    - Time your flaps to pass through pipe gaps
    
    ### 🏆 Scoring
    - Earn 1 point for each pipe you successfully pass
    - Try to beat your high score!
    
    ### 💡 Tips
    - Don't flap too much - small, timed flaps work best
    - Watch the bird's momentum and plan ahead
    - Stay calm and focused for higher scores
    """)

# Footer
st.markdown("---")
st.markdown("*🐦 Flappy Bird Game • Built with Streamlit • Have Fun! 🎮*")
