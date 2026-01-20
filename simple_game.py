

import random
import pygame
import sys
import os

# Konstanty
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (30, 30, 40)
PLAYER_COLOR = (50, 200, 50)
ENEMY_COLOR = (200, 50, 50)
BULLET_COLOR = (255, 220, 100)
FPS = 60

# Cesta k obrázkům
IMAGES_DIR = 'images'

class GameObject:
    """Základní třída pro všechny objekty."""
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(int(x), int(y), w, h)

    def update_rect(self):
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, surface):
        raise NotImplementedError

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 130, 130)
        self.speed = 5
        self.cooldown = 0  # frames do střelby
        self.image = self.load_image('player.png', (130, 130))
    
    def load_image(self, filename, size):
        """Načtěte obrázek nebo vrátí None, pokud neexistuje."""
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                return pygame.transform.scale(img, size)
            except:
                return None
        return None

    def handle_input(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed

        self.x = max(0, min(WIDTH - self.w, self.x + dx))
        self.y = max(0, min(HEIGHT - self.h, self.y + dy))
        self.update_rect()

        if self.cooldown > 0:
            self.cooldown -= 1

    def can_shoot(self):
        return self.cooldown == 0

    def shoot(self):
        self.cooldown = 12  # frames between shots
        bx = self.x + self.w // 2 - 10
        by = self.y - 30
        return Bullet(bx, by, 20, 20, -7)

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
            pygame.draw.rect(surface, (100, 255, 100), self.rect, 3)  # Zelený outline
        else:
            pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
            pygame.draw.rect(surface, (100, 255, 100), self.rect, 3)

class Enemy(GameObject):
    def __init__(self, x, y, speed):
        super().__init__(x, y, 100, 100)
        self.speed = speed
        self.image = self.load_image('enemy.png', (100, 100))
    
    def load_image(self, filename, size):
        """Načtěte obrázek nebo vrátí None, pokud neexistuje."""
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                return pygame.transform.scale(img, size)
            except:
                return None
        return None

    def update(self):
        self.y += self.speed
        self.update_rect()

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
            pygame.draw.rect(surface, (255, 100, 100), self.rect, 3)  # Červený outline
        else:
            pygame.draw.rect(surface, ENEMY_COLOR, self.rect)
            pygame.draw.rect(surface, (255, 100, 100), self.rect, 3)

class Bullet(GameObject):
    def __init__(self, x, y, w, h, vy):
        super().__init__(x, y, w, h)
        self.vy = vy
        self.image = self.load_image('bullet.png', (20, 20))
    
    def load_image(self, filename, size):
        """Načtěte obrázek nebo vrátí None, pokud neexistuje."""
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                return pygame.transform.scale(img, size)
            except:
                return None
        return None

    def update(self):
        self.y += self.vy
        self.update_rect()

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, BULLET_COLOR, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Fantasy Fighter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.large_font = pygame.font.SysFont(None, 50)
        self.background = self.load_background()
        self.reset_game()
    
    def reset_game(self):
        """Obnovit hru na počátek."""
        self.player = Player(WIDTH // 2 - 65, HEIGHT - 150)
        self.bullets = []
        self.enemies = []
        self.spawn_timer = 0
        self.score = 0
        self.running = True
    
    def load_background(self):
        """Načtěte background obrázek nebo vrátí None."""
        path = os.path.join(IMAGES_DIR, 'background.png')
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                return pygame.transform.scale(img, (WIDTH, HEIGHT))
            except:
                return None
        return None

    def spawn_enemy(self):
        x = random.randint(0, WIDTH - 30)
        speed = random.uniform(1.0, 3.0)
        enemy = Enemy(x, -30, speed)
        self.enemies.append(enemy)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_SPACE and self.player.can_shoot():
                    self.bullets.append(self.player.shoot())

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        # spawn enemies
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = max(20, 60 - self.score // 5)

        # update bullets
        for b in self.bullets[:]:
            b.update()
            if b.y < -10:
                self.bullets.remove(b)

        # update enemies
        for e in self.enemies[:]:
            e.update()
            if e.y > HEIGHT:
                self.enemies.remove(e)

        # collisions: bullets vs enemies
        for b in self.bullets[:]:
            for e in self.enemies[:]:
                if b.rect.colliderect(e.rect):
                    try:
                        self.bullets.remove(b)
                        self.enemies.remove(e)
                    except ValueError:
                        pass
                    self.score += 1
                    break

        # collisions: enemy vs player
        for e in self.enemies:
            if e.rect.colliderect(self.player.rect):
                self.running = False

    def draw_hud(self):
        score_surf = self.font.render(f"Skóre: {self.score}", True, (230, 230, 230))
        self.screen.blit(score_surf, (10, 10))

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BG_COLOR)
        self.player.draw(self.screen)
        for b in self.bullets:
            b.draw(self.screen)
        for e in self.enemies:
            e.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        game_running = True
        while game_running:
            self.reset_game()
            while self.running:
                self.clock.tick(FPS)
                self.handle_events()
                self.update()
                self.draw()

            # Konec hry - ukázat skóre a možnost hrát znovu
            game_running = self.show_game_over()

    def show_game_over(self):
        """Ukázat obrazovku konce hry s možností hrát znovu."""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True  # Hrát znovu
                    elif event.key == pygame.K_ESCAPE:
                        return False  # Ukončit hru
            
            # Vykreslit obrazovku
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(BG_COLOR)
            
            # Vykreslení textu
            game_over_msg = self.large_font.render("KONEC HRY", True, (255, 100, 100))
            score_msg = self.font.render(f"Skóre: {self.score}", True, (230, 230, 230))
            restart_msg = self.font.render("MEZERNÍK - Hrát znovu  |  ESC - Konec", True, (200, 200, 200))
            
            game_over_rect = game_over_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            score_rect = score_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            restart_rect = restart_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            
            self.screen.blit(game_over_msg, game_over_rect)
            self.screen.blit(score_msg, score_rect)
            self.screen.blit(restart_msg, restart_rect)
            
            pygame.display.flip()
            self.clock.tick(30)


if __name__ == '__main__':
    Game().run()
