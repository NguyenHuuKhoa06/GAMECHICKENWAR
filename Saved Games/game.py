import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 719
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Bắn Gà")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

clock = pygame.time.Clock()
FPS = 60

ROUND_TIME = 30
POWER_UP_TIME = 10
DOUBLE_BULLET_DURATION = 5
COOLDOWN_TIME = 10

try:
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    shoot_sound = pygame.mixer.Sound("bullet_sound.wav")
    shoot_sound.set_volume(0.7)

    enemy_destroyed_sound = pygame.mixer.Sound("enemy_destroyed.wav")
    enemy_destroyed_sound.set_volume(0.8)
except pygame.error as e:
    print(f"Lỗi khi tải hoặc phát âm thanh: {e}")
    pygame.mixer.quit()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(x=random.randint(0, SCREEN_WIDTH - 50), y=random.randint(0, 200))
        self.speed_x = random.choice([-3, 3])
        self.speed_y = random.choice([1, 2])

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.top <= 0 or self.rect.bottom >= 200:
            self.speed_y = -self.speed_y

def show_score(score):
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def show_timer(time_left):
    font = pygame.font.SysFont(None, 36)
    timer_text = font.render(f"Time: {time_left}s", True, WHITE)
    screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))

def draw_power_up_button():
    font = pygame.font.SysFont(None, 24)
    power_up_button = pygame.Rect(10, SCREEN_HEIGHT - 50, 100, 40)
    pygame.draw.rect(screen, GREEN, power_up_button)
    text = font.render("Power-Up", True, WHITE)
    screen.blit(text, (20, SCREEN_HEIGHT - 40))
    return power_up_button

def draw_exit_button():
    font = pygame.font.SysFont(None, 24)
    exit_button = pygame.Rect(SCREEN_WIDTH - 110, SCREEN_HEIGHT - 50, 100, 40)
    pygame.draw.rect(screen, RED, exit_button)
    text = font.render("Exit", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH - 95, SCREEN_HEIGHT - 40))
    return exit_button

def show_start_screen():
    start_background = pygame.image.load("start_screen.png").convert_alpha()
    screen.blit(start_background, (0, 0))

    font = pygame.font.SysFont(None, 48)
    start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, GREEN, start_button)
    start_text = font.render("START", True, WHITE)
    screen.blit(start_text, (start_button.x + 50, start_button.y + 10))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    waiting = False

def main():
    show_start_screen()

    game_background = pygame.image.load("game_background.png").convert_alpha()

    player = Player()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group(Enemy() for _ in range(10))
    all_sprites = pygame.sprite.Group(player, bullets, enemies)

    score = 0
    double_bullet = False
    double_bullet_end_time = 0
    power_up_visible = False
    power_up_time = 0
    cooldown_end_time = 0
    running = True
    start_ticks = pygame.time.get_ticks()

    while running:
        screen.blit(game_background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                shoot_sound.play()
                if double_bullet:
                    bullets.add(Bullet(player.rect.centerx - 15, player.rect.top))
                    bullets.add(Bullet(player.rect.centerx + 15, player.rect.top))
                else:
                    bullets.add(Bullet(player.rect.centerx, player.rect.top))
                all_sprites.add(bullets)

            if event.type == pygame.MOUSEBUTTONDOWN:
                exit_button = draw_exit_button()
                if exit_button.collidepoint(event.pos):
                    running = False
                elif power_up_visible:
                    power_up_button = draw_power_up_button()
                    if power_up_button.collidepoint(event.pos):
                        double_bullet = True
                        double_bullet_end_time = pygame.time.get_ticks() + DOUBLE_BULLET_DURATION * 1000
                        power_up_visible = False
                        cooldown_end_time = pygame.time.get_ticks() + COOLDOWN_TIME * 1000

        if double_bullet and pygame.time.get_ticks() > double_bullet_end_time:
            double_bullet = False

        elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000
        time_left = max(0, ROUND_TIME - elapsed_time)

        if elapsed_time >= POWER_UP_TIME and not double_bullet and not power_up_visible:
            power_up_visible = True
            power_up_time = pygame.time.get_ticks() + COOLDOWN_TIME * 1000

        if power_up_visible and pygame.time.get_ticks() > power_up_time:
            power_up_visible = False

        if pygame.time.get_ticks() > cooldown_end_time:
            power_up_visible = True

        if time_left == 0:
            running = False

        all_sprites.update()
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, True)
            if hits:
                bullet.kill()
                score += len(hits)
                enemy_destroyed_sound.play()

        if len(enemies) == 0:
            for _ in range(10):
                enemy = Enemy()
                enemies.add(enemy)
                all_sprites.add(enemy)

        all_sprites.draw(screen)
        show_score(score)
        show_timer(time_left)
        draw_exit_button()

        if power_up_visible:
            draw_power_up_button()

        pygame.display.flip()
        clock.tick(FPS)

    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 72)
    game_over_text = font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100))

    score_text = pygame.font.SysFont(None, 48).render(f"Your Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

    pygame.display.flip()
    pygame.time.wait(3000)

if __name__ == "__main__":
    try:
        main()
    except pygame.error as e:
        print(f"Lỗi pygame: {e}")
    pygame.quit()
    sys.exit()
