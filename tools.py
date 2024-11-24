import cv2
from drawable_object import DrawableObject

class Tool:
    def start_action(self, event, *args, **kwargs):
        pass

    def perform_action(self, event, *args, **kwargs):
        pass

    def end_action(self, event, *args, **kwargs):
        pass


class ScaleTool(Tool):
    def __init__(self):
        self.start_x = None
        self.start_y = None

    def start_action(self, event, *args, **kwargs):
        self.start_x, self.start_y = event.x, event.y

    def perform_action(self, event, original_image, scale_factor):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        scale_change = 1 + (dx - dy) / 200

        new_scale_factor = scale_factor * scale_change
        new_scale_factor = max(0.1, min(new_scale_factor, 5.0))

        new_width = int(original_image.shape[1] * new_scale_factor)
        new_height = int(original_image.shape[0] * new_scale_factor)
        resized_image = cv2.resize(original_image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        self.start_x = event.x
        self.start_y = event.y

        return resized_image, new_scale_factor


class TranslateTool:
    def __init__(self):
        self.start_x = 0
        self.start_y = 0
        self.start_image_offset = None

    def start_action(self, event, image_offset):
        self.start_x = event.x
        self.start_y = event.y
        self.start_image_offset = image_offset[:]

    def perform_action(self, event, image_offset):
        if image_offset is None:
            image_offset = [0, 0]

        dx = event.x - self.start_x
        dy = event.y - self.start_y

        image_offset[0] = self.start_image_offset[0] + dx
        image_offset[1] = self.start_image_offset[1] + dy

        return image_offset

class DrawTool(Tool):
    def __init__(self):
        self.current_stroke = None

    def start_action(self, event, image_offset, scale_factor, x_scroll_offset=0, y_scroll_offset=0):
        x = (event.x + x_scroll_offset - image_offset[0]) / scale_factor
        y = (event.y + y_scroll_offset - image_offset[1]) / scale_factor
        # Start a new stroke
        self.current_stroke = DrawableObject(points=[(x, y)])
        return self.current_stroke

    def perform_action(self, event, image_offset, scale_factor, x_scroll_offset=0, y_scroll_offset=0):
        x = (event.x + x_scroll_offset - image_offset[0]) / scale_factor
        y = (event.y + y_scroll_offset - image_offset[1]) / scale_factor
        # Add the new point to the current stroke
        self.current_stroke.points.append((x, y))


class LassoTool(Tool):
    def __init__(self):
        self.lasso_points = []

    def start_action(self, event, image_offset, scale_factor):
        x = (event.x - image_offset[0]) / scale_factor
        y = (event.y - image_offset[1]) / scale_factor
        self.lasso_points = [(x, y)]

    def perform_action(self, event, image_offset, scale_factor):
        x = (event.x - image_offset[0]) / scale_factor
        y = (event.y - image_offset[1]) / scale_factor
        self.lasso_points.append((x, y))

    def end_action(self):
        if len(self.lasso_points) > 2:
            self.lasso_points.append(self.lasso_points[0])


# ---------------- UNDO REDO --------------------#
class HistoryTool(Tool):
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def record_action(self, action_type, params):
        action = {
            "type": action_type,
            "params": params
        }
        self.undo_stack.append(action)
        self.redo_stack.clear()

    def undo(self):

        if not self.undo_stack:
            return None

        action = self.undo_stack.pop()
        self.redo_stack.append(action)


        return action

    def redo(self):

        if not self.redo_stack:
            return None

        action = self.redo_stack.pop()
        self.undo_stack.append(action)

        return action


class RotateTool(Tool):
    def __init__(self):
        self.start_x = None
        self.start_y = None

    def start_action(self, event, *args, **kwargs):
        self.start_x, self.start_y = event.x, event.y

    def perform_action(self, event, original_image, angle):

        dx = event.x - self.start_x
        dy = event.y - self.start_y
        angle_change = (dx - dy) / 5

        new_angle = angle + angle_change

        (h, w) = original_image.shape[:2]
        center = (w // 2, h // 2)

        rotation_matrix = cv2.getRotationMatrix2D(center, new_angle, 1.0)
        rotated_image = cv2.warpAffine(original_image, rotation_matrix, (w, h))

        self.start_x = event.x
        self.start_y = event.y

        return rotated_image, new_angle

