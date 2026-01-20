import pygame # type: ignore
import sys
from car import Car
from ai_car import AICar

pygame.init()

START = 0
COUNTDOWN = 1
RACE = 2
FINISHED = 3
countdown_done = False

game_state = START

WIDTH, HEIGHT = 1200, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Racing Game")

clock = pygame.time.Clock()

# --- Load Track (scale with aspect ratio preserved) ---
zoom = 1.5
track = pygame.image.load("img/track_2.png").convert()

new_width = int(track.get_width() * zoom)
new_height = int(track.get_height() * zoom)

track = pygame.transform.scale(track, (new_width, new_height))
TRACK_WIDTH, TRACK_HEIGHT = track.get_size()

# Load finish line image
finish_line = pygame.image.load("img/Finish_line.png").convert_alpha()
finish_line = pygame.transform.rotate(finish_line, 45)
finish_line = pygame.transform.scale(finish_line, (220, 170))

# Finish line world coordinates
finish_x = 907
finish_y = 1659
finish_rect = finish_line.get_rect(center=(finish_x, finish_y))

# Create car object
car = Car(980.5727070840167, 1741.5746694988086)

# --- Lap & Checkpoint System ---

checkpoints = [
    (926.5727070840167, 1669.5746694988086),
    (679.4634841463737, 1238.759903286356),
    (1060.9715178826782, 1081.9002972084932),
    (1301.064127829592, 876.5663307358749),
    (727.9529533837689, 725.1799929024234),
    (264, 502.7782271396132),
    (836.1572434072149, 247),
    (1386.5563422148937, 381),
    (1535.5569949283522, 602),
    (1752.5569949416854, 421),
    (2069, 306.96861365720565),
    (1952, 761.7739014476721),
    (1582, 1060.1161380756573),
    (1614.2634416154842, 1570.3612774747835),
    (1651, 2113),
    (1172.0041293681163, 1967),
    (926.5727070840167, 1669.5746694988086)
]

show_checkpoints = True

lap = 0
font = pygame.font.Font(None, 40)

button_font = pygame.font.Font(None, 50)
start_button_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 60)

countdown_value = 3
countdown_start_time = 0
best_lap_time = None
lap_start_time = 0
lap_count = 0
current_checkpoint = 0
total_laps = 3
crossed_finish = False

# Create AI opponents
ai_cars = [
    AICar(950, 1700, "img/f1_blue.png", checkpoints, speed=6.0),
    AICar(960, 1710, "img/f1_yellow.png", checkpoints, speed=6.1),
    AICar(950, 1700, "img/f1_white.png", checkpoints, speed=5.2),
    AICar(960, 1710, "img/f1_redBull.png", checkpoints, speed=6.5)
]

def get_progress(car_obj):
    return car_obj.lap * len(checkpoints) + car_obj.current_cp

while True:

    # =============================
    # 1. EVENTS
    # =============================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            track_x = mx + camera_x
            track_y = my + camera_y
            print("Checkpoint position:", track_x, track_y)

            if game_state == START:
                if start_button_rect.collidepoint(event.pos):
                    game_state = COUNTDOWN
                    countdown_start_time = pygame.time.get_ticks()
                    countdown_value = 3

    # =============================
    # 2. CAMERA FOLLOW
    # =============================
    camera_x = car.x - WIDTH // 2
    camera_y = car.y - HEIGHT // 2

    camera_x = max(0, min(camera_x, TRACK_WIDTH - WIDTH))
    camera_y = max(0, min(camera_y, TRACK_HEIGHT - HEIGHT))

    keys = pygame.key.get_pressed()

    # =============================
    # 3. COUNTDOWN LOGIC (FIXED)
    # =============================
    if game_state == COUNTDOWN:
        elapsed = (pygame.time.get_ticks() - countdown_start_time) // 1000

        if elapsed == 0:
            countdown_value = 3
        elif elapsed == 1:
            countdown_value = 2
        elif elapsed == 2:
            countdown_value = 1
        else:
            countdown_value = "GO"

        if elapsed >= 3 and not countdown_done:
            countdown_done = True
            game_state = RACE
            lap_start_time = pygame.time.get_ticks()
            lap_count = 0
            current_checkpoint = 0


    # =============================
    # 4. UPDATE CARS (ONLY DURING RACE)
    # =============================
    if game_state == RACE:
        car.update(keys, track, camera_x, camera_y)
        for ai in ai_cars:
            ai.update()

    # =============================
    # 5. FINISH LINE & CHECKPOINTS
    # =============================
    # if game_state == RACE:
    #     car_rect = pygame.Rect(car.x - 20, car.y - 20, 40, 40)
    #
    #     if car_rect.colliderect(finish_rect):
    #         if not crossed_finish and current_checkpoint == 0:
    #             lap_count += 1
    #             crossed_finish = True
    #
    #             now = pygame.time.get_ticks()
    #             lap_time = (now - lap_start_time) / 1000.0
    #             lap_start_time = now
    #
    #             if best_lap_time is None or lap_time < best_lap_time:
    #                 best_lap_time = lap_time
    #     else:
    #         crossed_finish = False

        cp_x, cp_y = checkpoints[current_checkpoint]
        dist = ((car.x - cp_x)**2 + (car.y - cp_y)**2)**0.5

        if dist < 75:
            current_checkpoint += 1

            if current_checkpoint >= len(checkpoints):
                current_checkpoint = 0
                lap_count += 1

                if lap_count >= total_laps:
                    game_state = FINISHED
    # =============================
    # 6. DRAW TRACK
    # =============================
    window.fill((0, 0, 0))
    window.blit(track, (-camera_x, -camera_y))

    screen_rect = finish_rect.move(-camera_x, -camera_y)
    window.blit(finish_line, screen_rect)

    car.draw_at(window, car.x - camera_x, car.y - camera_y)

    for ai in ai_cars:
        ai.draw(window, camera_x, camera_y)

    # =============================
    # 7. UI STATES
    # =============================
    if game_state == START:
        pygame.draw.rect(window, (0, 200, 0), start_button_rect)
        text = font.render("START", True, (0, 0, 0))
        window.blit(text, text.get_rect(center=start_button_rect.center))

    elif game_state == COUNTDOWN:
        text = font.render(str(countdown_value), True, (255, 0, 0))
        window.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

    elif game_state == RACE:
        timer = (pygame.time.get_ticks() - lap_start_time) / 1000.0
        hud = f"Lap: {lap_count}/{total_laps}   Time: {timer:.2f}s"
        window.blit(font.render(hud, True, (255, 255, 255)), (20, 20))

    if game_state == RACE:
        race_cars = []

        # Player progress
        race_cars.append({
            "name": "Player",
            "progress": lap_count * len(checkpoints) + current_checkpoint
        })

        # AI progress
        for i, ai in enumerate(ai_cars):
            race_cars.append({
                "name": f"AI {i + 1}",
                "progress": ai.lap * len(checkpoints) + ai.current_cp
            })

        # Sort by race progress
        race_cars.sort(key=lambda x: x["progress"], reverse=True)

        # --- Draw scoreboard ---
        score_x = WIDTH - 280
        score_y = 70

        title = font.render("Positions", True, (255, 215, 0))
        window.blit(title, (score_x, score_y))
        score_y += 30

        for idx, car_info in enumerate(race_cars):
            text = f"{idx + 1}. {car_info['name']}"
            render = font.render(text, True, (255, 255, 255))
            window.blit(render, (score_x, score_y))
            score_y += 25

    pygame.display.flip()
    clock.tick(60)