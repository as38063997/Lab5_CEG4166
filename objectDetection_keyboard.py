## Object detection in stingray using TensorFlow lite  
## Save the file as object_detection.py 
## Lab 3 

import os 
import argparse 
import cv2 
import numpy as np 
import sys 
import time 
from threading import Thread 
import importlib.util 
import threading 
import tty 
import termios 

class Video_PiCamera:
    def __init__(self, resolution=(640, 480), framerate=60):
        # Initializing the Picamera of the Stingray 
        self.stream = cv2.VideoCapture(0) 
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) 
        self.stream.set(3, resolution[0])
        self.stream.set(4, resolution[1])
        
        (self.grabbed, self.frame) = self.stream.read()  # Reading the initial frame from the video stream 
        self.stopped = False 
    
    def start(self): 
        Thread(target=self.update, args=()).start()  # Starting the thread to read from the video stream 
        return self 
    
    def update(self): 
        while True: 
            if self.stopped: 
                self.stream.release()  # Stop the thread when camera is stopped 
                return 
            (self.grabbed, self.frame) = self.stream.read()  # Read the next frame if the camera is running 
    
    def read(self): 
        return self.frame  # The most recent frame captured from the Picamera 
    
    def stop(self): 
        self.stopped = True  # Stops the thread and camera  

# Parsing the arguments for the TensorFlow Lite input 
parser = argparse.ArgumentParser() 
parser.add_argument('--modeldir', required=True) 
parser.add_argument('--graph', default='detect.tflite') 
parser.add_argument('--labels', default='labelmap.txt') 
parser.add_argument('--threshold', default=0.5) 
parser.add_argument('--resolution', default='600x300') 
args = parser.parse_args() 

model = args.modeldir 
graph_n = args.graph 
label_ = args.labels 
minimum_confidence = float(args.threshold) 
resW, resH = args.resolution.split('x') 
imW, imH = int(resW), int(resH) 

# Import the TensorFlow Lite libraries 
pkg = importlib.util.find_spec('tflite_runtime') 
if pkg: 
    from tflite_runtime.interpreter import Interpreter 
else: 
    from tensorflow.lite.python.interpreter import Interpreter 

current_dir = os.getcwd()  # Get path to the current directory  
tflite_directory = os.path.join(current_dir, model, graph_n)  # Path to the .tflite file with the object detection model 
label_destination = os.path.join(current_dir, model, label_)  # Path to the label map file 

with open(label_destination, 'r') as f:  # Load the label map 
    labels = [line.strip() for line in f.readlines()] 

if labels[0] == '???':  # First label is always '???', which has to be removed to avoid errors 
    del(labels[0]) 

model_interpreter = Interpreter(model_path=tflite_directory) 
model_interpreter.allocate_tensors() 

input = model_interpreter.get_input_details() 
output = model_interpreter.get_output_details() 
height = input[0]['shape'][1] 
width = input[0]['shape'][2] 

floating_model = (input[0]['dtype'] == np.float32) 
input_mean = 127.5 
input_std = 127.5 

# Initializing the video streaming 
Video_PiCamera = Video_PiCamera(resolution=(imW, imH), framerate=60).start() 
time.sleep(1) 

def detection(any, any2): 
    while True: 
        original_frame = Video_PiCamera.read()  # Grab frame from video stream 
        
        # Duplicating the frame and adjusting the size of it 
        frame = original_frame.copy() 
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        frame_resized = cv2.resize(frame_rgb, (width, height)) 
        input_data = np.expand_dims(frame_resized, axis=0) 

        # Normalize pixels if using a non-quantized model 
        if floating_model: 
            input_data = (np.float32(input_data) - input_mean) / input_std 

        model_interpreter.set_tensor(input[0]['index'], input_data) 
        model_interpreter.invoke() 

        box = model_interpreter.get_tensor(output[0]['index'])[0]  # Bounding box coordinates  
        classes = model_interpreter.get_tensor(output[1]['index'])[0]  # Class index of the objects 
        conf_value = model_interpreter.get_tensor(output[2]['index'])[0]  # Confidence of detected objects 
        
        for i in range(len(conf_value)):  # Comparing with the minimum threshold 
            if (conf_value[i] > minimum_confidence) and (conf_value[i] <= 1.0): 
                # Get bounding box coordinates and draw box 
                ymin = int(max(1, (box[i][0] * imH))) 
                xmin = int(max(1, (box[i][1] * imW))) 
                ymax = int(min(imH, (box[i][2] * imH))) 
                xmax = int(min(imW, (box[i][3] * imW))) 
                
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2) 
                
                # Draw label around the box 
                object_name = labels[int(classes[i])]  
                label = '%s: %d%%' % (object_name, int(conf_value[i] * 100))  
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)  # Get font size 
                label_ymin = max(ymin, labelSize[1] + 10)  
                
                cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10), 
                              (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)  
                cv2.putText(frame, label, (xmin, label_ymin - 7), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)  
        
        cv2.imshow('Object Detection in Stingray', frame) 

        # Press 'q' to quit 
        if cv2.waitKey(1) == ord('q'): 
            print("\n Exiting the frame") 
            break 

    cv2.destroyAllWindows() 
    Video_PiCamera.stop() 

# Creating a thread for object detection 
objectDetectionThread = threading.Thread(target=detection, args=('any1', 'any2'))  
objectDetectionThread.start()
