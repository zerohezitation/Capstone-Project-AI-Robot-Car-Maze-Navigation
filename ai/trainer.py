import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras import layers
import keras

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

epochs = 150

# TODO add arguments parser

#data_path = r"/home/mbulger/Documents/Capstone_Project/Capstone-Project-AI-Robot-Car-Maze-Navigation/AI/TrackImages/Images1_50"
data_path = r"/home/mbulger/Documents/Capstone_Project/Capstone-Project-AI-Robot-Car-Maze-Navigation/dataset_09_23_24_826977"


def train_model():
    data_dir = Path(data_path)
    img_width = 160  # 640
    img_height = 64  # 480
    batch_size = 32
    # class_names = ["LeftTurn", "OffsetLeft",
    # "Straight", "OffsetRight", "RightTurn"]
    class_names = ["OffsetRight", "Straight", "OffsetLeft"]

    train_ds, val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",  # labels are from directory names
        label_mode="int",
        class_names=class_names,
        color_mode="grayscale",  # use only 1 channel
        seed=4,  # must set a specific seed for deterministic validation split
        image_size=(64, 160),  # resize input images down to 160x64
        validation_split=0.2,  # use 20% of training images for validation
        subset="both",  # return training dataset and validation dataset
        batch_size=batch_size,
    )

    shape = None
    for image_batch, labels_batch in val_ds:
        shape = image_batch.shape
        print(image_batch.shape)
        print(labels_batch)
        break

    print(train_ds, val_ds)
    print(np.shape(train_ds), np.shape(val_ds))

    AUTOTUNE = tf.data.AUTOTUNE

    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    augmentation_layer = keras.Sequential(
        [
            # layers.RandomFlip("horizontal", input_shape=(
            #    img_height, img_width, 3)),
            # layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
        ]
    )

    model = Sequential(
        [
            # augmentation_layer,
            layers.Rescaling(
                1.0 / 255, input_shape=(img_height, img_width, 1)),  # 3)),
            layers.Conv2D(16, 3, padding="same", activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(32, 3, padding="same", activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, padding="same", activation="relu"),
            layers.MaxPooling2D(),
            layers.Dropout(rate=0.25),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(len(class_names), activation='softmax')
        ]
    )

    model.build(shape)

    model.compile(
        optimizer="adam",
        # loss=tf.keras.losses.CategoricalCrossentropy(from_logits=False),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
        # metrics=["accuracy"],
        metrics=["accuracy",
                 tf.keras.metrics.SparseTopKCategoricalAccuracy(k=2)]
    )

    model.summary()

    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)

    return model, history


def visualize(history):
    acc1 = history.history['accuracy']
    val_acc1 = history.history['val_accuracy']
    acc = history.history['sparse_top_k_categorical_accuracy']
    val_acc = history.history['val_sparse_top_k_categorical_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(epochs)

    plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.plot(epochs_range, acc1, label='Training Accuracy1')
    plt.plot(epochs_range, val_acc1, label='Validation Accuracy1')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plt.show()


def export_model(model):
    print("Exporting the model...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

    # Save the model.
    with open("model.tflite", "wb") as f:
        f.write(tflite_model)

    print("Finished exporting the model.")


def main():
    (model, history) = train_model()
    export_model(model)
    visualize(history)


if __name__ == "__main__":
    main()
