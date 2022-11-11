# Utils

This submodule contains various classes and utility functions that are command between the AI and Middleware modules.

## Buffer
The `Buffer` class facilitates communication between two threads. A producer thread should "own" the `Buffer`, and periodically `write` updated values to it. When a consumer thread `read`s the `Buffer`, it waits until the producer writes to it (triggering an event), ensuring the consumer does not waste resources doing the same processing on a given input more than once.


**Usage**
```python
from common.buffer import Buffer

buffer = Buffer()
buffer.write("new value")
value = buffer.read_and_write("newer value") # read the current value of the buffer (value == "new value"), then overwrite it afterwards
value = buffer.read() # value == "newer value"
```
___

## Camera
`Camera` is the parent class that all other cameras (`PhysicalCamera`, `ProcessedCamera`, and `RemoteCamera`) inherit; you shouldn't use this class directly. At its core, a `Camera` owns a `Buffer`, which it is continually writing still frames to. Another thread is able to `read` from the camera, which returns the most recent still frame that has been written to the buffer.

### PhysicalCamera
A basic camera that reads frames from a camera physically connected to the robot (usually a USB camera, but it can be any camera recognized by the V4L2 backend on Linux). We use the OpenCV2 `VideoCapture` to implement this. 
By default, we set the video capture to 320x240@25fps, which is the highest frame rate you can get on the LABISTS robot camera. Note that if you are using a different camera, you should run `v4l2-ctl --list-formats` in the terminal to see the supported modes for your specific hardware; otherwise you may see these parameters will not get correctly applied to the camera.
You can optionally provide a `cam_port` to the constructor to specify the ID of a certain camera if more than one is connected.

**Usage**
```python
from common.physical_camera import PhysicalCamera

with PhysicalCamera() as camera:
  img = camera.read()
```

### ProcessedCamera
This is a "virtual" camera; that is, it takes in raw frames from some other `Camera` object (usually either a `PhysicalCamera` or `RemoteCamera`), and uses OpenCV2 to do processing on those frames before publishing them to a new buffer. Since this class takes in a `Camera` as input, and is itself also a `Camera`, it can be seen as a real-time processing pipeline for a camera.
To see more details about the exactly processing on these frames, see `process_image` below, but the gist is the that we want to shrink the images down to a smaller size, turn it to binary black/white pixels, and detect the white rectangles in the image, with the hope that these rectangles represent the lane lines of the road.

**Why do we need a `ProcessedCamera`?** While this certainly bottlenecks how fast we can run the AI model, doing a bit of preprocessing on the camera frames drastically improves the accuracy and reliability of our model. Doing this preprocessing means that the model is less likely to get confused by irrelevant factors in the image, particularly when the robot is placed in a new environment. 

**Usage**
```python
from common.physical_camera import PhysicalCamera
from common.processed_camera import ProcessedCamera

with PhysicalCamera() as physical_cam:
  with ProcessedCamera() as proc_cam:
    img = proc_cam.read()
```

### RemoteCamera
This class connects to a host running on the same LAN, which must be running either the middleware in its entirety, or the streamer program by itself. Once the `RemoteCamera` is connected to the `Streamer`, the `RemoteCamera` will start decoding the Base64 frames that are sent to it, before storing them in a buffer. This allows you to view the robot's video stream in real time while the robot is running, or test out the `ProcessedCamera` or `TrackOffsetSensor` on a remote machine before sending it over to the robot, and more.

**Usage**
```python
from common.remote_camera import RemoteCamera

with RemoteCamera() as stream:
  img = stream.read()
```

You can also run `common.remote_camera` by itself to get some helpful feature, using the command:
```bash
python3 -m common.remote_camera <INSERT THE ROBOT IP ADDRESS> -p <INSERT PORT OF STREAMER> --mode <INSERT MODE>
```
The port defaults to 8125. 
The below table documents the various modes you can pass:
| Mode      | Description |
| ----------- | ----------- |
| view | View the raw frames being sent from the Streamer |
| view_p | Spawn a `ProcessedCamera` using the frames being sent to the `RemoteCamera`, and display the processed frames. *Note that the processing is done on the remote machine, not the Raspberry Pi*. |
| ai | Test out the current `model.tflite` by processing the frames and spawning a `TrackOffsetSensor`. *Note that the processing and Tensorflow interpreter runs on the `RemoteCamera` side, not the Raspberry Pi*. |
| capture | Easily capture training data by saving the current frame to disk when you press enter. |
All of these modes require OpenCV to be installed. To use the "ai" mode, you must have either Tensorflow or Tensorflow Lite installed on the `RemoteCamera` side.
___ 

## Utils
This file contains a collection of functions that primarily pertain to computer vision and image processing.

`process_image(image)`: Takes in a raw camera frame (usually from `PhysicalCamera` or `RemoteCamera`), turns it grayscale, and performs a Gaussian blur. Then, uses a binary threshold to convert from grayscale to pure white and black pixels, before doing Canny line detection (and other morphological processing) to return a frame that outlines the major rectangular shapes in the image, with the hope that the majority of these detected shapes are the lane lines in front of the robot.

`get_ip(interface: str = "wlan0")`: Gets the IP address associated with the specified network interface (defaults to the first wireless interface on the Raspberry Pi, "wlan0", since this is the interface that the access point will be running on). This helper function means that the robot will always try to use the proper IP address without needed to update the source code or a configuration file (although this doesn't guarantee that ports 8124 or 8125 will be open).
