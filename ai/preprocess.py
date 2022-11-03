import cv2
import numpy as np
import os
import glob

from ..common.physical_camera import Camera
from ..common.utils import process_image


root_new = r"/home/mbulger/Documents/Capstone_Project/Capstone-Project-AI-Robot-Car-Maze-Navigation/AI/new_processed_images"

classes = ["LeftTurn", "OffsetLeft", "OffsetRight",
           "OffTrack", "RightTurn", "Straight"]

# Batch preprocess raw images from a directory


def main():
    root = r"/home/mbulger/Documents/Capstone_Project/Capstone-Project-AI-Robot-Car-Maze-Navigation/AI/original_processed_images"

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


if __name__ == "__main__":
    main()
