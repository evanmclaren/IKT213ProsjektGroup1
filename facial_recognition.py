import cv2
import numpy as np
import dlib
from PIL import Image

class SunglassesFilter:
    def __init__(self, predictor_path="shape_predictor_68_face_landmarks.dat", filter_image_path="sunglasses.png"):
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor(predictor_path)
        self.sunglasses_image = cv2.imread(filter_image_path, cv2.IMREAD_UNCHANGED)

    def apply_filter(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector(gray)

        # Create an empty transparent layer for sunglass
        sunglasses_layer = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)

        for face in faces:
            # fetch face landmarks
            landmarks = self.landmark_predictor(gray, face)

            # Extract coordinates for temples
            left_temple_x = landmarks.part(0).x
            right_temple_x = landmarks.part(16).x

            # Find width of the sunglasses based on temple distance
            sunglasses_width = int(right_temple_x - left_temple_x)
            sunglasses_height = int(sunglasses_width * self.sunglasses_image.shape[0] / self.sunglasses_image.shape[1])
            sunglasses_resized = cv2.resize(self.sunglasses_image, (sunglasses_width, sunglasses_height))

            eye_mid_y = int((landmarks.part(36).y + landmarks.part(45).y) / 2)  # Midpoint between eyes
            x_offset = left_temple_x
            y_offset = eye_mid_y - int(sunglasses_height / 2)

            # Extract the alpha channel from the sunglasses image for transparency
            if sunglasses_resized.shape[2] == 4:
                b, g, r, a = cv2.split(sunglasses_resized)
                overlay_color = cv2.merge((b, g, r, a))
            else:
                print("Error: The sunglasses image does not have an alpha channel.")
                continue

            y1, y2 = y_offset, y_offset + sunglasses_height
            x1, x2 = x_offset, x_offset + sunglasses_width
            if y1 < 0 or y2 > image.shape[0] or x1 < 0 or x2 > image.shape[1]:
                continue

            # Extract the region of interest from the sunglasses layer
            sunglasses_layer[y1:y2, x1:x2] = overlay_color

        return sunglasses_layer


# test
if __name__ == "__main__":
    obama_image = cv2.imread("obama.jpg")
    sunglasses_filter = SunglassesFilter()
    sunglasses_layer = sunglasses_filter.apply_filter(obama_image)

    if obama_image.shape[2] == 3:
        obama_image = cv2.cvtColor(obama_image, cv2.COLOR_BGR2BGRA)

    final_image = cv2.addWeighted(obama_image, 1.0, sunglasses_layer, 1.0, 0)

    cv2.imshow("Filtered Image", final_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
