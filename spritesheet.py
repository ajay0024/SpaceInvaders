import time

import pygame
from pygame.locals import *
import numpy as np


class SpriteSheet:

    def __init__(self, filename):
        """Load the sheet."""
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectangle, colorkey=None):
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey=None):
        """Load a whole bunch of images and return them as a list."""
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey=None):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

    def load_grid_images(self, num_rows, num_cols, x_margin=0, x_padding=0,
                         y_margin=0, y_padding=0):
        """Load a grid of images.
        x_margin is space between top of sheet and top of first row.
        x_padding is space between rows.
        Assumes symmetrical padding on left and right.
        Same reasoning for y.
        Calls self.images_at() to get list of images.
        """
        sheet_rect = self.sheet.get_rect()
        sheet_width, sheet_height = sheet_rect.size

        # To calculate the size of each sprite, subtract the two margins,
        #   and the padding between each row, then divide by num_cols.
        # Same reasoning for y.
        x_sprite_size = (sheet_width - 2 * x_margin
                         - (num_cols - 1) * x_padding) / num_cols
        y_sprite_size = (sheet_height - 2 * y_margin
                         - (num_rows - 1) * y_padding) / num_rows

        sprite_rects = []
        for row_num in range(num_rows):
            for col_num in range(num_cols):
                # Position of sprite rect is margin + one sprite size
                #   and one padding size for each row. Same for y.
                x = x_margin + col_num * (x_sprite_size + x_padding)
                y = y_margin + row_num * (y_sprite_size + y_padding)
                sprite_rect = (x, y, x_sprite_size, y_sprite_size)
                sprite_rects.append(sprite_rect)

        grid_images = self.images_at(sprite_rects, colorkey=0)
        # print(f"Loaded {len(grid_images)} grid images.")

        return grid_images


clock = pygame.time.Clock()


class Sprite:
    # Image to be supplied if directly supplying Rect instead of Image File
    # Images if we want to store multiple image for 1 sprite
    def __init__(self, file=None, pos=(0, 0), size=None, velocity=(0, 0), image=None, tag="Sprite", images=None,
                 collision_box_size=None):
        self.collision_box_size = collision_box_size
        self.parent = None
        self.size = size
        self.rect = Rect(pos, (20, 20))

        self.position = np.array(pos, dtype=float)
        self.tag = tag
        # self.velocity = np.array([1.5, 0.5], dtype=float)
        self.velocity = velocity
        self.angle = 0
        self.angular_velocity = 0
        self.color = 'blue'
        self.speed = [0, 0]
        self.images = None
        if images:
            self.images = images
            if self.size:
                for x in range(len(self.images)):
                    self.images[x] = pygame.transform.scale(self.images[x], size)
                self.rect.size = self.images[0].get_size()
            self.image = self.images[0]
            self.elapsed = pygame.time.get_ticks()

        elif image:
            self.image = image
            if self.size:
                self.image = pygame.transform.scale(self.image, size)
                self.rect.size = self.image.get_size()
        elif file:
            self.image = pygame.image.load(file)
            if self.size:
                self.image = pygame.transform.scale(self.image, size)
                self.rect.size = self.image.get_size()
        else:
            self.image = pygame.Surface(self.rect.size)
            self.image.fill(self.color)
        self.image0 = self.image.copy()
        print(tag, self.images)
        self.collision_rect = self.rect.copy()
        if collision_box_size:
            self.collision_rect.size = collision_box_size

        # print(file, self.image, self.position, self.rect, self.velocity)

    def set_pos(self, pos):
        self.position = np.array(pos, dtype=float)
        self.rect.center = pos
        self.collision_rect = pos

    def get_pos(self):
        return self.position

    def set_velocity(self, velocity):
        self.velocity = velocity

    def set_angle(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.rect.size = self.image.get_size()

    def do(self, event):
        pass

    def update(self):
        self.move()

    def move(self):
        self.position += self.velocity

        if self.angular_velocity:
            self.angle += self.angular_velocity
            self.image = pygame.transform.rotate(self.image0, self.angle)
            self.rect.size = self.image.get_size()

        self.rect.center = self.position
        self.collision_rect.center = self.position

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        #   Uncomment following code to check custom collision boxes while playing
        # if self.collision_box_size:
        #     pygame.draw.rect(surf, (255, 0, 0, 0.5), self.collision_rect)

    def distance(self, other):
        distance = self.position - other.position
        distance *= distance
        d = np.sqrt(np.sum(distance))
        return d

    def on_collision(self, other):
        is_colliding = self.collision_rect.colliderect(other.collision_rect)
        return is_colliding

    def __repr__(self):
        return f"{self.tag} Object"


class SpriteText(Sprite):
    def __init__(self, text=None, pos=(0, 0), tag="Text", font=None):
        self.font = font
        self.position = pos
        text = font.render(text, False, (0, 222, 0, 0))
        super(SpriteText, self).__init__(image=text, tag=tag, pos=self.position)
        # print(file, self.image, self.position, self.rect, self.velocity)

    def update_text(self, new_text):
        text = self.font.render(new_text, False, (0, 222, 0, 0))
        self.image = text
