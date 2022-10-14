import cv2
import numpy as np


def grey(image):
  # convert to grayscale
    image = np.asarray(image)
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

  # Apply Gaussian Blur --> Reduce noise and smoothen image


def gauss(image):
    return cv2.GaussianBlur(image, (7, 7), 0)

  # outline the strongest gradients in the image --> this is where lines in the image are


def canny(image):
    edges = cv2.Canny(image, 50, 150)
    return edges


def resize(image):
    return cv2.resize(image, (640, 480))
