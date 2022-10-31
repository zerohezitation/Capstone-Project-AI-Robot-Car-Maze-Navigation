import cv2
import numpy as np
import struct
import fcntl
import socket


def grey(image):
  # convert to grayscale
    image = np.asarray(image)
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def gauss(image):
  # Apply Gaussian Blur --> Reduce noise and smoothen image
    return cv2.GaussianBlur(image, (7, 7), 0)


def canny(image):
  # outline the strongest gradients in the image --> this is where lines in the image are
    edges = cv2.Canny(image, 50, 150)
    return edges


def resize(image):
    return cv2.resize(image, (160, 64))


def process_image(image):
    image = gauss(grey(image))
    ret, t = cv2.threshold(image, 125, 255, cv2.THRESH_BINARY)
    image = canny(image)
    #cv2.imshow("im3", image)
    kernel = np.ones((2, 2), np.uint8)
    image = cv2.dilate(image, kernel, iterations=2)
    image = cv2.bitwise_and(image, t)
    #cv2.imshow("im2", image)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    #cv2.imshow("1", image)
    # cv2.waitKey(1)
    return resize(image)


def get_ip(interface: str = "wlan0") -> str:
    # Get the IP address of the specified interface
    # This is usually a statically assigned IP address but if its not
    # then we don't have to update the code
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface.encode('utf_8'))
    packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    return socket.inet_ntoa(packed_addr)
