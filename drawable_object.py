class DrawableObject:
    def __init__(self, points, color="black", width=3):
        self.original_points = points.copy()  # Store original points for scaling
        self.points = points.copy()  # Working copy for display
        self.color = color
        self.width = width
