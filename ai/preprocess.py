import cv2
import numpy as np
import os
import glob

from ..common.camera import Camera
from ..common.utils import process_image


root_new = r"/home/mbulger/Documents/Capstone_Project/Capstone-Project-AI-Robot-Car-Maze-Navigation/AI/new_processed_images"


# Option 1 - Batch preprocess raw images from a directory
def main1():
    root = r"/home/mbulger/Documents/Capstone_Project/Capstone-Project-AI-Robot-Car-Maze-Navigation/AI/original_processed_images"

    classes = ["LeftTurn", "OffsetLeft", "OffsetRight",
               "OffTrack", "RightTurn", "Straight"]
    for label in classes:
        print(label)
        path = os.path.join(root, label)
        files = glob.glob(f"{path}/*.png")
        print(path)
        for idx, file_path in enumerate(files):
            img = cv2.imread(file_path)
            print(np.shape(img))
            proc = process_image(img)
            new_path = os.path.join(os.path.join(
                root_new, label), f"{idx}.png")
            cv2.imwrite(new_path, proc)

    return 0


# Option 2 - Preprocess images while taking them, without storing the raw images
def main():
    label = "LeftTurn"
    camera = Camera()
    idx = 0
    print(f"Waiting for input... (class = {label})")
    input()

    with camera as cam:
        while True:
            img = cam.read()
            proc = process_image(img)
            new_path = os.path.join(os.path.join(
                root_new, label), f"{idx}.png")
            cv2.imwrite(new_path, proc)
            idx += 1
            cv2.waitKey(0)


if __name__ == "__main__":
    main1()
