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
data_path = r"TrackImages\Images1_50"
# data_dir = tf.keras.utils.get_file(fname=data_path)
data_dir = pathlib.Path(data_path)
img_width = 640
img_height = 480

# (x_train, y_train), (x_test, y_test) = data_dir.load_data()


image_count = len(list(data_dir.glob("*/*.png")))
print(image_count)

# Load data with Keras now
# create training dataset and validation dataset


train_ds, val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    labels="inferred",
    seed=4,
    image_size=(img_height, img_width),
    validation_split=0.2,
    subset="both",
    batch_size=32,
)  # we may need to add more parameters here
# val_ds = tf.keras.utils.image_dataset_from_directory(
#     data_dir,
#     seed=4,
#     image_size=(img_height, img_width),
#     validation_split=0.2,
#     subset="validation",
#     batch_size=32,
# )  # and here


def mapper(x):
    if x == "LeftImages":
        return 0
    elif x == "StraightImages":
        return 1
    else:
        return 2


y_train = list(map(mapper, train_ds.class_names))
y_test = list(map(mapper, val_ds.class_names))

numclasses = 3
train_ds.class_names = keras.utils.np_utils.to_categorical(y_train, numclasses)
val_ds.class_names = keras.utils.np_utils.to_categorical(y_test, numclasses)

print("train_ds: ", train_ds.class_names)
print("val_ds: ", val_ds.class_names)

# train_ds = train_ds.unbatch()
# images = list(train_ds.map(lambda x, y: x))
# labels = list(train_ds.map(lambda x, y: y))

# print("length labels:", len(labels))
# print("length images:", len(images))

# val_ds = val_ds.unbatch()
# imagesval = list(val_ds.map(lambda x, y: x))
# labelsval = list(val_ds.map(lambda x, y: y))

# print("length vallabels:", len(imagesval))
# print("length valimages:", len(labelsval))


# print("XXXXXXXXXXXXXXX", train_ds, val_ds)
class_names = train_ds.class_names
num_classes = len(
    class_names
)  # FIX CLASS NAMES THIS DEPENDS ON HOW THE TEST IMAGES FOLDER IS SET UP
# print("class names: ", class_names)
AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(100).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# eventually we will need to specify class names in the training data such as straight, left, right


# add data augmentation to introduce new images to the model generated from the given training set
augmentation_layer = keras.Sequential(
    [
        layers.RandomFlip("horizontal", input_shape=(img_height, img_width, 3)),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
    ]
)

model = Sequential(
    [
        # augmentation_layer,
        layers.Rescaling(1.0 / 255, input_shape=(img_height, img_width, 3)),
        layers.Conv2D(16, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        layers.Dropout(rate=0.25),
        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.Dense(num_classes),
    ]
)


# model = Sequential(
#     [
#         layers.Rescaling(1.0 / 255, input_shape=(img_height, img_width, 3)),
#         layers.Conv2D(6, kernel_size=(5, 5), strides=1, padding="valid"),
#         layers.ReLU(),
#         layers.MaxPooling2D(pool_size=(2, 2), strides=2),
#         layers.Conv2D(16, kernel_size=(5, 5), strides=1, padding="valid"),
#         layers.ReLU(),
#         layers.MaxPooling2D(pool_size=(2, 2), strides=2),
#         layers.Dropout(rate=0.25),
#         layers.Flatten(),
#         layers.Dense(128, activation="relu"),
#         layers.Dense(num_classes),
#     ]
# )

model.compile(
    optimizer="adam",
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)

# view the summary of all the layers in the model
model.summary()

# train the model
epochs = 5
# history = model.fit(
#     x_train,
#     y_train,
#     batch_size=32,
#     epochs=epochs,
#     verbose=1,
#     validation_data=(x_test, y_test),
# )
history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)


# convert to tensorflow lite model
# Convert the model.
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the model.
with open("model.tflite", "wb") as f:
    f.write(tflite_model)
