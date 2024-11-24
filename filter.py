import cv2
import numpy as np
from PIL import Image


class Filter:
    def __init__(self):
        pass

    def apply_blur(self, image, kernel_size=(5, 5)):
        """
        Applies a Gaussian blur filter to the given image.

        Parameters:
        - image: PIL.Image object representing the input image.
        - kernel_size: Tuple representing the size of the Gaussian kernel.

        Returns:
        - A PIL.Image object representing the blurred image.
        """
        # Ensure kernel size is odd and greater than 0
        kernel_size = (kernel_size[0] if kernel_size[0] % 2 == 1 else kernel_size[0] + 1,
                       kernel_size[1] if kernel_size[1] % 2 == 1 else kernel_size[1] + 1)

        # Convert the PIL image to an OpenCV format (numpy array)
        image_np = np.array(image)
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)

        # Apply the Gaussian blur filter using OpenCV
        blurred_image_cv = cv2.GaussianBlur(image_cv, kernel_size, 0)

        # Convert the OpenCV image back to PIL format
        blurred_image_np = cv2.cvtColor(blurred_image_cv, cv2.COLOR_BGR2RGBA)
        blurred_image_pil = Image.fromarray(blurred_image_np)

        return blurred_image_pil

    def apply_sharpen(self, image):
        """
        Applies a sharpening filter to the given image.

        Parameters:
        - image: PIL.Image object representing the input image.

        Returns:
        - A PIL.Image object representing the sharpened image.
        """
        # Convert the PIL image to an OpenCV format (numpy array)
        image_np = np.array(image)
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)

        # Define the sharpening kernel
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])

        # Apply the sharpening filter using OpenCV
        sharpened_image_cv = cv2.filter2D(src=image_cv, ddepth=-1, kernel=kernel)

        # Convert the OpenCV image back to PIL format
        sharpened_image_np = cv2.cvtColor(sharpened_image_cv, cv2.COLOR_BGR2RGBA)
        sharpened_image_pil = Image.fromarray(sharpened_image_np)

        return sharpened_image_pil
