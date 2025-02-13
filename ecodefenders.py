import pygame
import random
import math
import os
import numpy as np
import time
import cv2 as cv

pygame.init()

pygame.display.set_icon(pygame.image.load('./interface/player.png'))

shoot_sound = pygame.mixer.Sound("./sons/disparo.mp3")
shoot_sound.set_volume(0.04)

die_sound = pygame.mixer.Sound("./sons/morte.mp3")
die_sound.set_volume(0.1)

damage_sound = pygame.mixer.Sound("./sons/dano.mp3")
damage_sound.set_volume(0.1)

screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Eco Defenders")
clock = pygame.time.Clock()
status = 'nao'
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

player_width = 50
player_height = 50
player_size = (player_width + player_height) // 2
player_pos = [screen_width // 2, screen_height // 2]
player_speed = 5
player_blink_timer = 0


bullets = []
bullet_speed = 8
player_shooting_speed = 20
player_projectiles = 1

enemy_size = 60
boss_size = 100
enemies = []
enemy_speed = 2

game_start_time = None

enemy_images = [
    pygame.image.load('./inimigos/sprite_1.png'),
    pygame.image.load('./inimigos/sprite_2.png'),
    pygame.image.load('./inimigos/sprite_3.png'),
    pygame.image.load('./inimigos/sprite_4.png'),
    pygame.image.load('./inimigos/sprite_5.png'),
    pygame.image.load('./inimigos/sprite_6.png'),
    pygame.image.load('./inimigos/sprite_7.png'),
    pygame.image.load('./inimigos/sprite_8.png'),
    pygame.image.load('./inimigos/sprite_9.png'),
    pygame.image.load('./inimigos/sprite_10.png'),
    pygame.image.load('./inimigos/sprite_12.png'),
    pygame.image.load('./inimigos/sprite_13.png'),
    pygame.image.load('./inimigos/sprite_14.png'),
    pygame.image.load('./inimigos/sprite_15.png'),
    pygame.image.load('./inimigos/sprite_16.png'),
    pygame.image.load('./inimigos/sprite_17.png'),
    pygame.image.load('./inimigos/sprite_18.png'),
    pygame.image.load('./inimigos/sprite_19.png'),
    pygame.image.load('./inimigos/sprite_20.png'),
    pygame.image.load('./inimigos/sprite_21.png'),
    pygame.image.load('./inimigos/sprite_22.png'),
    pygame.image.load('./inimigos/sprite_23.png'),
    pygame.image.load('./inimigos/sprite_24.png')
]

enemy_images = [pygame.transform.scale(img, (enemy_size, enemy_size)) for img in enemy_images]

enemy_boss = [
    pygame.image.load('./inimigos/sprite_11.png'),
]

enemy_boss = [pygame.transform.scale(img, (enemy_size, enemy_size)) for img in enemy_boss]

enemies = [
    {"pos": [random.randint(750, 1050), random.randint(0, 550)], "image": random.choice(enemy_images), "speed": enemy_speed, "size_factor": 1.0},
    {"pos": [random.randint(750, 1050), random.randint(0, 550)], "image": random.choice(enemy_images), "speed": enemy_speed, "size_factor": 1.0},
    {"pos": [random.randint(750, 1050), random.randint(0, 550)], "image": random.choice(enemy_images), "speed": enemy_speed, "size_factor": 1.0},
    {"pos": [random.randint(750, 1050), random.randint(0, 550)], "image": random.choice(enemy_images), "speed": enemy_speed, "size_factor": 1.0},
]

boss = {"pos": [random.randint(750, 1050), random.randint(0, 550)], "image": random.choice(enemy_boss), "speed": enemy_speed, "size_factor": 1.0}
boss_life = 45
boss_attack_cooldown = 10
boss_attack_timer = boss_attack_cooldown

growth_speed = 0.02
min_size_factor = 1.0
max_size_factor = 1.5

def draw_enemies():
    global growth_speed

    for enemy in enemies:
        if enemy["size_factor"] >= max_size_factor or enemy["size_factor"] <= min_size_factor:
            growth_speed *= -1

        enemy["size_factor"] += growth_speed
        
        if enemy["size_factor"] < min_size_factor:
            enemy["size_factor"] = min_size_factor
        elif enemy["size_factor"] > max_size_factor:
            enemy["size_factor"] = max_size_factor
        
        new_width = int(enemy_size * enemy["size_factor"])
        new_height = int(enemy_size * enemy["size_factor"])
        
        resized_image = pygame.transform.scale(enemy["image"], (new_width, new_height))
        
        screen.blit(resized_image, enemy["pos"])

score = 0
level = 1

player_lives = 3

def draw_lives():
    heart_img = pygame.image.load('./interface/coracao.png')
    heart_img = pygame.transform.scale(heart_img, (30, 26))

    for i in range(player_lives):
        screen.blit(heart_img, (10 + i * 30, 105))

enemies_killed = 0
wave = 1
enemies_to_next_wave = 30
projectiles = []

message = ""
message_timer = 0

game_active = False
wave_completed = False

shoot_timer = 0
shoot_delay = player_shooting_speed

def shoot_bullets():
    global shoot_timer
    if shoot_timer == 0 and player_projectiles > 0:
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - player_pos[0], my - player_pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        if distance == 0:
            dir_x, dir_y = 0, -1
        else:
            dir_x, dir_y = dx / distance, dy / distance

        for _ in range(player_projectiles):
            bullets.append({"pos": player_pos[:], "dir": [dir_x, dir_y]})
        
        shoot_sound.play()

        shoot_timer = shoot_delay

    if shoot_timer > 0:
        shoot_timer -= 1


def show_end_game_menu():
    global game_active, game_start_time, score
    font = pygame.font.Font('./fontes/tiny5.ttf', 40)
    
    elapsed_time = (pygame.time.get_ticks() - game_start_time) // 1000 
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    
    congratulation_message = "Parabéns! Você finalizou o jogo!"
    score_message = f"Seu score final: {score} - Tempo: {minutes}m {seconds}s"
    restart_message = "Pressione 'Espaço' para tentar novamente."
    exit_message = "Pressione 'Enter' para sair."

    while not game_active:
        screen.fill((0, 0, 0))
        
        text_score = font.render(score_message, True, (255, 255, 255))
        text_restart = font.render(restart_message, True, (255, 255, 255))
        text_exit = font.render(exit_message, True, (255, 255, 255))
        text_congratulation = font.render(congratulation_message, True, (255, 255, 255))

        screen.blit(text_congratulation, (screen_width // 2 - text_congratulation.get_width() // 2, screen_height // 2 - 100))
        screen.blit(text_score, (screen_width // 2 - text_score.get_width() // 2, screen_height // 4))
        screen.blit(text_restart, (screen_width // 2 - text_restart.get_width() // 2, screen_height // 2))
        screen.blit(text_exit, (screen_width // 2 - text_exit.get_width() // 2, screen_height // 1.5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    restart_game()
                    
                    game_active = True
                elif event.key == pygame.K_RETURN:
                    pygame.quit()
                    exit()


def restart_game():
    global wave, enemies_killed, enemies_to_next_wave, game_active, player_lives, score, shoot_delay, player_shooting_speed, game_start_time, boss_life, projectiles
    wave = 1
    enemies_killed = 0
    enemies_to_next_wave = 30
    player_lives = 3
    game_active = True
    enemies.clear()
    bullets.clear()
    score = 0
    boss_life = 30
    projectiles.clear()
    player_shooting_speed = 20
    shoot_delay = player_shooting_speed
    player_pos[:] = [screen_width // 2, screen_height // 2]
    game_start_time = pygame.time.get_ticks()


def check_wave_progress():
    global wave, enemies_to_next_wave, enemies_killed, wave_completed, message, message_timer, game_active, enemy_speed, spawn_rate
    
    if enemies_killed >= enemies_to_next_wave:
        wave += 1
        wave_completed = True

        if wave == 4:
            message = "Prepare-se, a próxima fase será uma batalha de boss!"
            message_timer = 180

        if wave > 5:
            game_active = False
            enemies_killed = 0
            enemies_to_next_wave = 30
            show_end_game_menu()
        
        upgrade_menu()
        
        enemies_killed = 0
        enemies_to_next_wave += 1
        
        enemy_speed += 0.2
        spawn_rate = max(15, spawn_rate - 2)

def handle_collisions():
    global score, player_lives, enemies_killed, player_blink_timer, game_active, message, message_timer, boss_life, wave
    
    if wave < 5:
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(*enemy["pos"], enemy_size, enemy_size)
            player_rect = pygame.Rect(*player_pos, player_size, player_size)
            
            if enemy_rect.colliderect(player_rect):
                if enemy in enemies:
                    enemies.remove(enemy)
                    die_sound.play()
                player_lives -= 1
                player_blink_timer = 30 
                message = "Voce foi atingido!"
                damage_sound.play()
                message_timer = 30
                if player_lives <= 0:
                    game_active = False

            for bullet in bullets[:]:
                bullet_rect = pygame.Rect(bullet["pos"][0] - 2, bullet["pos"][1] - 2, 4, 4)
                if enemy_rect.colliderect(bullet_rect):
                    if enemy in enemies:
                        enemies.remove(enemy)
                        die_sound.play()
                    if bullet in bullets:
                        bullets.remove(bullet)
                    score += 1
                    enemies_killed += 1
                    break
    else:
        boss_rect = pygame.Rect(*boss["pos"], enemy_size, enemy_size)
        player_rect = pygame.Rect(*player_pos, player_size, player_size)
        
        if boss_rect.colliderect(player_rect):
            player_lives -= 1
            player_blink_timer = 30
            if player_lives <= 0:
                game_active = False
        
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet["pos"][0] - 2, bullet["pos"][1] - 2, 4, 4)
            if boss_rect.colliderect(bullet_rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                boss_life -= 1
                damage_sound.play()
                if boss_life <= 0:
                    score += 10
                    game_active = False
                    wave = 1
                    enemies.clear()
                    show_end_game_menu()

boss_image = pygame.image.load('./inimigos/boss.png') 
boss_image = pygame.transform.scale(boss_image, (boss_size, boss_size))
boss_angle = 3

def move_boss():
    global boss_angle

    orbit_distance = 300
    orbit_speed = 0.020

    boss["pos"][0] = player_pos[0] + math.cos(boss_angle) * orbit_distance
    boss["pos"][1] = player_pos[1] + math.sin(boss_angle) * orbit_distance

    boss_angle += orbit_speed


def boss_attack():
    global boss_attack_timer, player_lives, message, message_timer, projectiles

    if boss_attack_timer <= 0:
        dx = player_pos[0] - boss["pos"][0]  
        dy = player_pos[1] - boss["pos"][1]  
        distance = math.sqrt(dx**2 + dy**2)  

        if distance != 0:
            direction_x = dx / distance
            direction_y = dy / distance
        else:
            direction_x = 0
            direction_y = 0

        projectiles.append({
            "pos": boss["pos"].copy(),
            "speed": 5,
            "color": (255, 0, 0),
            "direction": (direction_x, direction_y)
        })

        boss_attack_timer = boss_attack_cooldown
    else:
        boss_attack_timer -= 1


def draw_boss_health():
    screen.blit(boss_image, boss["pos"])
    
    pygame.draw.rect(screen, (255, 0, 0), (boss["pos"][0], boss["pos"][1] - 20, enemy_size, 10))
    pygame.draw.rect(screen, (0, 255, 0), (boss["pos"][0], boss["pos"][1] - 20, enemy_size * (boss_life / 10), 10))

    font = pygame.font.Font('./fontes/tiny5.ttf', 20)
    text = font.render(f"Vida: {boss_life}", True, (255, 255, 255))
    screen.blit(text, (boss["pos"][0], boss["pos"][1] - 40))

def draw_interface():
    font = pygame.font.Font('./fontes/tiny5.ttf', 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    wave_text = font.render(f"Wave: {wave}", True, WHITE)

    if game_start_time is not None:
        elapsed_time_ms = pygame.time.get_ticks() - game_start_time
        elapsed_time_sec = elapsed_time_ms // 1000
        elapsed_minutes = elapsed_time_sec // 60
        elapsed_seconds = elapsed_time_sec % 60
        time_text = font.render(f"Tempo: {elapsed_minutes:02}:{elapsed_seconds:02}", True, WHITE)
        screen.blit(time_text, (screen_width - time_text.get_width() - 10, 10))

    screen.blit(score_text, (10, 10))
    screen.blit(wave_text, (10, 50))
    draw_lives()


def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x, y = random.randint(0, screen_width), -enemy_size
    elif side == "bottom":
        x, y = random.randint(0, screen_width), screen_height + enemy_size
    elif side == "left":
        x, y = -enemy_size, random.randint(0, screen_height)
    else:
        x, y = screen_width + enemy_size, random.randint(0, screen_height)
    
    size_factor = random.uniform(0.8, 1.2)
    speed = enemy_speed * size_factor
    enemies.append({"pos": [x, y], "speed": speed, "image": random.choice(enemy_images), "size_factor": size_factor})



player_image = pygame.image.load('./interface/player.png')
player_image = pygame.transform.scale(player_image, (player_width, player_height))

def draw_player():
    global player_blink_timer

    if player_blink_timer > 0:
        image_to_draw = pygame.image.load("./interface/player_dano.png").convert_alpha()
        image_to_draw = pygame.transform.scale(image_to_draw, (player_width, player_height))
        player_blink_timer -= 1
    else:
        image_to_draw = player_image

    mouse_x, mouse_y = pygame.mouse.get_pos()
    delta_x = mouse_x - player_pos[0]
    delta_y = mouse_y - player_pos[1]
    angle = math.degrees(math.atan2(delta_y, delta_x))

    rotated_image = pygame.transform.rotate(image_to_draw, -angle)
    rotated_rect = rotated_image.get_rect()
    rotated_rect.centerx = player_pos[0]
    rotated_rect.top = player_pos[1]

    screen.blit(rotated_image, rotated_rect.topleft)

    
def draw_bullets():
    for bullet in bullets:
        pygame.draw.circle(screen, WHITE, bullet["pos"], 5)
    for projectile in projectiles:
        pygame.draw.circle(screen, projectile["color"], projectile["pos"], 5)


def move_projectiles():
    global projectiles

    for projectile in projectiles:
        projectile["pos"][0] += projectile["direction"][0] * projectile["speed"]
        projectile["pos"][1] += projectile["direction"][1] * projectile["speed"]

        pygame.draw.circle(screen, projectile["color"], (int(projectile["pos"][0]), int(projectile["pos"][1])), 5)


def move_player(keys):
    if keys[pygame.K_w] or keys[pygame.K_UP] and player_pos[1] > 0:
        player_pos[1] -= player_speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN] and player_pos[1] < screen_height - player_size:
        player_pos[1] += player_speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= player_speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT] and player_pos[0] < screen_width - player_size:
        player_pos[0] += player_speed

    player_pos[0] = max(0, min(player_pos[0], screen_width - player_width))
    player_pos[1] = max(0, min(player_pos[1], screen_height - player_height))

def move_bullets():
    for bullet in bullets[:]:
        bullet["pos"][0] += bullet["dir"][0] * bullet_speed
        bullet["pos"][1] += bullet["dir"][1] * bullet_speed
        if not (0 <= bullet["pos"][0] <= screen_width and 0 <= bullet["pos"][1] <= screen_height):
            if bullet in bullets:
                bullets.remove(bullet)

    for projectile in projectiles[:]: 
        projectile["pos"][0] += projectile["speed"]
        if not (0 <= projectile["pos"][0] <= screen_width and 0 <= projectile["pos"][1] <= screen_height):
            projectiles.remove(projectile)

def move_enemies():
    for enemy in enemies:
        dx, dy = player_pos[0] - enemy["pos"][0], player_pos[1] - enemy["pos"][1]
        distance = math.sqrt(dx**2 + dy**2)
        if distance != 0:
            dx, dy = dx / distance, dy / distance
            enemy["pos"][0] += dx * enemy["speed"]
            enemy["pos"][1] += dy * enemy["speed"]

def upgrade_menu():
    global player_lives, player_shooting_speed, player_projectiles, wave_completed, enemies_killed, shoot_delay
    font = pygame.font.Font('./fontes/tiny5.ttf', 24)
    
    options = [
        f"1. Mais {wave} corações",
        f"2. Aumentar velocidade de tiro em {wave * 2}%",
        f"3. Matar todos os inimigos (usável apenas uma vez)"
    ]
    
    screen.fill(BLACK)
    for i, option in enumerate(options):
        text = font.render(option, True, WHITE)
        screen.blit(text, (screen_width // 2 - 320, screen_height // 2 + i * 30))
    
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player_lives += wave
                    waiting = False
                elif event.key == pygame.K_2:
                    shoot_delay = max(1, shoot_delay - wave * 2)
                    waiting = False
                elif event.key == pygame.K_3:
                    enemies.clear()
                    enemies_killed = enemies_to_next_wave
                    waiting = False

def draw_message():
    global message, message_timer
    if message_timer > 0:
        font = pygame.font.Font('./fontes/tiny5.ttf', 48)
        text_surface = font.render(message, True, RED)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(text_surface, text_rect)
        message_timer -= 1

def show_game_over_menu():
    global message, status
    font = pygame.font.Font('./fontes/tiny5.ttf', 72)
    game_over_text = font.render("Game Over", True, RED)
    message = ""
    retry_text = pygame.font.Font('./fontes/tiny5.ttf', 26).render("Aperte espaço para tentar novamente ou enter para voltar ao menu principal", True, WHITE)

    game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    retry_rect = retry_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(retry_text, retry_rect)

    if(pygame.key.get_pressed()[pygame.K_SPACE]):
        restart_game()

    if(pygame.key.get_pressed()[pygame.K_RETURN]):
        status = 'menu'

    pygame.display.flip()

def load_frames(folder_path):
    frames = []
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.endswith(".png"):
            image_path = os.path.join(folder_path, file_name)
            frame = pygame.image.load(image_path).convert()
            frame = pygame.transform.scale(frame, (screen_width, screen_height))
            frames.append(frame)
    return frames

running = True
background = pygame.image.load("./background/frame-1.png")
logo = pygame.image.load("./interface/logo_2.png")
logo = pygame.transform.scale(logo, (400, 170))

def main_menu():
    global running, game_active, status, paused
    menu_options = ["Jogar", "Tutorial", "Sair"]
    selected_option = 0
    option_change_sound = pygame.mixer.Sound('./sons/menu.mp3')
    option_change_sound.set_volume(0.1)

    while running:
        screen.blit(pygame.transform.scale(background, (screen_width, screen_height)), (0, 0))

        screen.blit(logo, (screen_width // 2 - 195, 150))

        font = pygame.font.Font(None, 60)
        for i, option in enumerate(menu_options):
            color = (255, 0, 0) if i == selected_option else (255, 255, 255)
            text = font.render(option, 'tiny5.ttf', color)
            screen.blit(text, (screen_width // 2 - text.get_width() // 2, 400 + i * 80))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                    option_change_sound.play()
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                    option_change_sound.play()
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        status = "jogando"
                        game_active = True
                        paused = False
                        restart_game()
                        return
                    elif selected_option == 1:
                        game_active = False
                        status = "tutorial"
                        show_tutorial_menu() 
                        return
                    elif selected_option == 2:
                        running = False



def show_tutorial_menu():
    tutorial_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    tutorial_surface.fill((0, 0, 0)) 
    screen.blit(tutorial_surface, (0, 0))

    font = pygame.font.Font('./fontes/tiny5.ttf', 74)
    title_text = font.render("TUTORIAL", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 2 - 200))
    screen.blit(title_text, title_rect)
    
    small_font = pygame.font.Font('./fontes/tiny5.ttf', 36)
    move_text = small_font.render("W, A, S, D para mover a nave", True, (255, 255, 255))
    move_rect = move_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    screen.blit(move_text, move_rect)

    aim_text = small_font.render("Movimente o mouse para mirar", True, (255, 255, 255))
    aim_rect = aim_text.get_rect(center=(screen_width // 2, screen_height // 2 + 10))
    screen.blit(aim_text, aim_rect)

    upgrade_text = small_font.render("1, 2, 3 para escolher os upgrades", True, (255, 255, 255))
    upgrade_rect = upgrade_text.get_rect(center=(screen_width // 2, screen_height // 2 + 70))
    screen.blit(upgrade_text, upgrade_rect)

    back_text = small_font.render("Aperte Enter para voltar", True, (255, 255, 255))
    back_rect = back_text.get_rect(center=(screen_width // 2, screen_height // 2 + 150))
    screen.blit(back_text, back_rect)

    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting_for_input = False
                    global status
                    status = "menu"
                    main_menu()



def check_boss_attack_collision():
    global player_lives, message, message_timer
    for projectile in projectiles[:]:
        distance = math.sqrt((projectile["pos"][0] - player_pos[0]) ** 2 + (projectile["pos"][1] - player_pos[1]) ** 2)
        
       
        projectile_radius = 5 
        player_radius = 35
        
        if distance < (projectile_radius + player_radius):
            player_lives -= 1
            projectiles.remove(projectile) 
            message = "Voce foi atingido!"
            damage_sound.play()
            message_timer = 30

            if player_lives <= 0:
                show_game_over_menu()
                return


def draw_pause_menu():
    pause_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    pause_surface.fill((0, 0, 0)) 
    screen.blit(pause_surface, (0, 0))

    font = pygame.font.Font('./fontes/tiny5.ttf', 74)
    text = font.render("PAUSE", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    screen.blit(text, text_rect)
    
    small_font = pygame.font.Font('./fontes/tiny5.ttf', 36)
    resume_text = small_font.render("Aperte Enter para continuar", True, (255, 255, 255))
    resume_rect = resume_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
    screen.blit(resume_text, resume_rect)

    small_font = pygame.font.Font('./fontes/tiny5.ttf', 36)
    resume_text = small_font.render("Aperte ESC para voltar ao menu principal", True, (255, 255, 255))
    resume_rect = resume_text.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
    screen.blit(resume_text, resume_rect)

    pygame.display.flip()


frames_folder = "./background"
paused = False

frames = load_frames(frames_folder)

frame_index = 0
clock = pygame.time.Clock()
spawn_timer = 0
enemy_speed = 2.0
spawn_rate = 30
def show_intro_video():
    cap = cv.VideoCapture('inicial.mp4')

    if not cap.isOpened():
        print("Erro ao carregar o vídeo.")
        return

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("EcoDefenders")
    
    pygame.mixer.init()
    pygame.mixer.music.load("inicial.mp3")
    pygame.mixer.music.play()

    clock = pygame.time.Clock()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Fim do vídeo.")
            break

        frame = cv.resize(frame, (1280, 720))

        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = np.flipud(frame)
        frame = pygame.surfarray.make_surface(frame)

        screen.blit(frame, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                cap.release()
                pygame.mixer.music.stop()
                return

        clock.tick(30)

    cap.release()
    pygame.mixer.music.stop()

def game_loop():
    global frame_index, frames, player_lives, score, wave, enemies_killed, enemies_to_next_wave
    global enemies, bullets, player_shooting_speed, shoot_delay, player_pos
    global screen_width, screen_height, enemy_speed, spawn_rate, spawn_timer, running, game_active, paused, status

    show_intro_video()
        
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    FPS = 60
    pygame.mixer.music.load("./sons/background_music.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

    while running:
        frame_index = (frame_index + 1) % len(frames)
        screen.blit(frames[frame_index], (0, 0))

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if paused:
                    if event.key == pygame.K_RETURN:
                        paused = False
                    elif event.key == pygame.K_ESCAPE:
                        paused = False
                        game_active = False
                        main_menu()
                elif event.key == pygame.K_ESCAPE:
                    paused = True

        if paused:
            draw_pause_menu()
            clock.tick(60)
            continue

        if not game_active:
            if status == 'jogando':
                show_game_over_menu()
            elif status == 'menu':
                main_menu()
            elif status == 'tutorial':
                show_tutorial_menu()
                continue
            else:
                main_menu()

            if keys[pygame.K_SPACE]:
                player_lives = 3
                score = 0
                wave = 1
                enemies_killed = 0
                enemies_to_next_wave = 30
                enemies.clear()
                bullets.clear()
                player_shooting_speed = 20
                shoot_delay = player_shooting_speed
                player_pos[:] = [screen_width // 2, screen_height // 2]
                game_active = True
                enemy_speed = 2.0
                spawn_rate = 30
                spawn_timer = 0

        else:
            move_player(keys)
            move_bullets()
            move_enemies()
            handle_collisions()
            check_wave_progress()
            shoot_bullets()

            spawn_timer += 1
            if spawn_timer > spawn_rate:
                spawn_enemy()
                spawn_timer = 0

            draw_player()
            draw_bullets()
            draw_interface()
            draw_message()
            if wave == 5:
                draw_boss_health()
                move_projectiles()
                boss_attack()
                move_boss()
                check_boss_attack_collision()

                if player_lives <= 0:
                    game_active = False

                    show_game_over_menu()

            else:
                draw_enemies()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

game_loop()




