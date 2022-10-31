import cv2
import numpy as np
import sys
from collections import deque
import time
#import matplotlib.pyplot as plt

from .sensor import Sensor
from common.camera import Camera
from common.utils import *

# TODO: This needs to be cleaned up a lot, this is the result of a lot of experimenting to see what gives the best results

"""
AngleSensor

You can run this file standalone to test out the sensor without running the middleware:

python3 -m middleware.devices.sensors.angle_sensor
"""


class AngleSensor(Sensor):
    camera = None
    prev_angle = None
    data = None

    def __init__(self, camera: Camera) -> None:
        super().__init__()
        self.name = "angle"

        self.camera = camera
        self.data = deque(maxlen=20)

    def canny(self, copy):
        copy = gauss(copy)
        sigma = np.std(copy)
        mean = np.median(copy)
        lower = int(max(0, (mean - sigma)))
        upper = int(min(255, (mean + sigma)))

        edges = cv2.Canny(copy, lower, upper)
        return edges

    def run(self) -> float:
        image = self.camera.read()
        hls = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)

        cv2.imshow("hls", hls)

        lower_white1 = np.array([0, 0, 0])
        higher_white1 = np.array([50, 200, 255])
        mask1 = cv2.inRange(image, lower_white1, higher_white1)
        kernel = np.ones((50, 50), np.uint8)
        mask1 = 255 - cv2.dilate(mask1, kernel, iterations=1)
        cv2.imshow("mask1", mask1)

        lower_white = np.array([0, 125, 0])
        higher_white = np.array([255, 255, 255])
        mask = cv2.inRange(image, lower_white, higher_white)
        cv2.imshow("mask", mask)

        mask = cv2.bitwise_and(mask, mask, mask=mask1)
        cv2.imshow("mask_c", mask)

        image = cv2.bitwise_and(hls, hls, mask=mask)
        cv2.imshow("img1", image)
        image = self.canny(image)
        cv2.imshow("img", image)

        cv2.waitKey(1)
        return None

    def run_bad(self) -> float:
        image = self.camera.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        cv2.imshow("t0", image[:, :, 1])
        image = image[:, :, 1]

        #lower_white = np.array([0, 50, 0])
        #higher_white = np.array([255, 255, 255])
        #mask = cv2.inRange(image, lower_white, higher_white)
        #cv2.imshow("mask", mask)
        # Bitwise-AND mask and original image
        #image = cv2.bitwise_and(image, image, mask=mask)
        #ret, image = cv2.threshold(image, 100, 255, cv2.THRESH_OTSU)
