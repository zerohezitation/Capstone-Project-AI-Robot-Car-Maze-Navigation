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


num_classes = len(
    class_names
)  # FIX CLASS NAMES THIS DEPENDS ON HOW THE TEST IMAGES FOLDER IS SET UP

img_width = 640
img_height = 480


model = Sequential(
    [
        layers.Rescaling(1.0 / 255, input_shape=(img_height, img_width, 3)),
        layers.Conv2D(16, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.Dense(num_classes),
    ]
)

model.compile(
    optimizer="adam",
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)

# view the summary of all the layers in the model
model.summary()

# train the model
epochs = 10
history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)
