class Camera:
    def __init__(self, width, height, ppm=1.0):
        self.width = width
        self.height = height
        self.pixels_per_unit = ppm
        self.offset_x = 0.0
        self.offset_y = 0.0

    def world_to_screen(self, x, y):
        sx = (x - self.offset_x) * self.pixels_per_unit
        # Invert Y: 0 in world is the bottom of the screen (self.height)
        sy = self.height - ((y - self.offset_y) * self.pixels_per_unit)
        return int(sx), int(sy)

    def screen_to_world(self, sx, sy):
        x = (sx / self.pixels_per_unit) + self.offset_x
        # Invert Y back to world coordinates
        y = self.offset_y + (self.height - sy) / self.pixels_per_unit
        return x, y
