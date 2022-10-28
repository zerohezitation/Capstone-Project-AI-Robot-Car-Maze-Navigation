# This is the main python program used to track the lane lines of the road

import cv2
import time
import sys
import numpy as np
import argparse
import utils

def run(
    model: str,
    camera_id: int,
    width: int,
    height: int,
    num_threads: int,
    enable_edgetpu: bool,
) -> None:
    """Continuously run inference on images acquired from the camera.

    Args:
      model: Name of the TFLite object detection model.
      camera_id: The camera id to be passed to OpenCV.
      width: The width of the frame captured from the camera.
      height: The height of the frame captured from the camera.
      num_threads: The number of CPU threads to run the model.
      enable_edgetpu: True/False whether the model is a EdgeTPU model.
    """

    # Variables to calculate FPS
    counter, fps = 0, 0
    start_time = time.time()

    # Start capturing video input from the camera
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Visualization parameters
    row_size = 20  # pixels
    left_margin = 24  # pixels
    text_color = (0, 0, 255)  # red
    font_size = 1
    font_thickness = 1
    fps_avg_frame_count = 10

    # Continuously capture images from the camera and run inference
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            sys.exit(
                "ERROR: Unable to read from webcam. Please verify your webcam settings."
            )

        counter += 1
        image = cv2.flip(image, 1)

        # grayscale the image and noise reduction using gaussian blur
        image = np.asarray(image)
        grayImage = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        grayImage = cv2.GaussianBlur(grayImage, (5, 5), 0)
        cv2.imshow("gray image", grayImage)
        
        # canny edge detection
        edges = cv2.Canny(grayImage, 50, 150)
        cv2.imshow("canny image", edges)
    cap.release()
    cv2.destroyAllWindows
# Find the region of the image that we want to isolate and cover up everything else


# main functions
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--model",
        help="Path of the object detection model.",
        required=False,
        default="efficientdet_lite0.tflite",
    )
    parser.add_argument(
        "--cameraId", help="Id of camera.", required=False, type=int, default=0
    )
    parser.add_argument(
        "--frameWidth",
        help="Width of frame to capture from camera.",
        required=False,
        type=int,
        default=640,
    )
    parser.add_argument(
        "--frameHeight",
        help="Height of frame to capture from camera.",
        required=False,
        type=int,
        default=480,
    )
    parser.add_argument(
        "--numThreads",
        help="Number of CPU threads to run the model.",
        required=False,
        type=int,
        default=4,
    )
    parser.add_argument(
        "--enableEdgeTPU",
        help="Whether to run the model on EdgeTPU.",
        action="store_true",
        required=False,
        default=False,
    )
    args = parser.parse_args()

    run(
        args.model,
        int(args.cameraId),
        args.frameWidth,
        args.frameHeight,
        int(args.numThreads),
        bool(args.enableEdgeTPU),
    )


if __name__ == "__main__":
    main()