#        image = gauss(grey())
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #image = cv2.addWeighted(image, 5, image, 0, 0)
        #image = cv2.equalizeHist(image)
        cv2.imshow("b3", image)
        alpha = 1
        beta = 0

        image = cv2.blur(image, ksize=(5, 5))
        v = np.median(image)
        sigma = 0.3
        # ---- apply optimal Canny edge detection using the computed median----
        lower_thresh = int(max(0, (1.0 - sigma) * v))
        upper_thresh = int(min(255, (1.0 + sigma) * v))
        image = cv2.Canny(image, 50, 150)
        cv2.imshow("canny", image)
        cv2.waitKey(1)
        # image = cv2.normalize(image, None, alpha, beta,
        #                      norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        #image = image.astype(np.uint8)
        #image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        #image = image / np.max(image)
        #image = image.astype(np.uint8)
        ret, image = cv2.threshold(
            image, np.max(image) - 50, 255, cv2.THRESH_BINARY)
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.erode(image, kernel, iterations=12)
        cv2.imshow("b4", image)
        cv2.waitKey(1)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        image = cv2.morphologyEx(
            image, cv2.MORPH_OPEN, kernel, iterations=4)
        cv2.imshow("opening", image)

        return None

        v = np.median(image)
        sigma = 0.1

        # ---- apply optimal Canny edge detection using the computed median----
        lower_thresh = int(max(0, (1.0 - sigma) * v))
        upper_thresh = int(min(255, (1.0 + sigma) * v))
        image = cv2.Canny(image, lower_thresh, upper_thresh, 5)
        #image = gauss(grey(self.camera.read()))
        # t = cv2.adaptiveThreshold(image, 255,
        #                          cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 5)
        cv2.imshow("t1", image)
        cv2.waitKey(1)
        return None
        ret, t = cv2.threshold(image, 100, 255, cv2.THRESH_OTSU)

        image = self.canny(t)

        kernel = np.ones((2, 2), np.uint8)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        cv2.imshow("t", image)

        cnts = cv2.findContours(
            image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = list(cnts)
        cnts.sort(key=lambda x: cv2.contourArea(x), reverse=True)
        angles = []
        for c in cnts:
            #c = max(cnts, key = lambda x: cv2.arcLength(x, False))
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            image = cv2.drawContours(
                image, [c], -1, (255, 255, 255), -1)

        cv2.imshow("i", image)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        opening = cv2.morphologyEx(
            image, cv2.MORPH_CLOSE, kernel, iterations=4)
        cv2.imshow("opening", opening)

        cv2.waitKey(1)
        return None

    def run_curr(self) -> float:
        image = gauss(grey(self.camera.read()))
        t = cv2.adaptiveThreshold(image, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 10)
        cv2.imshow("t", t)
        image = self.canny(image)
        cv2.imshow("im3", image)
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=2)
        image = cv2.bitwise_and(image, t)
        cv2.imshow("im2", image)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

        cnts = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = list(cnts)
        cnts.sort(key=lambda x: cv2.contourArea(x), reverse=True)
        angles = []
        for c in cnts:
            #c = max(cnts, key = lambda x: cv2.arcLength(x, False))
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            image = cv2.drawContours(
                image, [c], -1, (255, 255, 255), -1)
        image = cv2.erode(image, kernel, iterations=12)

        lines = cv2.HoughLinesP(
            image, 2, np.pi/180, 100, np.array([]), minLineLength=50, maxLineGap=5)
        #cline = average(image, lines)

        # averaged_lines = average(copy, lines)
        # print(averaged_lines)
        # #centerLine = average(copy, averaged_lines)
        # #print("centerline", centerLine)
        # black_lines = display_lines(copy, averaged_lines)
        # # taking wighted sum of original image and lane lines image
        # lanes = cv2.addWeighted(copy, 0.8, black_lines, 1, 1)
        # cv2.imshow("lanes", lanes)

        if lines is not None and all(map(lambda x: x is not None, lines)):
            centerline = np.vstack(lines).sum(axis=0) / len(lines)
            #centerline = cline
            x1, y1, x2, y2 = centerline
            cline = display_lines(image, [centerline])
            lanes = cv2.addWeighted(image, 0.8, cline, 1, 1)
            cv2.imshow("lanes2", lanes)
            slope = ((np.arctan((y2 - y1) / (x2 - x1)) %
                     np.pi * 2) - np.pi) * (180 / np.pi)
            self.prev_angle = slope
            self.data.append(slope)

        cv2.imshow("im", image)

        cv2.waitKey(1)
        if len(self.data) < 5:
            return None

        return moving_average(self.data, len(self.data)-1)[-1]

    def run2(self) -> float:
        image = gauss(grey(self.camera.read()))
        ret, t = cv2.threshold(image, 40, 255, cv2.THRESH_BINARY)

        #image_path = r"./straight_img15.png"
        #image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        copy = np.copy(image)
        cv2.imshow("OG", copy)

        sigma = np.std(copy)
        mean = np.mean(copy)
        lower = int(max(0, (mean - sigma)))
        upper = int(min(255, (mean + sigma)))

        edges = cv2.Canny(copy, lower, upper)
        edges = cv2.bitwise_and(edges, t)
        #edges = copy

        # inverted = cv2.bitwise_not(edges)
        # kernel = np.ones((10, 10), np.uint8)
        # #inverted = cv2.dilate(inverted,kernel,iterations = 1)
        # inverted = cv2.erode(inverted, kernel, iterations=3)
        # cnts = cv2.findContours(
        #     inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        # for c in cnts:
        #     pass
        #     #cv2.drawContours(inverted, [c], -1, (255, 255, 255), -1)
        # cv2.imshow("inv", inverted)

        #isolated = region(edges)
        isolated = edges

        thresh_img = isolated
        kernel = np.ones((1, 1), np.uint8)
        thresh_img = cv2.dilate(thresh_img, kernel, iterations=5)
        thresh_img = cv2.morphologyEx(thresh_img, cv2.MORPH_CLOSE, kernel)
        #thresh_img = cv2.erode(thresh_img, kernel, iterations=1)
        # thresh_img = cv2.threshold(
        #    isolated, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(
            thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = list(cnts)
        cnts.sort(key=lambda x: cv2.contourArea(x), reverse=True)
        angles = []
        for c in cnts:
            #c = max(cnts, key = lambda x: cv2.arcLength(x, False))
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            thresh_img = cv2.drawContours(
                thresh_img, [c], -1, (255, 255, 255), -1)
        #cv2.drawContours(thresh_img, [c], -1, (255, 255, 255), -1)
        cv2.imshow("tresh", thresh_img)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        opening = cv2.morphologyEx(
            thresh_img, cv2.MORPH_OPEN, kernel, iterations=4)
        cv2.imshow("opening", opening)

        cnts = cv2.findContours(
            opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = list(cnts)
        cnts.sort(key=lambda x: cv2.arcLength(x, True), reverse=True)
        copy3 = np.copy(image)
        angles = []
        for c in cnts[:2]:
            #c = max(cnts, key = lambda x: cv2.arcLength(x, False))
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            opening = cv2.drawContours(
                opening, [box], -1, (255, 255, 255), -1)

            rows, cols = image.shape[:2]
            [vx, vy, x, y] = cv2.fitLine(c, cv2.DIST_L2, 0, 0.01, 0.01)
            lefty = np.clip(int((-x*vy/vx) + y), -99999, 99999)
            righty = np.clip(int(((cols-x)*vy/vx)+y), -99999, 99999)

            copy3 = cv2.line(copy3, (cols-1, righty),
                             (0, lefty), (255, 255, 255), 2)

            x1, y1, x2, y2 = (cols-1, righty, 0, lefty)
            angles.append(get_angle_from__points(x1, y1, x2, y2))

        cv2.waitKey(1)
        cv2.imshow("copy3", copy3)
        cv2.imshow("edges", edges)
        cv2.imshow("isolated", isolated)
        # print("HISOGRAM: ", histogram.size)
        # cv2.waitKey(0)

        #x1, y1, x2, y2 = (cols-1,righty, 0,lefty)
        # slope = ((np.arctan((y2 - y1) / (x2 - x1)) %
        #         np.pi * 2) - np.pi) * (180 / np.pi)
        # print(angles)
        #slope = np.average(angles)
        #self.prev_angle = slope
        # self.data.append(slope)

        # cv2.waitKey(1)
        # if len(self.data) == 0:
        #    return None

        # return moving_average(self.data, 10)[-1]

        # DRAWING LINES: (order of params) --> region of interest, bin size (P, theta), min intersections needed, placeholder array,
        lines = cv2.HoughLinesP(
            opening, 2, np.pi/180, 100, np.array([]), minLineLength=50, maxLineGap=5)

        # averaged_lines = average(copy, lines)
        # print(averaged_lines)
        # #centerLine = average(copy, averaged_lines)
        # #print("centerline", centerLine)
        # black_lines = display_lines(copy, averaged_lines)
        # # taking wighted sum of original image and lane lines image
        # lanes = cv2.addWeighted(copy, 0.8, black_lines, 1, 1)
        # cv2.imshow("lanes", lanes)

        if lines is not None and all(map(lambda x: x is not None, lines)):
            centerline = np.vstack(lines).sum(axis=0) / len(lines)
            x1, y1, x2, y2 = centerline
            cline = display_lines(copy, [centerline])
            lanes = cv2.addWeighted(copy, 0.8, cline, 1, 1)
            cv2.imshow("lanes2", lanes)
            slope = ((np.arctan((y2 - y1) / (x2 - x1)) %
                     np.pi * 2) - np.pi) * (180 / np.pi)
            self.prev_angle = slope
            self.data.append(slope)

        cv2.waitKey(1)
        if len(self.data) < 10:
            return None

        return moving_average(self.data, 10)[-1]


def moving_average(s, n):
    # return np.convolve(x, np.ones(w), 'valid') / w
    s = list(s)
    ema = []
    j = 1

    # get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)

    # EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(((s[n] - sma) * multiplier) + sma)

    # now calculate the rest of the values
    for i in s[n+1:]:
        tmp = ((i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)

    return ema


def region(image):
    height, width = image.shape
    # isolate the gradients that correspond to the lane lines
    triangle = np.array([
        [(0, height-130), (0, 50), (width, 50), (width, height-130)]
    ])
    # create a black image with the same dimensions as original image
    mask = np.zeros_like(image)
    # create a mask (triangle that isolates the region of interest in our image)
    mask = cv2.fillPoly(mask, triangle, 255)
    mask = cv2.bitwise_and(image, mask)
    return mask


def display_lines(image, lines):
    lines_image = np.zeros_like(image)
    # make sure array isn't empty
    if lines is not None:
        for line in filter(lambda x: x is not None, lines):
            x1, y1, x2, y2 = np.clip(line, -10000, 10000).astype(int)
            # draw lines on a black image
            cv2.line(lines_image, (x1, y1), (x2, y2), (255, 0, 0), 10)

    return lines_image


def average(image, lines):
    left = []
    right = []
    if lines is not None:
        for line in filter(lambda x: x is not None, lines):
            x1, y1, x2, y2 = np.clip(line.reshape(4), -10000, 10000)
            # fit line to points, return slope and y-int
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            slope = parameters[0]
            y_int = parameters[1]
            # lines on the right have positive slope, and lines on the left have neg slope
            if slope < 0:
                left.append((slope, y_int))
            else:
                right.append((slope, y_int))

    # takes average among all the columns (column0: slope, column1: y_int)
    right_avg = np.average(right, axis=0)
    left_avg = np.average(left, axis=0)
    # create lines based on averages calculates
    left_line = make_points(image, left_avg)
    right_line = make_points(image, right_avg)
    return np.array([left_line, right_line])


def make_points(image, average):
    try:
        slope, y_int = average
        y1 = image.shape[0]
        # how long we want our lines to be --> 3/5 the size of the image
        y2 = int(y1 * (3/5))
        # determine algebraically
        x1 = (y1 - y_int) // slope
        x2 = (y2 - y_int) // slope
        return np.array(np.clip([x1, y1, x2, y2], -10000, 1000).astype(int))
    except TypeError:
        return None


def get_angle_from__points(x1, y1, x2, y2):
    slope = ((np.arctan((y2 - y1) / (x2 - x1)) %
              np.pi * 2) - np.pi) * (180 / np.pi)
    return slope


if __name__ == "__main__":
    camera = Camera()
    with camera as cam:
        sensor = AngleSensor(cam)
        while True:
            print(sensor.run())
            time.sleep(0.05)
