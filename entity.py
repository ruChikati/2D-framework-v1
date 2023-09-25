
import math

import input
import particle
import pygame


class Entity:

    def __init__(self, x, y, w, h, name, img, game):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name
        self.img = img
        self.game = game
        self.action = 'idle'
        self.vel = [0, 0]

    def update(self):
        collision_directions, amount_moved = self.move(self.game.assets.worlds.current_world.level.get_collision_mesh((self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright)), self.game.dt)
        if collision_directions['down'] or collision_directions['up']:
            self.vel[1] = 0
        if collision_directions['right'] or collision_directions['left']:
            self.vel[0] = 0
        self.game.assets.camera.render(self.img, (self.x + self.w // 2 - self.img.get_width(), self.y + self.h // 2 - self.img.get_height()))

    def move(self, tiles, dt):
        collision_directions = {'up': False, 'down': False, 'left': False, 'right': False}
        orig_x, orig_y = self.rect.x / 1, self.rect.y / 1
        self.rect.x += self.vel[0] * dt
        collision_tiles = [tile for tile in tiles if self.rect.colliderect(tile)]
        for tile in collision_tiles:
            if self.vel[0] > 0:
                self.rect.x = tile.x - self.w
                collision_directions['right'] = True
            elif self.vel[0] < 0:
                self.rect.x = tile.right
                collision_directions['left'] = True
        self.rect.y += self.vel[1] * dt
        collision_tiles = [tile for tile in tiles if self.rect.colliderect(tile)]
        for tile in collision_tiles:
            if self.vel[1] > 0:
                self.rect.y = tile.y - self.h
                collision_directions['down'] = True
            elif self.vel[1] < 0:
                self.rect.y = tile.bottom
                collision_directions['up'] = True
        self.y, self.x = self.rect.y, self.rect.x
        amount_moved = [self.x - orig_x, self.y - orig_y]
        return collision_directions, amount_moved


class Player(Entity):

    def __init__(self, x, y, w, h, img, game, gravity=0):
        super().__init__(x, y, w, h, 'player', img, game)
        self.anims = {anim.split(self.name)[-1]: self.game.assets.anims.anims[anim] for anim in self.game.assets.anims.anims if self.name in anim}
        self.gravity = gravity
        self.vel_cap = 8
        self.speed = 2
        self.rot_speed = 3
        self.fwd = 0.
        self.decel_speed = 1
        self.accel_speed = 1

    def update(self):
        particle_colours = ((255, 255, 0), (255, 250, 250), (255, 255, 240), (245, 245, 245), (255, 255, 255), (169, 169, 169), (129, 133, 137), (211, 211, 211), (137, 148, 153), (229, 228, 226), (192, 192, 192), (132, 136, 132))
        for event in self.game.last_input:
            if event.type == input.KEYHOLD:
                match event.key:
                    case input.SPACE:
                        self.vel[1] -= self.speed * math.sin(math.radians(self.fwd)) * self.accel_speed
                        self.vel[0] += self.speed * math.cos(math.radians(self.fwd)) * self.accel_speed
                        self.game.particles.append(
                            particle.ParticleBurst((self.x + self.w // 2, self.y + self.h // 2), 7, 25, particle_colours, 80, 80, (-self.speed * math.cos(math.radians(self.fwd)), self.speed * math.sin(math.radians(self.fwd))), self.game, type='o', shape='rect', fade=True, spread=2))
                        #self.game.assets.sfx.play('noise')
                    case input.A:
                        self.fwd += self.rot_speed
                        self.game.particles.append(
                            particle.ParticleBurst((self.x + self.w // 2, self.y + self.h // 2), 2, 15, particle_colours, 80, 80, (self.rot_speed * -math.cos(math.radians(-self.fwd)), self.rot_speed * math.sin(math.radians(-self.fwd))), self.game, type='-', shape='rect', fade=True, spread=2))
                        #self.game.assets.sfx.play('noise')
                    case input.D:
                        self.fwd -= self.rot_speed
                        self.game.particles.append(
                            particle.ParticleBurst((self.x + self.w // 2, self.y + self.h // 2), 2, 15, particle_colours, 80, 80, (self.rot_speed * math.cos(math.radians(-self.fwd)), self.rot_speed * -math.sin(math.radians(-self.fwd))), self.game, type='-', shape='rect', fade=True, spread=2))
                        #self.game.assets.sfx.play('noise')
                    case input.RETURN:
                        # for debugging, is going to be removed in the final release
                        self.x, self.y = 0, 0
                        self.rect.x, self.rect.y = 0, 0
                        self.vel = [0, 0]
                        self.fwd = 0.

        if self.vel[0] > self.vel_cap:
            self.vel[0] = self.vel_cap
        if self.vel[1] > self.vel_cap:
            self.vel[1] = self.vel_cap
        if self.vel[0] < -self.vel_cap:
            self.vel[0] = -self.vel_cap
        if self.vel[1] < -self.vel_cap:
            self.vel[1] = -self.vel_cap
        self.vel[1] += self.gravity

        collision_directions, amount_moved = self.move(self.game.assets.worlds.get_active_world().level.collision_mesh, self.game.dt)
        # TODO: use math of angle to find an equation to make 'pixel-perfect' collisions
        # TODO: just use a square astronaut :/

        if collision_directions['down'] or collision_directions['up']:
            self.vel[1] = 0
        if collision_directions['right'] or collision_directions['left']:
            self.vel[0] = 0

        if self.vel[0] > 0:
            if self.vel[0] <= 1:
                self.vel[0] = 0
            else:
                self.vel[0] -= self.decel_speed
        elif self.vel[0] < 0:
            if self.vel[0] >= -1:
                self.vel[0] = 0
            else:
                self.vel[0] += self.decel_speed
        if self.vel[1] > 0:
            if self.vel[1] <= 1:
                self.vel[1] = 0
            else:
                self.vel[1] -= self.decel_speed
        elif self.vel[1] < 0:
            if self.vel[1] >= -1:
                self.vel[1] = 0
            else:
                self.vel[1] += self.decel_speed

        self.anims[self.action].play(self.game.dt)
        self.anims[self.action].img = pygame.transform.rotate(self.anims[self.action].img, self.fwd)
        self.anims[self.action].img.set_colorkey((1, 1, 1))
        self.anims[self.action].render_main((self.x, self.y))
