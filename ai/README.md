# AI

This submodule contains the files pertaining to training the AI model.

We assume that the full version of Tensorflow is already installed, with or without GPU support. *You cannot train a model on the Raspberry Pi itself, as it cannot run the full version of Tensorflow, only Tensorflow Lite (not to mention it would be incredibly slow to train the model on the Pi even if you could)*.

## Trainer
This script takes in a path to the training dataset as input, and outputs a Tensorflow Lite model that can be transferred to and run on the Raspberry Pi using Tensorflow Lite and the `AiSensor`.

Your dataset should contain folders corresponding to the names of the classes you are trying to identify, each containing an arbitrary number of images that correspond to that classification.

To run the trainer:
```bash
python3 -m ai.trainer <INSERT PATH TO DATASET> --epochs <INSERT NUMBER OF EPOCHS>
```
Devising a good model is more of an art than a science, but somewhere between 20-100 epochs tends to produce good results; the primary factor is how fast your computer is.

## Preprocess (Deprecated)
This script takes in a dataset of raw images from the robot, and runs `common.process_image` on them before saving them to a new dataset. You should look at using `RemoteCamera` instead, which allows you to collect training data from the robot remotely, which is much easier since you don't need to fumble around with a USB flash drive or anything.