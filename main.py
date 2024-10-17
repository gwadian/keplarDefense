import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 1075, 683
PLAYER_SIZE = 35
ROCK_SIZE = 35
BULLET_SIZE = 15
PLAYER_COLOR = (255, 255, 255)  # white for the player
ROCK_COLOR = (46, 46, 46)  # dark grey for rocks
PLAYER_BULLET_COLOR = (0, 255, 0)  # green for player bullets
ROCK_BULLET_COLOR = (255, 0, 0)  # red for rock bullets
BG_COLOR = (0, 0, 0)  # black for the sky
FPS = 100
ROCK_FALL_SPEED = 2
ROCK_SPAWN_INTERVAL = 25  # Number of frames between rock spawns
BULLET_SPEED = 50
ROCK_BULLET_SPEED = 25
BULLET_COOLDOWN = 0.2  # seconds
ROCK_SHOOT_INTERVAL = 0  # Number of frames between rock shots
ROCK_SHOOT_COOLDOWN = 1.2  # seconds between rock shots
MAX_HITS = 10  # Number of hits before game over
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_COLOR = (0, 0, 255)  # Blue for health bar
HEALTH_BAR_BG_COLOR = (100, 100, 100)  # Gray for background of health

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Keplar defense")
# Initialize clock
clock = pygame.time.Clock()

# Player
player_pos = [WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT - PLAYER_SIZE]
player_speed = 6

# Rocks
rocks = []
rock_timer = 0

# Bullets
bullets = []
last_bullet_time = time.time()

# Rock Shots
rock_shots = []

# Health
player_health = MAX_HITS  # Start with maximum health

# Score
score = 0  # Initialize score

def draw_player():
    pygame.draw.rect(screen, PLAYER_COLOR, (*player_pos, PLAYER_SIZE, PLAYER_SIZE))

def draw_rocks():
    for rock in rocks:
        pygame.draw.rect(screen, ROCK_COLOR, (*rock['pos'], ROCK_SIZE, ROCK_SIZE))

def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, PLAYER_BULLET_COLOR, (*bullet['pos'], BULLET_SIZE, BULLET_SIZE))

def draw_rock_shots():
    for shot in rock_shots:
        pygame.draw.rect(screen, ROCK_BULLET_COLOR, (*shot['pos'], BULLET_SIZE, BULLET_SIZE))

def draw_health_bar():
    # Draw health bar background
    pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR, (10, 10, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
    # Calculate health bar fill width
    fill_width = (HEALTH_BAR_WIDTH * player_health) / MAX_HITS
    # Draw health bar fill
    pygame.draw.rect(screen, HEALTH_BAR_COLOR, (10, 10, fill_width, HEALTH_BAR_HEIGHT))

def draw_score():
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))  # Top right corner

def handle_input():
    global last_bullet_time
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_pos[0] -= player_speed
    if keys[pygame.K_d]:
        player_pos[0] += player_speed
    if keys[pygame.K_s]:
        current_time = time.time()
        if current_time - last_bullet_time >= BULLET_COOLDOWN:
            shoot_bullet()
            last_bullet_time = current_time

    # Ensure player stays within bounds
    player_pos[0] = max(0, min(WIDTH - PLAYER_SIZE, player_pos[0]))

def shoot_bullet():
    bullet_x = player_pos[0] + PLAYER_SIZE // 2 - BULLET_SIZE // 2
    bullet_y = player_pos[1] - BULLET_SIZE
    bullets.append({'pos': [bullet_x, bullet_y]})

def update_rocks():
    global rocks
    for rock in rocks:
        rock['pos'][1] += ROCK_FALL_SPEED

    rocks = [rock for rock in rocks if rock['pos'][1] < HEIGHT]

def update_bullets():
    global bullets
    for bullet in bullets:
        bullet['pos'][1] -= BULLET_SPEED

    bullets = [bullet for bullet in bullets if bullet['pos'][1] > -BULLET_SIZE]

def update_rock_shots():
    global rock_shots
    for shot in rock_shots:
        shot['pos'][1] += BULLET_SPEED

    rock_shots = [shot for shot in rock_shots if shot['pos'][1] < HEIGHT]

def check_bullet_rock_collisions():
    global rocks, bullets, score
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(*bullet['pos'], BULLET_SIZE, BULLET_SIZE)
        for rock in rocks[:]:
            rock_rect = pygame.Rect(*rock['pos'], ROCK_SIZE, ROCK_SIZE)
            if bullet_rect.colliderect(rock_rect):
                score += 1  # Increment score on hit
                bullets.remove(bullet)
                rocks.remove(rock)  # Remove the rock on hit
                break  # Exit the inner loop since we removed the rock

def check_rock_shot_collisions():
    global rock_shots, player_health
    for shot in rock_shots[:]:
        shot_rect = pygame.Rect(*shot['pos'], BULLET_SIZE, BULLET_SIZE)
        player_rect = pygame.Rect(*player_pos, PLAYER_SIZE, PLAYER_SIZE)
        if shot_rect.colliderect(player_rect):
            rock_shots.remove(shot)
            player_health -= 1
            if player_health <= 0:
                game_over()
            break

def check_player_rock_collisions():
    player_rect = pygame.Rect(*player_pos, PLAYER_SIZE, PLAYER_SIZE)
    for rock in rocks:
        rock_rect = pygame.Rect(*rock['pos'], ROCK_SIZE, ROCK_SIZE)
        if player_rect.colliderect(rock_rect):
            return True
    return False

def spawn_rock():
    x_pos = random.randint(0, WIDTH - ROCK_SIZE)
    rocks.append({'pos': [x_pos, -ROCK_SIZE], 'hit_count': 0})

def rock_shoot():
    current_time = time.time()
    for rock in rocks:
        if current_time - rock.get('last_shot_time', 0) >= ROCK_SHOOT_COOLDOWN:
            rock_x = rock['pos'][0] + ROCK_SIZE // 2 - BULLET_SIZE // 2
            rock_y = rock['pos'][1] + ROCK_SIZE
            rock_shots.append({'pos': [rock_x, rock_y]})
            rock['last_shot_time'] = current_time

def game_over():
    font = pygame.font.SysFont(None, 55)
    text = font.render('HEALTH CRITICAL, RETURNING TO HANGAR.', True, (255, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(2000)  # Wait for 2 seconds before closing
    pygame.quit()
    sys.exit()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    handle_input()

    rock_timer += 1
    if rock_timer >= ROCK_SPAWN_INTERVAL:
        spawn_rock()
        rock_timer = 0

    update_rocks()
    update_bullets()
    update_rock_shots()
    rock_shoot()

    check_bullet_rock_collisions()
    check_rock_shot_collisions()
    if check_player_rock_collisions():
        game_over()

    screen.fill(BG_COLOR)
    draw_rocks()
    draw_bullets()
    draw_rock_shots()
    draw_player()
    draw_health_bar()
    draw_score()  # Draw the score

    pygame.display.flip()
    clock.tick(FPS)
