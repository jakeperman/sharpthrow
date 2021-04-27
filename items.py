import arcade
import math
import random
frames_per_update = 3
left = -1
right = 1



# THROWING KNIFE
class ThrowingKnife(arcade.Sprite):
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
        # update the position and direction while not attacking
        # print(f"target_x: {self.target_x} current_x: {self.center_x}")
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