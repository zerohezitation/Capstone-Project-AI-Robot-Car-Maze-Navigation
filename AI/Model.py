from email.mime import image
import pathlib
import PIL
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from tensorflow import keras

from keras.models import Sequential
from keras import layers
import keras

# load the dataset --- FIGURE THIS PART OUT IT DOESNT WORK RIGHT NOW
data_path = "/Users/mgriffin/OneDrive/Documents/CapstoneProject/repo/Capstone-Project-AI-Robot-Car-Maze-Navigation/TrackImages"
data_dir = tf.keras.utils.get_file("TrackImages", origin=data_path, untar=True)
data_dir = pathlib.Path(data_dir)

image_count = len(list(data_dir.glob("*/*.png")))
print(image_count)

# Load data with Keras now
# create training dataset and validation dataset
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir, validation_split=0.2, subset="training"
)  # we may need to add more parameters here
val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir, validation_split=0.2, subset="validation"
)  # and here

# eventually we will need to specify class names in the training data such as straight, left, right
