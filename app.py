import streamlit as st
import random
import time
import plotly.graph_objects as go
import math

# Page configuration
st.set_page_config(
    page_title="🐦 Flappy Bird Game",
    page_icon="🐦",
    layout="wide"
)

# Game constants
BIRD_SIZE = 30
PIPE_WIDTH = 80
PIPE_GAP = 150
PIPE_SPEED = 4
GRAVITY = 1.2
JUMP_STRENGTH = -15
GAME_WIDTH = 800
GAME_HEIGHT = 600
BIRD_X = 150

# Initialize game state
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'menu'
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
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0

def create_pipe(x_position):
    """Create a new pipe with random gap position"""
    gap_y = random.randint(150, GAME_HEIGHT - PIPE_GAP - 150)
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
    if st.session_state.bird_y < BIRD_SIZE:
        st.session_state.bird_y = BIRD_SIZE
        st.session_state.game_state = 'game_over'
    elif st.session_state.bird_y > GAME_HEIGHT - BIRD_SIZE - 50:  # Account for ground
        st.session_state.bird_y = GAME_HEIGHT - BIRD_SIZE - 50
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
    if not st.session_state.pipes or st.session_state.pipes[-1]['x'] < GAME_WIDTH - 250:
        st.session_state.pipes.append(create_pipe(GAME_WIDTH))

def check_collisions():
    """Check for collisions with pipes"""
    bird_left = BIRD_X - BIRD_SIZE//2
    bird_right = BIRD_X + BIRD_SIZE//2
    bird_top = st.session_state.bird_y - BIRD_SIZE//2
    bird_bottom = st.session_state.bird_y + BIRD_SIZE//2
    
    for pipe in st.session_state.pipes:
        pipe_left = pipe['x']
        pipe_right = pipe['x'] + PIPE_WIDTH
        
        # Check if bird is horizontally aligned with pipe
        if bird_right > pipe_left and bird_left < pipe_right:
            # Check collision with top pipe
            if bird_top < pipe['gap_y']:
                st.session_state.game_state = 'game_over'
                return
            
            # Check collision with bottom pipe
            if bird_bottom > pipe['gap_y'] + PIPE_GAP:
                st.session_state.game_state = 'game_over'
                return
        
        # Check if bird passed the pipe (for scoring)
        if pipe['x'] + PIPE_WIDTH < BIRD_X and not pipe['passed']:
            pipe['passed'] = True
            st.session_state.score += 1

