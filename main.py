# Space Shooter Game using Pygame

import pygame
from random import randint, uniform
from os.path import join

# Game Initialization
pygame.init()
pygame.display.set_caption("Space Shooter")

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Clock and control variables
running = True
clock = pygame.time.Clock()
score = 0
best_score = 0


# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.image.load('images\\player.png').convert_alpha()
        self.rect = self.image.get_frect(center=(WIDTH / 2, HEIGHT / 2))
        self.direction = pygame.math.Vector2()
        self.speed = 300
        self.mask = pygame.mask.from_surface(self.image)

        # Shooting cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.stop_timer = 200

    def laser_timer(self):
        """Handles laser shooting cooldown."""
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.stop_timer:
                self.can_shoot = True

    def update(self, delta_time):
        """Update player position and handle shooting."""
        keys = pygame.key.get_pressed()

        # Movement handling
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.rect.center += self.direction * self.speed * dt

        # Shooting
        recent_key = pygame.key.get_just_pressed()
        if recent_key[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surface, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

        # Boundary check
        if self.rect.bottom > HEIGHT or (self.rect.left < 0 or self.rect.right > WIDTH):
            pygame.quit()
            exit()


# Star Class (Background)
class Star(pygame.sprite.Sprite):
    def __init__(self, surface, *groups):
        super().__init__(*groups)
        self.image = surface
        self.rect = self.image.get_frect(center=(randint(0, WIDTH), randint(0, HEIGHT)))


# Laser Class (Player Bullets)
class Laser(pygame.sprite.Sprite):
    def __init__(self, surface, position, *groups):
        super().__init__(*groups)
        self.image = surface
        self.rect = self.image.get_frect(center=position)
        self.speed = 700  # pixels per second
        self.direction = pygame.math.Vector2(0, -1)  # moves upward

    def update(self, dt):
        """Move the laser and remove it when off-screen."""
        self.rect.center += self.direction * self.speed * dt
        if self.rect.bottom < 0:
            self.kill()


# Meteor Class (Enemies)
class Meteor(pygame.sprite.Sprite):
    def __init__(self, surface, position, *groups):
        super().__init__(*groups)
        self.original_surface = surface
        self.image = surface
        self.rect = self.image.get_frect(center=position)
        self.start_time = pygame.time.get_ticks()
        self.lifespan = 2500
        self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(200, 500)
        self.rotation_speed = randint(10, 25)

    def update(self, dt):
        """Move and rotate meteors; destroy after lifespan."""
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifespan:
            self.kill()
        self.rotation_speed += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surface, self.rotation_speed, 1)


# Animated Fire (Explosion Effect)
class AnimatedFire(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frame = frames
        self.frame_index = 0
        self.image = self.frame[self.frame_index]
        self.rect = self.image.get_frect(center=pos)

    def update(self, dt):
        """Play explosion animation frame by frame."""
        self.frame_index += 10 * dt
        if self.frame_index < len(self.frame):
            self.image = self.frame[int(self.frame_index)]
        else:
            self.kill()


# Scoreboard
def score_card():
    """Display the player's current score."""
    score_text_surface = font.render(f'Score : {score}', True, color='#38272e')
    score_text_rect = score_text_surface.get_frect(center=(WIDTH - 100, 50))
    screen.blit(score_text_surface, score_text_rect)
    # pygame.draw.rect(screen, rect=text_rect.inflate(10, 15), color='#2c2c33', border_radius=10, width=5)

# Collision Handling
def collision():
    """Handle player and laser collisions with meteors."""
    global running
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        global score
        if collided_sprites:
            laser.kill()
            score += 1
            AnimatedFire(fire_image, laser.rect.midtop, all_sprites)
            explosion_sound.play()


# Assets Loading (Images / Audio / Font)
meteor_surface = pygame.image.load('images\\meteor.png').convert_alpha()
meteor_rect = meteor_surface.get_frect(center=(WIDTH / 2, HEIGHT / 2))
laser_surface = pygame.image.load('images\\laser.png').convert_alpha()
star_surface = pygame.image.load('images\\star.png').convert_alpha()
font = pygame.font.Font("images\\Oxanium-Bold.ttf", 30)

fire_image = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.3)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.3)
game_sound = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_sound.set_volume(0.2)
game_sound.play(loops=3)


# Sprite Groups
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

# Create background stars
for i in range(20):
    Star(star_surface, all_sprites)

# Create player
player = Player(all_sprites)


# Custom Meteor Spawn Event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 250)


# Game Loop
while running:
    dt = clock.tick() / 1000

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WIDTH), randint(-200, -100)
            Meteor(meteor_surface, (x, y), (all_sprites, meteor_sprites))

    # Update all sprites
    all_sprites.update(dt)

    # Handle collisions
    collision()

    # Draw background
    screen.fill(color='#4e6657')

    # Draw sprites
    all_sprites.draw(screen)

    # Display score
    score_card()

    # Refresh display
    pygame.display.update()


# Quit Game
pygame.quit()
