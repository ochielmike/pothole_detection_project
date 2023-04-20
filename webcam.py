import tensorflow as tf
import numpy as np
import cv2
import datetime
import os
import sqlite3
import RPi.GPIO as GPIO
import serial
import time
from gps_module import SIM7600X as gps
sim = gps('/dev/ttyS0', 115200, 6)
sim.power_on()


def calculate_area(x1, y1, x2, y2):
    return (x2 - x1) * (y2 - y1)
# Sum up the areas of all bounding boxes in the image.
def sum_areas(output_data):
    total_area = 0
    for detection in output_data:
        _,x1, y1, x2, y2, _, _ = detection
        total_area += calculate_area(x1, y1, x2, y2)
    return total_area


def save_to_database(total_area, file_name):
    # Connect to the database.
    connection = sqlite3.connect("bounding_box_areas.db")
    cursor = connection.cursor()
    # Insert a row with the file name and total area.
    cursor.execute(
        "INSERT INTO bounding_box_areas (file_name, total_area,lat_out, long_out, date_d, time_t) VALUES (?,?,?,?,?,?)",
        (file_name, total_area,lat_out,long_out,date_d,time_t)
    )
    connection.commit()
    connection.close()
class ObjectDetection:
    def __init__(self, model_path, output_folder):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_tensor_index = self.interpreter.get_input_details()[0]["index"]
        self.output_tensor_index = self.interpreter.get_output_details()[0]["index"]
        self.output_folder = output_folder
        self.webcam = cv2.VideoCapture(0)
        self.file_name_format = "object_detection_{:%Y%m%d_%H%M%S}.jpg"
    


    def run(self):
        
        while True:
            ret, frame = self.webcam.read()
            if not ret:
                break

            frame = cv2.resize(frame, (416, 416))
            input_data = np.array(frame, dtype=np.float32) / 255.0
            input_data = np.expand_dims(input_data, axis=0)
            input_data = np.transpose(input_data,(0,3,1,2))

            self.interpreter.set_tensor(self.input_tensor_index, input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_tensor_index)
            total_area = sum_areas(output_data)

            num_detections = output_data.shape[0]
            lat_out,long_out,date_d,time_t = sim.get_gps_position()
            for i in range(num_detections):
                first, x1, y1, x2, y2, class_id, confidence = output_data[i]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"{class_id}: {confidence:.2f}", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            file_name = self.file_name_format.format(datetime.datetime.now())
            save_to_database(total_area, file_name,lat_out,long_out,date_d, time_t)
            file_path = os.path.join(self.output_folder, file_name)
            cv2.imwrite(file_path, frame)
            if cv2.waitKey(1) == ord("q"):
                break

        self.webcam.release()
        cv2.destroyAllWindows()

detector = ObjectDetection("yolov7_model.tflite", "object_detection_frames")
detector.run()
