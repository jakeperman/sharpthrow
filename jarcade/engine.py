from shapes import *
from copy import deepcopy

left = -1
right = 1


class RyanEngine:
    def __init__(self, targets: arcade.SpriteList, gravity, level=None, ground: arcade.SpriteList = None):
        self.surface_list = ground
        self.target_list = targets
        self.objects = arcade.SpriteList()
        self.collider = level.collisions if level else None
        self.gravity = gravity

    def update(self):
        self.objects.update()
        for obj in self.objects:
            if arcade.check_for_collision_with_list(obj, self.target_list):
                obj.path = None

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)

    def draw_trajectory(self, projectile: ProjectileDistanceTrajectory):
        path = projectile.get_sliced(self.target_list)
        arcade.draw_points(path, arcade.color.GOLD, 3)

    def throw_object(self, obj, x0, y0, v0):
        trajectory = self.get_trajectory_from_object(obj, x0, y0, v0)
        obj.set_trajectory(trajectory)
        obj.on_throw()
        obj.set_angle_change(trajectory.angle, self.get_angle_change(trajectory))
        self.add_object(obj)

    def get_trajectory_from_point(self, x1, y1, x2, y2, v):
        tri = StaticTriangle(x1, x2, y1, y2, 100)
        return ProjectileDistanceTrajectory(x1, y1, v, tri.angle, self.gravity)

    def get_trajectory_from_object(self, object, x0, y0, v0, max_velocity=None):
        tri = StaticTriangle(object.center_x, x0, object.center_y, y0, 100)
        if max_velocity and v0 > max_velocity:
            v0 = max_velocity
        return ProjectileDistanceTrajectory(object.center_x, object.center_y, v0, tri.angle, self.gravity)

    def get_angle_change(self, trajectory):
        mid_point = trajectory.get_max_point()
        start_point = trajectory.x0, trajectory.y0
        end_point = trajectory.get_point_of_impact(self.target_list)
        tri = Triangle(start_point, mid_point, end_point)
        v = trajectory.v0
        vy = v * math.sin(math.radians(tri.angle_a()))
        time = (-vy - vy) / -5  # time
        new = deepcopy(trajectory)
        new.slice_at_collision(self.target_list)
        new.trim()
        ln = len(new.get_path())
        chng = (180 - tri.angle_b()) / (time / (1 / 3))
        # if tri.an
        if new.get_index_of_impact(self.target_list) <= new.get_path().index(new.get_max_point()):
            chng = (90 - tri.angle_b()) / (time / (1 / 3))
        return chng


class PhysicsEngine(arcade.PhysicsEnginePlatformer):
    def __init__(self, player, ground: arcade.SpriteList, targets: arcade.SpriteList, gravity, level=None):
        super().__init__(player, ground, gravity)
        self.player = player
        self.surface_list = ground
        self.target_list = targets
        self.objects = arcade.SpriteList()
        self.player.physics_engine = self
        self.collider = level.collisions if level else None
        self.gravity = gravity

    def update(self):
        super(PhysicsEngine, self).update()
        self.objects.update()

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)

    def draw_trajectory(self, projectile):
        path = projectile.get_sliced(self.surface_list)
        arcade.draw_points(path, arcade.color.GOLD, 3)

    def throw_object(self, obj, x0, y0, v0):
        trajectory = self.get_trajectory_from_player(x0, y0, v0)
        obj.set_trajectory(trajectory)
        obj.on_throw()
        obj.set_angle_change(trajectory.angle, self.get_angle_change(trajectory))
        self.player.weapons.append(obj)
        self.add_object(obj)

    def get_trajectory_from_point(self, x1, y1, x2, y2, v):
        tri = StaticTriangle(x1, x2, y1, y2, 100)
        return ProjectileDistanceTrajectory(x1, y1, v, tri.angle, self.gravity)

    def get_trajectory_from_player(self, x0, y0, v0, max_velocity=None):
        tri = StaticTriangle(self.player.center_x, x0, self.player.center_y, y0, 100)
        if max_velocity and v0 > max_velocity:
            v0 = max_velocity
        return ProjectileDistanceTrajectory(self.player.center_x, self.player.center_y, v0, tri.angle, 3)

    def get_angle_change(self, trajectory):
        mid_point = trajectory.get_max_point()
        start_point = trajectory.x0, trajectory.y0
        end_point = trajectory.get_point_of_impact(self.surface_list)
        tri = Triangle(start_point, mid_point, end_point)
        v = trajectory.v0
        vy = v * math.sin(math.radians(tri.angle_a()))
        time = (-vy - vy) / -5  # time
        new = deepcopy(trajectory)
        new.slice_at_collision(self.surface_list)
        new.trim()
        ln = len(new.get_path())
        chng = (180 - tri.angle_b()) / (time / (1 / 3))
        # if tri.an
        if new.get_index_of_impact(self.surface_list) <= new.get_path().index(new.get_max_point()):
            chng = (90 - tri.angle_b()) / (time / (1 / 3))
        return chng
