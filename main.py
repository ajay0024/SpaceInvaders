import random
import sys, pygame
from pygame.locals import *
from spritesheet import SpriteSheet, Sprite, SpriteText

clock = pygame.time.Clock()


class Enemy(Sprite):
    def __init__(self, file=None, pos=(0, 0), size=None, velocity=(0, 0), image=None, images=None):
        super(Enemy, self).__init__(file=file, pos=pos, size=size, velocity=velocity, image=image, tag="Enemy",
                                    images=images)
        self.initial_position = pos
        self.left = False
        self.right = False
        self.index = 0

    def turn_around(self):
        Sprite.set_velocity(self, [-self.velocity[0], 0])

    def set_left(self):
        self.left = True

    def set_right(self):
        self.right = True

    def do(self, event):
        if event.type == game.TURN_AROUND:
            Sprite.set_velocity(self, [-self.velocity[0], 0])

    def change_sprite(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def take_damage(self):
        # Activate hit enemy event
        pygame.event.post(pygame.event.Event(game.HIT_ENEMY, score=100))
        # Add destruction animation
        destruction = Destruction((self.get_pos()[0], self.get_pos()[1]))
        game.add(destruction)
        game.remove(self)

    def update(self):
        super(Enemy, self).update()
        if self.images:
            if pygame.time.get_ticks() - self.elapsed > 300:  # animate every 0.3 second
                self.change_sprite()
                self.elapsed = pygame.time.get_ticks()

    def fire_bullet(self):
        bullet = EnemyBullet((self.get_pos()[0], self.get_pos()[1] + 10))
        game.add(bullet)


class Obstacle(Sprite):
    def __init__(self, file=None, pos=(0, 0), size=None, velocity=(0, 0), images=None):
        super(Obstacle, self).__init__(file=file, pos=pos, size=size, velocity=velocity, images=images,
                                       tag="Obstacle")
        self.stages = len(self.images)
        self.current_stage = 0
        # pygame.draw.rect(self.image, (255, 255, 0), [0, 0, 64, 64], 1)

    def do(self, event):
        pass

    def take_damage(self):
        self.current_stage += 1
        # print(self.current_stage, self.stages)
        if self.current_stage >= self.stages:
            game.remove(self)
            return
        self.image = self.images[self.current_stage]

    def update(self):
        super(Obstacle, self).update()


class Player(Sprite):
    def __init__(self, file=None, pos=(0, 0), size=None, velocity=(0, 0), image=None):
        super(Player, self).__init__(file=file, pos=pos, size=size, velocity=velocity, image=image, tag="Player")
        self.initial_position = pos

    def do(self, event):
        super(Player, self).do(event)
        if event.type == (pygame.USEREVENT + 3) or event.type == pygame.KEYUP and (
                event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
            self.velocity = [0, 0]
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and self.get_pos()[0] > 0:
                self.velocity = [-2, 0]
            elif event.key == pygame.K_RIGHT and self.get_pos()[0] < 640:
                self.velocity = [2, 0]
            elif event.key == pygame.K_SPACE:  # Instantiate Bullet
                if len(game.objects_tag_dict["PlayerBullet"]) == 0:
                    bullet = PlayerBullet((self.get_pos()[0], self.get_pos()[1] - 10))
                    game.add(bullet)

    def update(self):
        super(Player, self).update()
        if self.get_pos()[0] < 0 or self.get_pos()[0] > 640:
            # print("Outside", self.get_pos()[0])
            my_event = pygame.event.Event(pygame.USEREVENT + 3)
            pygame.event.post(my_event)


class PlayerBullet(Sprite):
    def __init__(self, pos=(0, 0)):
        # Give collision box size to reduce the collision box thickness
        super(PlayerBullet, self).__init__(file=None, pos=pos, size=(32, 32), velocity=(0, -2), image=sprite_images[2],
                                           tag="PlayerBullet", collision_box_size=(4, 12))
        self.initial_position = pos
        # pygame.draw.rect(self.image, (255, 0, 255), [0, 0, 32, 32], 1)

    def do(self, event):
        super(PlayerBullet, self).do(event)
        if event.type == game.GAME_OVER:
            game.remove(self)

    def update(self):
        super(PlayerBullet, self).update()

        if self.get_pos()[1] < 30:
            game.remove(self)


class EnemyBullet(Sprite):
    def __init__(self, pos=(0, 0)):
        # Give collision box size to reduce the collision box thickness
        self.images = [sprite_images[9], sprite_images[12]]
        super(EnemyBullet, self).__init__(file=None, pos=pos, size=(32, 32), velocity=(0, 2), images=self.images,
                                          tag="EnemyBullet", collision_box_size=(4, 12))
        self.index = 0
        # pygame.draw.rect(self.image, (255, 0, 255), [0, 0, 32, 32], 1)

    def do(self, event):
        super(EnemyBullet, self).do(event)
        if event.type == game.GAME_OVER:
            game.remove(self)

    def change_sprite(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def update(self):
        super(EnemyBullet, self).update()

        if self.images:
            if pygame.time.get_ticks() - self.elapsed > 100:  # animate every 0.3 second
                self.change_sprite()
                self.elapsed = pygame.time.get_ticks()

        if self.get_pos()[1] > 800:
            game.remove(self)


class Destruction(Sprite):
    def __init__(self, pos=(0, 0)):
        # Give collision box size to reduce the collision box thickness
        self.images = [sprite_images[16], sprite_images[23], sprite_images[30]]
        self.current_stage = 0
        self.stages = len(self.images)
        super(Destruction, self).__init__(file=None, pos=pos, size=(32, 32), velocity=(0, 0), images=self.images,
                                          tag="EnemyBullet", collision_box_size=(4, 12))
        self.index = 0
        # pygame.draw.rect(self.image, (255, 0, 255), [0, 0, 32, 32], 1)

    def do(self, event):
        super(Destruction, self).do(event)
        if event.type == game.GAME_OVER:
            game.remove(self)

    def change_sprite(self):
        self.current_stage += 1
        if self.current_stage >= self.stages:
            game.remove(self)
            return
        self.image = self.images[self.current_stage]

    def update(self):
        super(Destruction, self).update()

        if self.images:
            if pygame.time.get_ticks() - self.elapsed > 100:  # animate every 0.3 second
                self.change_sprite()
                self.elapsed = pygame.time.get_ticks()


class Score(SpriteText):
    def __init__(self, pos=(0, 0), font=None):
        self.score = 0
        super(Score, self).__init__(text=str(self.score), pos=pos, font=font, tag="Score")

    def do(self, event):
        super(Score, self).do(event)
        if event.type == game.HIT_ENEMY:
            self.score += event.score
            self.update_text(str(self.score))

    def get_score(self):
        return self.score


class App:
    def __init__(self, file=None, caption='Pygame', size=(640, 800)):
        pygame.init()
        pygame.display.set_caption(caption)
        self.flags = RESIZABLE
        self.size = size
        self.screen = pygame.display.set_mode(self.size, self.flags)
        self.running = True
        self.updating = True
        self.game_over = False
        self.final_score = 0
        self.objects = []
        self.TURN_AROUND = pygame.USEREVENT + 1
        self.HIT_ENEMY = pygame.USEREVENT + 4
        self.GAME_OVER = pygame.USEREVENT + 5
        self.player = None
        # Maintain a tag dictionary for easy access of particular type
        # adding already know tags for easy access and no errors in loops
        self.objects_tag_dict = {"PlayerBullet": [], "Enemy": [], "EnemyBullet": []}
        self.bg_color = 'black'
        if file:
            self.load_image(file)
        else:
            self.image = pygame.Surface(self.size)
            self.image.fill(self.bg_color)
            self.rect = self.image.get_rect()
        self.key_cmd = {}
        self.time_elapsed = pygame.time.get_ticks()

    def load_image(self, file):
        self.image = pygame.image.load(file).convert()
        self.rect = self.image.get_rect()
        self.screen = pygame.display.set_mode(self.rect.size, self.flags)

    def run(self):
        print(self.objects_tag_dict.keys())
        while self.running:
            for event in pygame.event.get():
                self.do(event)
            self.update()
            self.draw()

    def add_cmd(self, key, cmd):
        self.key_cmd[key] = cmd
        print(self.key_cmd)

    def add(self, obj):
        self.objects.append(obj)
        if obj.tag:
            if obj.tag not in self.objects_tag_dict:
                self.objects_tag_dict[obj.tag] = []
            self.objects_tag_dict[obj.tag].append(obj)
        obj.parent = self

    def remove(self, obj):
        # print(obj.tag)
        if obj in self.objects:
            self.objects.remove(obj)
        if obj.tag in self.objects_tag_dict and obj in self.objects_tag_dict[obj.tag]:
            self.objects_tag_dict[obj.tag].remove(obj)
        del obj

    def do(self, event):
        if event.type == QUIT:
            self.running = False
            pygame.quit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.updating = not self.updating
            if event.key in self.key_cmd:
                cmd = self.key_cmd[event.key]
                eval(cmd)
            if event.key == K_r and self.game_over:
                self.clean_screen()
                generate_level()

        for obj in self.objects:
            obj.do(event)

    def update(self):
        # Checking collision of enemies with playerbullet
        if len(self.objects_tag_dict["PlayerBullet"]) > 0:
            player_bullet = self.objects_tag_dict["PlayerBullet"][0]
            for enemy in self.objects_tag_dict["Enemy"]:
                if enemy.on_collision(player_bullet):
                    # print("Collision with Enemy")
                    self.remove(player_bullet)
                    enemy.take_damage()
            for obs in self.objects_tag_dict["Obstacle"]:
                if obs.on_collision(player_bullet):
                    # print("Damage Obstacle")
                    self.remove(player_bullet)
                    obs.take_damage()
                    break
        # Checking collision of Enemy Bullet with obstacle and player
        for enemy_bullet in self.objects_tag_dict["EnemyBullet"]:
            for obs in self.objects_tag_dict["Obstacle"]:
                if obs.on_collision(enemy_bullet):
                    # print("Damage Obstacle")
                    self.remove(enemy_bullet)
                    obs.take_damage()
                    break
            if self.player.on_collision(enemy_bullet):
                self.game_over = True
                self.final_score = self.objects_tag_dict["Score"][0].get_score()
                self.clean_screen()
                self.show_game_over_screen()

        # Generating Random Bullets by Enemy
        if self.updating and pygame.time.get_ticks() - self.time_elapsed > random.randint(1000,
                                                                                          3000):  # animate every 0.1 to 0.3 second
            if len(self.objects_tag_dict["Enemy"]) > 0:
                random.choice(self.objects_tag_dict["Enemy"]).fire_bullet()
            self.time_elapsed = pygame.time.get_ticks()

        # Update All Objects
        if self.updating:
            for obj in self.objects:
                obj.update()

        # Check turning point of enemies Should be after updating of all objects
        for enemy in self.objects_tag_dict["Enemy"]:
            if 20 > enemy.get_pos()[0] or enemy.get_pos()[0] > 620:
                pygame.event.post(pygame.event.Event(self.TURN_AROUND))
                break

    def draw(self):
        self.screen.blit(self.image, self.rect)
        for obj in self.objects:
            obj.draw(self.screen)
        pygame.display.update()

    def show_game_over_screen(self):
        game_over_label = SpriteText(text="Game Over", pos=(200, 50), font=large_font)
        game_over_score = SpriteText(text=f"Score :  {self.final_score}", pos=(200, 150), font=large_font)
        game_over_restart = SpriteText(text="Press \"R\" to restart", pos=(150, 250), font=large_font)
        self.add(game_over_label)
        self.add(game_over_score)
        self.add(game_over_restart)

    def clean_screen(self):
        objects_list = self.objects.copy()

        for obj in objects_list:
            # if obj.tag != "Background":
            self.remove(obj)


def generate_level():
    enemies_sprites = []
    left_obstacle_images = []
    right_obstacle_images = []
    left_obstacle_sprites = []
    right_obstacle_sprites = []
    texts = []
    for x in range(4):
        left_obstacle_images.append(sprite_images[10 + x * 7])
        right_obstacle_images.append(sprite_images[11 + x * 7])
    posx = 77
    for x in range(4):
        obstacle = Obstacle(images=left_obstacle_images, pos=(posx, 500), size=(64, 64))
        left_obstacle_sprites.append(obstacle)
        posx += 64
        obstacle = Obstacle(images=right_obstacle_images, pos=(posx, 500), size=(64, 64))
        right_obstacle_sprites.append(obstacle)
        posx += 75
    score_label = SpriteText(text="Score : ", pos=(400, 50), font=font)
    texts.append(score_label)
    score = Score(font=font, pos=(470, 50))
    texts.append(score)


    player = Player(image=sprite_images[4], pos=(320, 700), size=(32, 32))
    game.player = player

    # Background Sprites
    bg_sprites = []
    for x in range(5):
        for y in range(7):
            pos = (128 * x + 64, 128 * y + 64)  # 64 is added so that position marks center of the rectangle
            if y <= 3:
                bg_sprites.append(Sprite(file=bg_img, pos=pos, size=(128, 128), tag="Background"))
            if y > 3:
                bg_sprites.append(Sprite(file=bg_floor_img, pos=pos, size=(128, 128), tag="Background"))
            elif y == 3:
                bg_sprites.append(Sprite(file=bg_buildings_img, pos=pos, size=(128, 128), tag="Background"))
    print(f"Adding {len(bg_sprites)} Backgounds")
    for bg_sprite in bg_sprites:
        game.add(bg_sprite)

    # Line Enemies Sprite
    for x in range(10):
        for y in range(5):
            enemy = Enemy(image=sprite_images[y * 7], pos=(42 * x + 30, 150 + 30 * y), size=(32, 32),
                          velocity=[1, 0],
                          images=[sprite_images[y * 7], sprite_images[y * 7 + 1]])
            if x == 0:
                enemy.set_left()
            elif x == 9:
                enemy.set_right()
            enemies_sprites.append(enemy)
    print(f"Adding {len(enemies_sprites)} Enemies")
    for enemy_sprite in enemies_sprites:
        game.add(enemy_sprite)

    for obstacle_sprite in left_obstacle_sprites:
        game.add(obstacle_sprite)
    for obstacle_sprite in right_obstacle_sprites:
        game.add(obstacle_sprite)

    for text in texts:
        game.add(text)
    game.add(player)
    print("Loaded")


# sprite_images = SpriteSheet('Assets/SpaceInvaders.png').load_grid_images(5, 7)
# bgrect = background.get_rect()

game = App(caption="Space Invaders by Ajay")
# background = Sprite(file="Assets/SpaceInvaders_Background.png")
bg_img="Assets/SpaceInvaders_Background.png"
bg_floor_img="Assets/SpaceInvaders_BackgroundFloor.png"
bg_buildings_img="Assets/SpaceInvaders_BackgroundBuildings.png"
sprite_images = SpriteSheet('Assets/SpaceInvaders.png').load_grid_images(5, 7)
font = pygame.font.Font(None, 28)
large_font = pygame.font.Font(None, 64)
generate_level()

# fonts = pygame.font.get_fonts()
# print(len(fonts))
# for f in fonts:
#     print(f)

game.run()
