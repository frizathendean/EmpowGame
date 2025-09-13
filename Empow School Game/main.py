import pygame
import random
import time

pygame.init()

# Ukuran layar
WIDTH, HEIGHT = 480, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Empow School Game")

# Warna
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GOLD = (180, 166, 57)
GREEN = (0, 128, 0)

# Sound
click_sfx = pygame.mixer.Sound("assets/sounds/click.wav")
pop_sfx = pygame.mixer.Sound("assets/sounds/pop.wav")
game_over_sfx = pygame.mixer.Sound("assets/sounds/gameover.wav")
lose_heart_sfx = pygame.mixer.Sound("assets/sounds/lose_heart.wav")

# Load & resize
def load_and_scale(path, w, h):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (w, h))

# Background
menu_bg = load_and_scale("assets/menu_background.png", WIDTH, HEIGHT)
game_bg = load_and_scale("assets/game_background.png", WIDTH, HEIGHT)

# Karakter
player_img = load_and_scale("assets/karakter.png", 250, 295)
player_rect = player_img.get_rect(midbottom=(WIDTH // 2, HEIGHT - 50))

# Icon nyawa
heart_img = load_and_scale("assets/icons/heart.png", 32, 25)

# Item
ITEM_WIDTH, ITEM_HEIGHT = 70, 70
item_names = {
    "air", "bekal", "buku", "papan", "penggaris", "pulpen", "uang",
    "lipstik", "bedak", "dryer", "game", "laptop"
}
items = {
    name: load_and_scale(f"assets/{name}.png", ITEM_WIDTH, ITEM_HEIGHT)
    for name in item_names
}
allowed_items = {"air", "bekal", "buku", "papan", "penggaris", "pulpen", "uang"}

# Font
def draw_text(text, x, y, size=32, color=WHITE, font=None):
    font = font or pygame.font.SysFont(None, size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

pixel_font = pygame.font.Font("assets/fonts/pixel_font.ttf", 50)

# Tombol
start_btn_img = load_and_scale("assets/start_button.png", 345, 100)
start_btn_rect = start_btn_img.get_rect(center=(WIDTH // 2, HEIGHT - 180))
restart_btn_font = pygame.font.SysFont(None, 40)
restart_btn_text = restart_btn_font.render("Coba Lagi", True, WHITE)
restart_btn_rect = pygame.Rect(0, 0, 200, 60)
restart_btn_rect.center = (WIDTH // 2, HEIGHT // 2 + 70)

# Class item jatuh
class FallingItem:
    def __init__(self, speed=None):
        self.type = random.choice(list(items.keys()))
        self.image = items[self.type]
        self.rect = self.image.get_rect(midtop=(random.randint(50, WIDTH - 50), -random.randint(150, 300)))
        self.speed = speed if speed else random.randint(3, 5)

    def fall(self):
        self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

# Game state
clock = pygame.time.Clock()
score = 0
lives = 3
running = True
game_started = False
menu_mode = True
item_list = []
game_over = False
game_start_time = 0
spawn_delay = 1.2
max_items = 1
current_scale = 1.0
target_scale = 1.0
scale_speed = 0.1

# Game loop
while running:
    mouse = pygame.mouse.get_pos()
    mouse_clicking = pygame.mouse.get_pressed()[0]
    mouse_over = start_btn_rect.collidepoint(mouse)

    if menu_mode and not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("assets/sounds/main_music.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    if menu_mode and mouse_over and mouse_clicking:
        target_scale = 0.92
    else:
        target_scale = 1.0
    current_scale += (target_scale - current_scale) * scale_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if menu_mode and event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn_rect.collidepoint(event.pos):
                click_sfx.play()
                menu_mode = False
                game_started = True
                game_start_time = time.time()
                item_list = [FallingItem()]
                score = 0
                lives = 3
                max_items = 1
                game_over = False

        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if restart_btn_rect.collidepoint(event.pos):
                click_sfx.play()
                menu_mode = True
                game_started = False
                game_over = False
                item_list = []
                score = 0
                lives = 3
                max_items = 1

    # MENU
    if menu_mode:
        screen.blit(menu_bg, (0, 0))
        title1 = pixel_font.render("EMPOW", True, GOLD)
        title2 = pixel_font.render("SCHOOL", True, GOLD)
        screen.blit(title1, title1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))
        screen.blit(title2, title2.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))

        scaled_btn = pygame.transform.scale(start_btn_img, (
            int(start_btn_rect.width * current_scale),
            int(start_btn_rect.height * current_scale)))
        scaled_btn_rect = scaled_btn.get_rect(center=start_btn_rect.center)
        screen.blit(scaled_btn, scaled_btn_rect)

        start_text = pixel_font.render("START", True, GOLD)
        start_text_rect = start_text.get_rect(center=scaled_btn_rect.center)
        start_text_rect.y -= int(0 * current_scale)
        start_text_rect.x += int(5 * current_scale)
        screen.blit(start_text, start_text_rect)

    # GAMEPLAY
    elif game_started and not game_over:
        screen.blit(game_bg, (0, 0))

        # Karakter bisa keluar layar
        player_rect.centerx = mouse[0]
        screen.blit(player_img, player_rect)

        if time.time() - game_start_time > spawn_delay:
            for item in item_list:
                item.fall()
                item.draw()
                if player_rect.colliderect(item.rect):
                    if item.type in allowed_items:
                        pop_sfx.play()
                        score += 1
                        max_items = min(5, 1 + score // 3)
                    else:
                        lives -= 1
                        lose_heart_sfx.play()
                        if lives <= 0:
                            pygame.mixer.music.stop()
                            game_over_sfx.play()
                            game_over = True
                    item_list.remove(item)
                    break

            if len(item_list) < max_items:
                item_speed = min(3 + score // 4, 10)
                item_list.append(FallingItem(speed=item_speed))
            item_list = [item for item in item_list if item.rect.top <= HEIGHT]

        draw_text(f"Skor: {score}", WIDTH - 110, 20, 36, GOLD)
        for i in range(lives):
            screen.blit(heart_img, (20 + i * 28, 20))

    # GAME OVER
    elif game_over:
        screen.blit(game_bg, (0, 0))
        small_pixel_font = pygame.font.Font("assets/fonts/pixel_font.ttf", 40)
        game_over_text = small_pixel_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
        draw_text(f"Skor Akhir: {score}", WIDTH // 2 - 90, HEIGHT // 2 + 10, 32, GOLD)
        pygame.draw.rect(screen, GREEN, restart_btn_rect, border_radius=12)
        screen.blit(restart_btn_text, restart_btn_text.get_rect(center=restart_btn_rect.center))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()