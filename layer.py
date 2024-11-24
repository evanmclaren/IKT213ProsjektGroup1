from PIL import Image

class Layer:
    def __init__(self, width, height, name="Layer"):
        self.width = width
        self.height = height
        self.name = name
        self.image = None
        self.visible = True
        self.offset = [0, 0]
        self.brush_strokes = []

    # Add this method
    def set_offset(self, x_offset, y_offset):
        self.offset = [x_offset, y_offset]


    def update_image(self, image):
        self.image = image

    def get_image(self):
        return self.image

    def get_offset(self):
        return self.offset

    def add_brush_stroke(self, stroke):
        self.brush_strokes.append(stroke)
