import arcade
import math
import random
# import physics

frames_per_update = 3
left = -1
right = 1


class Knife(arcade.Sprite):
    def __init__(self, texture, scale):
        super(Knife, self).__init__(texture, scale)

    def update(self):
        pass

    def throw(self, trajectory):
        pass


class Projectile(arcade.Sprite):

    trajectory = None
    change_angle: float = None
    path: list = None
    direction: int = 0

    def __init__(self, texture, scale, trajectory=None):
        super(Projectile, self).__init__(texture, scale)
        self.trajectory = trajectory or None

    def update(self):
        if self.path:
            self.position = self.path[0]
            self.path.pop(0)
            self.update_angle()

    def update_angle(self):
        if self.direction is right:
            self.angle -= self.change_angle
        elif self.direction is left:
            self.angle += self.change_angle

    def set_trajectory(self, trajectory):
        self.trajectory = trajectory
        self.set_path()

    def set_path(self):
        # self.path = self.trajectory.get_trimmed_path()
        self.path = self.trajectory.get_path()

    def on_throw(self):
        pass

    def throw(self, trajectory):
        self.set_trajectory(trajectory)
        self.on_throw()

    def on_collision(self):
        pass


class ThrowingKnife(Projectile):
    def __init__(self, knife_object):
        super(ThrowingKnife, self).__init__(knife_object.texture, knife_object.scale)
        self.speed = knife_object.speed
        self.range = knife_object.range * 64
        self.max_speed = knife_object.max_speed
        self.sounds = [arcade.Sound(sound) for sound in knife_object.sounds]
        self.hit_sound = arcade.Sound("resources/sounds/knife_hit_ground.wav")
        self.triangle = None


    def set_direction(self, direction):
        self.direction = direction
        if self.direction == right:
            self.angle = 0
        elif self.direction == left:
            self.angle = 90

    def on_throw(self):
        random.choice(self.sounds).play(.5)

    def update(self):
        super(ThrowingKnife, self).update()
        if self.center_y < 0:
            self.kill()

    def set_angle_change(self, dx, dy, angle):
        self.angle = angle - 45
        self.change_angle = 180 / 40
        # # calculate how much to change the angle each update
        # a = math.degrees(math.atan2(dx, dy))
        # self.change_angle = 60



class ThrowingKnife1(Knife):
    def __init__(self, knife_object):
        super(ThrowingKnife, self).__init__(knife_object.texture, knife_object.scale)
        self.speed = knife_object.speed
        self.range = knife_object.range * 64
        self.max_speed = knife_object.max_speed
        self.sounds = [arcade.Sound(sound) for sound in knife_object.sounds]
        self.hit_sound = arcade.Sound("resources/sounds/knife_hit_ground.wav")
        self.trajectory = None
        self.path = None
        self.direction = 0
        self.ang_change = 0
        self.thrown = False

    def throw(self, trajectory):
        # load trajectory object
        self.trajectory = trajectory
        # load point list from trajectory
        self.path = trajectory.get_path()
        # play throwing sound
        random.choice(self.sounds).play(.3)
        self.thrown = True

    def update(self):
        if self.path:
            self.position = self.path[0]
            self.path.pop(0)
            if self.direction is right:
                self.angle -= self.ang_change
            elif self.direction is left:
                self.angle += self.ang_change

    def set_ang_change(self, ang, change):
        self.angle = ang - 45
        self.ang_change = change

    def set_angle(self, dx, dy, angle):
        self.angle = angle - 45
        # calculate how much to change the angle each update
        a = math.degrees(math.atan2(dy, dx))
        self.ang_change = a / (self.range/self.max_speed)
        # if 80 < angle < 90 or -80 > angle > -90:
        #     self.ang_change *= 1.15
            # self.angle += 24

    def set_direction(self, direction):
        self.direction = direction
        if self.direction == right:
            self.angle = 0
        elif self.direction == left:
            self.angle = 90




# THROWING KNIFE
class ThrowingKnife_Old(arcade.Sprite):
    def __init__(self, parent):
        super().__init__("resources/sprites/item/knife.png", .5)
        self.parent = parent
        self.direction = self.parent.direction
        self.attacked = True
        self.thrown = False
        self.target_x, self.target_y = 0, 0
        self.path = []
        self.trajectory = ()
        self.speed = 2
        self.range = (1*64)
        self.max_velocity = 35
        self.ang_change = 0
        self.projectile = 0
        self.tri = None
        self.sounds = [arcade.Sound(f"resources/sounds/knife_throw{i}.wav") for i in range(3)]
        self.hit_sound = arcade.Sound("resources/sounds/knife_hit_ground.wav")

    def update(self):
        if self.thrown:
            if self.path:
                self.center_y = self.path[0][1]
                self.center_x = self.path[0][0]
                self.path.pop(0)
                if self.direction is right:
                    self.angle -= self.ang_change
                elif self.direction is left:
                    self.angle += self.ang_change
            else:
                self.thrown = False

    def throw(self, trajectory):
        self.projectile = trajectory
        self.path = trajectory.get_path()
        random.choice(self.sounds).play(.5)
        self.thrown = True

    def set_angle(self, dx, dy, angle):
        self.angle = angle - 45
        # if 80 < angle < 95:
        #     self.angle = angle - 90
        # calculate how much to change the angle each update
        a = math.degrees(math.atan2(dx, dy))
        # self.a = -(self.a)
        self.ang_change = a / (self.range/self.speed)
        if 80 < angle < 90 or -80 > angle > -90:
            self.ang_change *= 1.4
            self.angle += 24

    def set_ang_change(self, ang, change):
        self.angle = ang - 45
        self.ang_change = change

    def set_direction(self, direction):
        self.direction = direction
        if direction == right:
            self.change_x = 0
            self.angle = 0
            self.center_x = self.parent.right
            self.center_y = self.parent.center_y - 14
        elif direction == left:
            self.change_x = 0
            self.angle = 90
            self.center_x = self.parent.left
            self.center_y = self.parent.center_y - 10