def create_game_visual():
    """Create the game visualization with a visible bird"""
    fig = go.Figure()
    
    # Add sky background
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=GAME_WIDTH, y1=GAME_HEIGHT,
        fillcolor="skyblue",
        line=dict(width=0),
        layer="below"
    )
    
    # Add clouds for atmosphere
    cloud_positions = [(100, 500), (300, 480), (500, 520), (700, 490)]
    for cx, cy in cloud_positions:
        fig.add_shape(
            type="circle",
            x0=cx-30, y0=cy-15, x1=cx+30, y1=cy+15,
            fillcolor="white",
            line=dict(width=0),
            opacity=0.7,
            layer="below"
        )
    
    # Add pipes with better visibility
    for pipe in st.session_state.pipes:
        # Top pipe
        fig.add_shape(
            type="rect",
            x0=pipe['x'], y0=pipe['gap_y'],
            x1=pipe['x'] + PIPE_WIDTH, y1=GAME_HEIGHT,
            fillcolor="darkgreen",
            line=dict(color="green", width=3)
        )
        
        # Top pipe cap
        fig.add_shape(
            type="rect",
            x0=pipe['x']-5, y0=pipe['gap_y']-20,
            x1=pipe['x'] + PIPE_WIDTH+5, y1=pipe['gap_y'],
            fillcolor="green",
            line=dict(color="darkgreen", width=2)
        )
        
        # Bottom pipe
        fig.add_shape(
            type="rect",
            x0=pipe['x'], y0=0,
            x1=pipe['x'] + PIPE_WIDTH, y1=pipe['gap_y'] - PIPE_GAP,
            fillcolor="darkgreen",
            line=dict(color="green", width=3)
        )
        
        # Bottom pipe cap
        fig.add_shape(
            type="rect",
            x0=pipe['x']-5, y0=pipe['gap_y'] - PIPE_GAP,
            x1=pipe['x'] + PIPE_WIDTH+5, y1=pipe['gap_y'] - PIPE_GAP + 20,
            fillcolor="green",
            line=dict(color="darkgreen", width=2)
        )
    
    # Add the bird - MAIN FIX: Proper bird visualization
    bird_angle = max(-30, min(30, st.session_state.bird_velocity * 2))  # Tilt based on velocity
    
    # Bird body (main circle)
    fig.add_trace(go.Scatter(
        x=[BIRD_X],
        y=[st.session_state.bird_y],
        mode='markers',
        marker=dict(
            size=BIRD_SIZE,
            color='gold',
            line=dict(color='orange', width=3),
            symbol='circle'
        ),
        showlegend=False,
        hoverinfo='skip',
        name='Bird Body'
    ))
    
    # Bird eye
    fig.add_trace(go.Scatter(
        x=[BIRD_X + 8],
        y=[st.session_state.bird_y + 5],
        mode='markers',
        marker=dict(
            size=8,
            color='white',
            line=dict(color='black', width=2),
            symbol='circle'
        ),
        showlegend=False,
        hoverinfo='skip',
        name='Bird Eye'
    ))
    
    # Bird pupil
    fig.add_trace(go.Scatter(
        x=[BIRD_X + 10],
        y=[st.session_state.bird_y + 5],
        mode='markers',
        marker=dict(
            size=4,
            color='black',
            symbol='circle'
        ),
        showlegend=False,
        hoverinfo='skip',
        name='Bird Pupil'
    ))
    
    # Bird beak
    fig.add_trace(go.Scatter(
        x=[BIRD_X + 15, BIRD_X + 25, BIRD_X + 15],
        y=[st.session_state.bird_y, st.session_state.bird_y - 3, st.session_state.bird_y + 3],
        mode='lines',
        fill='toself',
        fillcolor='orange',
        line=dict(color='darkorange', width=2),
        showlegend=False,
        hoverinfo='skip',
        name='Bird Beak'
    ))
    
    # Add ground
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=GAME_WIDTH, y1=50,
        fillcolor="saddlebrown",
        line=dict(color="brown", width=2)
    )
    
    # Add grass on ground
    fig.add_shape(
        type="rect",
        x0=0, y0=40, x1=GAME_WIDTH, y1=50,
        fillcolor="green",
        line=dict(width=0)
    )
    
    # Configure layout
    fig.update_layout(
        width=GAME_WIDTH,
        height=GAME_HEIGHT,
        xaxis=dict(
            range=[0, GAME_WIDTH],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[0, GAME_HEIGHT],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            fixedrange=True
        ),
        plot_bgcolor='skyblue',
        paper_bgcolor='skyblue',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        dragmode=False
    )
    
    return fig

def reset_game():
    """Reset game to initial state"""
    st.session_state.bird_y = GAME_HEIGHT // 2
    st.session_state.bird_velocity = 0
    st.session_state.pipes = []
    st.session_state.score = 0
    st.session_state.game_state = 'playing'
    st.session_state.frame_count = 0

def game_over():
    """Handle game over state"""
    if st.session_state.score > st.session_state.high_score:
        st.session_state.high_score = st.session_state.score

# Main game title with bird emoji
st.title("🐦 Flappy Bird Game - Now with Visible Bird!")
st.markdown("---")

