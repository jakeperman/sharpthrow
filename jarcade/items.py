left = -1
right = 1
import arcade

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

    def set_angle_change(self, angle, change):
        if self.direction == right:
            self.angle += angle
        else:
            self.angle += angle - 180
        self.change_angle = change

    def set_trajectory(self, trajectory):
        self.trajectory = trajectory
        self.set_path()

    def set_path(self):
        self.path = self.trajectory.get_trimmed_path()
        # self.path = self.trajectory.get_path()

    def on_throw(self):
        pass

    def throw(self, trajectory):
        self.set_trajectory(trajectory)
        self.on_throw()

    def on_collision(self):
        pass