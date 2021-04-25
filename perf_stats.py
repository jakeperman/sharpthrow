import arcade
import timeit

class FpsCounter:

    def __init__(self):
        # --- Variables for our statistics

        # Time for on_update
        self.processing_time = 0

        # Time for on_draw
        self.draw_time = 0

        # Variables used to calculate frames per second
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None


    def draw_fps(self, func):
        # Start timing how long this takes
        start_time = timeit.default_timer()

        # --- Calculate FPS
        fps_calculation_freq = 60
        # Once every 60 frames, calculate our FPS
        if self.frame_count % fps_calculation_freq == 0:
            # Do we have a start time?
            if self.fps_start_timer is not None:
                # Calculate FPS
                total_time = timeit.default_timer() - self.fps_start_timer
                self.fps = fps_calculation_freq / total_time
            # Reset the timer
            self.fps_start_timer = timeit.default_timer()
        # Add one to our frame count
        self.frame_count += 1
        func()
        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, self.left_view + 10, self.top_view - 25, arcade.color.BLACK, 18)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, self.left_view + 10, self.top_view - 50, arcade.color.BLACK, 18)

        if self.fps is not None:
            output = f"FPS: {self.fps:.0f}"
            arcade.draw_text(output, self.left_view + 10, self.top_view - 75, arcade.color.BLACK, 18)

        # Stop the draw timer, and calculate total on_draw time.
        self.draw_time = timeit.default_timer() - start_time
        
    def update_time(self, func, delta_time: float):
        start_time = timeit.default_timer()

        if self.frame > 60:
            self.frame = 0
        # run func
        func(delta_time)
        
        self.processing_time = timeit.default_timer() - start_time