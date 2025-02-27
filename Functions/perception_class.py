#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import Camera
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
from CameraCalibration.CalibrationConfig import *

class Perception():
    def __init__(self):
        self.color_range = {
            'red':   (0, 0, 255),
            'blue':  (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),}
        self.target_color = ('red', 'green', 'blue')
        self.camera = Camera.Camera()
        self.camera.camera_open()
        self.size = (640, 480)
        self.get_roi = False
        self.best_contour = None
        self.best_contour_area = 0
        self.color_of_interest = None
        self.minimum_contour_thresh = 2500
        self.blur_kernal = (11, 11)
        self.filter_kernal = (6, 6)
        self.std_kernal = 11
        self.roi = ()
        self.last_x = 0
        self.last_y = 0
        self.color_to_number = {"red" : 1, "green" : 2, "blue" : 3}
        self.number_to_color = {1 : "red", 2 : "green", 3 : "blue"}
        self.color_list = []
        self.center_locations = []
        self.movement_change_thresh = 0.5
        self.previous_time = time.time()
        self.time_thresh = 1.0
        self.current_colour = "None"
        self.draw_colour = self.color_range['black']
        self.rotation_angle = 0


    def finding_objects(self):
        #self.camera.camera_open()
        while True:
            img = self.camera.frame
            if img is not None:
                frame = img.copy()
                Frame = self.processing_image(frame)           
                cv2.imshow('Frame', Frame)
                key = cv2.waitKey(1)
                if key == 27:
                    break

        self.camera.camera_close()
        cv2.destroyAllWindows()

    def processing_image(self, img):

        img_h, img_w = img.shape[:2]

        #draw on calibration +
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        #resize image to area of interest
        frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)

        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)

        self.area_of_interest_processing(frame_lab)

        if self.best_contour_area > self.minimum_contour_thresh:
            rect = cv2.minAreaRect(self.best_contour)
            box = np.int0(cv2.boxPoints(rect))
            
            self.roi = getROI(box)
            img_x, img_y = getCenter(rect, self.roi, self.size, square_length)
            world_x, world_y = convertCoordinate(img_x, img_y, self.size)

            cv2.drawContours(img, [box], -1, self.color_range[self.color_of_interest], 2)
            cv2.putText(img, f'({world_x}, {world_y})', (min(box[0, 0], box[2, 0]), box[2, 1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                        self.color_range[self.color_of_interest], 1) 

            distance = math.sqrt((world_x - self.last_x)**2 + (world_y - self.last_y)**2)
            self.last_x, self.last_y = world_x, world_y

            if self.color_of_interest in self.color_to_number:
                color_location = self.color_to_number[self.color_of_interest]

            else:
                color_location = 0
            
            self.color_list.append(color_location)

            if distance < self.movement_change_thresh:
                self.center_locations.extend((world_x, world_y))
                self.timing(rect)

            else:
                self.previous_time = time.time()
                self.center_locations = []

            if len(self.color_list) == 3:
                number = int(round(np.mean(np.array(self.color_list))))
            
                if number in self.number_to_color:
                    self.current_colour = self.number_to_color[number]
                    self.draw_colour = self.color_range[self.current_colour]

                else:
                    self.current_colour = 'None'
                    self.draw_colour = self.color_range['black']
                    
                
                self.color_list = []

        else:
            self.draw_colour = (0, 0, 0)
            self.current_colour = "None"

        cv2.putText(img, f'Colour: {self.current_colour}', (10, img_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.draw_colour, 2)
        return img


    def area_of_interest_processing(self, frame_lab):
        self.color_area_max = None
        self.max_area = 0
        self.areaMaxContour_max = 0

        for color in color_range:
            if color in self.target_color:
                frame_mask = cv2.inRange(frame_lab, color_range[color][0], color_range[color][1])  
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))  
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8)) 
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  

                if not contours:
                    continue
                
                largest_contour = max(contours, key=cv2.contourArea)
                largest_contour_area = cv2.contourArea(largest_contour)

                if largest_contour_area > self.best_contour_area:
                    self.best_contour_area = largest_contour_area
                    self.best_contour = largest_contour
                    self.color_of_interest = color

    def timing(self, rect):
        if time.time() - self.previous_time > self.time_thresh:
            self.rotation_angle = rect[2]
            self.center_locations = []
            self.previous_time = time.time()

if __name__ == "__main__":
    perp = Perception()

    perp.finding_objects()
        
                