# Game state handling
if st.session_state.game_state == 'menu':
    st.markdown("""
    ## 🎮 Welcome to Flappy Bird!
    
    ### 🐦 What You'll See:
    - **Golden Bird**: A bright yellow/gold bird with eyes and beak
    - **Green Pipes**: Obstacles to navigate through
    - **Blue Sky**: Beautiful background with clouds
    - **Real-time Movement**: Smooth bird physics and animation
    
    ### 🎯 How to Play:
    1. Click **"FLAP!"** to make the bird jump upward
    2. Avoid hitting the green pipes or the ground
    3. Pass through pipe gaps to score points
    4. Try to beat your high score!
    
    ### 🎮 Controls:
    - **FLAP Button**: Makes the bird jump (counteracts gravity)
    - Bird automatically falls due to gravity
    - Time your flaps to navigate through pipes
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 START GAME", type="primary", use_container_width=True):
            reset_game()
            st.rerun()

elif st.session_state.game_state == 'playing':
    # Game controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        if st.button("🐦 FLAP! (Make Bird Jump)", type="primary", use_container_width=True):
            bird_jump()
    
    with col2:
        st.metric("📊 Score", st.session_state.score)
    
    with col3:
        st.metric("🏆 High Score", st.session_state.high_score)
    
    with col4:
        if st.button("🔄 Reset Game", use_container_width=True):
            st.session_state.game_state = 'menu'
            st.rerun()
    
    # Game status
    st.info(f"🎮 **Game Active** - Bird Height: {int(st.session_state.bird_y)} | Velocity: {st.session_state.bird_velocity:.1f}")
    
    # Update game logic
    update_bird()
    update_pipes()
    check_collisions()
    
    # Display game
    fig = create_game_visual()
    st.plotly_chart(fig, use_container_width=True, key=f"game_{st.session_state.frame_count}")
    
    # Game tips
    st.markdown("💡 **Tip**: Click FLAP to make the golden bird jump up! Watch it fall and time your clicks to pass through the green pipe gaps.")
    
    # Auto-refresh for continuous gameplay
    if st.session_state.game_state == 'playing':
        st.session_state.frame_count += 1
        time.sleep(0.05)  # Faster refresh for smoother gameplay
        st.rerun()

elif st.session_state.game_state == 'game_over':
    st.error("💥 GAME OVER! The bird crashed!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎯 Final Score", st.session_state.score)
    with col2:
        st.metric("🏆 High Score", st.session_state.high_score)
    
    if st.session_state.score == st.session_state.high_score and st.session_state.score > 0:
        st.success("🏆 NEW HIGH SCORE! Congratulations!")
        st.balloons()
    
    # Show final game state with crashed bird
    fig = create_game_visual()
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("🔍 **Can you see the bird?** Look for the golden/yellow circle with eyes and an orange beak!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 PLAY AGAIN", type="primary", use_container_width=True):
            reset_game()
            st.rerun()
    
    with col2:
        if st.button("🏠 MAIN MENU", use_container_width=True):
            st.session_state.game_state = 'menu'
            st.rerun()

# Debug information
with st.expander("🔧 Game Debug Info (Check if bird is working)"):
    st.write(f"**Bird Position**: X={BIRD_X}, Y={st.session_state.bird_y}")
    st.write(f"**Bird Velocity**: {st.session_state.bird_velocity}")
    st.write(f"**Number of Pipes**: {len(st.session_state.pipes)}")
    st.write(f"**Game State**: {st.session_state.game_state}")
    st.write(f"**Frame Count**: {st.session_state.frame_count}")

# Game instructions
with st.expander("📖 Detailed Game Guide"):
    st.markdown("""
    ### 🐦 Bird Appearance
    The bird consists of:
    - **Main Body**: Large golden/yellow circle
    - **Eye**: White circle with black pupil
    - **Beak**: Orange triangular shape pointing right
    - **Position**: Always at X=150, Y varies based on your clicks
    
    ### 🎮 Gameplay Mechanics
    - **Gravity**: Bird constantly falls downward (velocity increases)
    - **Flapping**: Click FLAP to give upward momentum
    - **Physics**: Realistic momentum and gravity simulation
    - **Collision**: Game ends if bird touches pipes or ground
    
    ### 🏆 Scoring System
    - **1 Point**: For each pipe successfully passed
    - **High Score**: Automatically saved during session
    - **Challenge**: Try to beat your personal best!
    
    ### 💡 Pro Tips
    - Don't spam the FLAP button - use controlled, timed clicks
    - Watch the bird's velocity indicator to predict movement
    - Aim for the center of pipe gaps for safety margin
    - Stay calm and develop a rhythm
    """)

# Footer
st.markdown("---")
st.markdown("*🐦 Fixed Flappy Bird Game • Bird is now fully visible! • Built with Streamlit 🚀*")
