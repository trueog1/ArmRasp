#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import Camera
import time
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

class Perception():
    def __init__(self):
        self.color_range = {
            'red':   (0, 0, 255),
            'blue':  (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            }
        
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
        self.color_area = {"red": 0, "blue": 0, "green": 0}
        self.center_locations = {"red": (0,0), "blue": (0,0), "green": (0,0)}
        self.best_contour_d = {"red": 0, "blue": 0, "green": 0}
        self.movement_change_thresh = 0.5
        self.previous_time = time.time()
        self.time_thresh = 1.0
        self.current_colour = "None"
        self.draw_colour = self.color_range['black']
        self.rotation_angle = {"red": 0, "green": 0, "blue": 0}


    def finding_objects(self):
        #self.camera.camera_open()
        while True:
            img = self.camera.frame
            if img is not None:
                frame = img.copy()
                Frame = self.processing_image(frame)           
                cv2.imshow('Frame', Frame)
                #bgr_value = int(img, [300, 300])
                #print(bgr_value)
                key = cv2.waitKey(1)
                if key == 27:
                    break

        self.camera.camera_close()
        cv2.destroyAllWindows()

    def processing_image(self, img):

        #img = img.copy()

        img_h, img_w = img.shape[:2]

        #draw on calibration +
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        #resize image to area of interest
        frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)

        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)

        self.area_of_interest_processing(frame_lab)

        for color in self.target_color:
            if self.color_area[color] > self.minimum_contour_thresh:
                rect = cv2.minAreaRect(self.best_contour_d[color])
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
                #print(f'coords')

                self.center_locations[color] = (world_x, world_y)
                self.timing(rect, color)
                #print(f'updating')

                '''if self.color_of_interest in self.color_to_number:
                    color_location = self.color_to_number[self.color_of_interest]

                else:
                    color_location = 0
                
                self.color_list.append(color_location)'''

                '''if distance < self.movement_change_thresh:
                    print(f'updating')
                    self.center_locations[color] = (world_x, world_y)
                    self.timing(rect, color)

                else:
                    self.previous_time = time.time()
                    #self.center_locations = {}'''

                '''if len(self.color_list) == 6:
                    number = int(round(np.mean(np.array(self.color_list))))
                
                    if number in self.number_to_color:
                        self.current_colour = self.number_to_color[number]
                        self.draw_colour = self.color_range[self.current_colour]

                    else:
                        self.current_colour = 'None'
                        self.draw_colour = self.color_range['black']
                        
                    
                    self.color_list = []'''

            else:
                self.draw_colour = (0, 0, 0)
                self.current_colour = "None"

        self.center_locations["yellow"] = (self.center_locations["green"][0] + 1, self.center_locations["green"][1])
        print(self.rotation_angle)
        _, chorous_color, _, chorous_time = self.get_music()
        cv2.putText(img, f'Colour: {self.current_colour}', (10, img_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.draw_colour, 2)
        return img


    def area_of_interest_processing(self, frame_lab):
        self.best_contour = None
        self.best_contour_area = 0
        self.color_of_interest = None

        for color in color_range:
            if color in self.target_color:
                color_mask = cv2.inRange(frame_lab, color_range[color][0], color_range[color][1]) # Find all values within given color range we want to analyze
                cleaned_image = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, np.ones(self.filter_kernal, np.uint8))
                cleaned_image = cv2.morphologyEx(cleaned_image, cv2.MORPH_CLOSE, np.ones(self.filter_kernal, np.uint8))
                contours = cv2.findContours(cleaned_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2] # Only give us the contours, don't care about the image or hierarchy

                try:
                    largest_contour = max(contours, key=cv2.contourArea)
                    largest_contour_area = cv2.contourArea(largest_contour)
                    self.color_area[color] = largest_contour_area
                    self.best_contour_d[color] = largest_contour

                    if largest_contour_area > self.best_contour_area:
                        self.best_contour_area = largest_contour_area
                        self.best_contour = largest_contour
                        self.color_of_interest = color
                        self.color_area[color] = self.best_contour_area
                        self.best_contour_d[color] = self.best_contour
                except:
                    continue

    def timing(self, rect, color):
        if time.time() - self.previous_time > self.time_thresh:
            self.rotation_angle[color] = rect[2]
            #self.center_locations = []
            self.previous_time = time.time()

    # Notes from sheet music
    def get_music(self):
        pre_chorous= 'd c d d d d d d c d e d d d d d e d d d d a g f e f e f e f f f d e e e e d g f '
        chorous = 'f f d d d g f d d e e d f d e d e f e d e e d f d e d e d f e d e d f e d d e f e f e f e f f e d'
        pre_chorous_notes= pre_chorous.split(' ')
        chorous_notes = chorous.split(' ')
        c_colors = []
        pc_colors = []

        #types of notes from sheet music
        pre_chorous_type = [8, 8 ,8, 8, 8, 4, 8, 8, 8, 4, 4, 8, 8, 8, 8, 8, 4, 8, 8, 8, 8, 8, 8, 8, 4, 8, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 8, 4, 4, 4, 2 ]
        chorous_type = [8, 4, 8, 8, 8, 4, 4, 4, 8, 8, 8, 8, 8, 8, 4, 4, 4, 4, 4, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 4, 4, 4, 8, 8, 4, 4, 8, 8, 4, 8, 8, 8, 8, 8, 8, 4, 8, 8, 4]
        play_time_pc= []
        play_time_c = []
        self.bpm_to_time (pre_chorous_type,play_time_pc)
        self.bpm_to_time(chorous_type,play_time_c)
        self.notes_to_color(pre_chorous_notes,pc_colors)
        self.notes_to_color(chorous_notes,c_colors)

        return pc_colors, c_colors, play_time_pc, play_time_c
    
    #equate note type to time
    def bpm_to_time (self, music,array):
        for i in music:
            if i == 8:
                t = .25
            elif i == 4: 
                t = .5
            elif i == 2:
                t = 1
            elif i == 3:
                t = 1.5
            array.append(t)

    def notes_to_color (self,music,array):
        for i in music:
            if i == 'd':
                color = 'green'
            elif i == 'e':
                color = 'yellow'
            elif i == 'f':
                color = 'blue'
            elif i == 'g':
                color = 'red'
            array.append(color)

class Move():
    def __init__(self, perception):
        self.coordinate = {
        'red':   (-15 + 0.5, 12 - 0.5, 1.5),
        'green': (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        self.perception = perception
        self.currently_moving = False
        self.sleep_time = 0.5
        self.gripper_open = 280
        self.servo_1_id = 1
        self.servo_2_id = 2
        self.AK = ArmIK()
        self.desired_approach_height_grasp = 7
        self.desired_final_height_grasp = 1.0
        self.servo1 = 500
        self.new_target_color = ('red', 'green', 'blue', 'yellow')

    def set_rgb(self, color):
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()

    def initMove(self):
        Board.setBusServoPulse(1, 610 - 50, 300)
        #Board.setBusServoPulse(2, 500, 500)
        Board.setBusServoPulse(2, 100, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(self.sleep_time)

    def moving_arm(self):
        while True:
            print(self.perception.center_locations)
            if self.perception.center_locations["red"][0] != 0 and self.perception.center_locations["green"][0] != 0 and self.perception.center_locations["blue"][0] != 0:
                #current_color = self.perception.current_colour
                #self.set_rgb(current_color)
                print(f'success')
                #print(self.perception.center_locations)

                for color in self.new_target_color:
                    world_X, world_Y, rotation_angle = self.perception.center_locations[color][0], self.perception.center_locations[color][1], self.perception.rotation_angle[color]
                    #result = self.AK.setPitchRangeMoving((world_X, world_Y, self.desired_approach_height_grasp), -90, -90, 0)  

                    if world_X:
                        #time.sleep(result[2]/2000) #this was originally divide by 1000
                        time.sleep(0.1)

                        servo2_angle = getAngle(world_X, world_Y, rotation_angle) #计算夹持器需要旋转的角度 = Calculate the angle at which the gripper needs to be rotated
                        #Board.setBusServoPulse(1, self.servo1, 200)  #夹持器闭合 = gripper closed
                        print(self.servo1)
                        Board.setBusServoPulse(1, 560, 200)  #夹持器闭合 = gripper closed
                        #Board.setBusServoPulse(2, servo2_angle, 200)
                        time.sleep(0.1)

                        #self.AK.setPitchRangeMoving((world_X, world_Y, 1.5), -90, -90, 0, 500)  #was originally 1000, maybe =1, so now should be a quarter of that?
                        self.AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 500)
                        time.sleep(0.4)
                        
                        self.AK.setPitchRangeMoving((world_X, world_Y, 6), -90, -90, 0, 500)
                        time.sleep(0.4)

                        Board.setBusServoPulse(2, 100, 200)
                        #self.AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 500)
                        self.AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 500)  #机械臂抬起 = the robotic arm is raised
                        time.sleep(0.4)

                        #self.initMove()  # 回到初始位置 = return to initial position
                        #time.sleep(0.75)

                        current_color = 'None'
                        self.set_rgb(current_color)

if __name__ == "__main__":
    perception = Perception()
    motion = Move(perception)

    t1 = threading.Thread(target=perception.finding_objects)
    t2 = threading.Thread(target=motion.moving_arm)

    t1.start()
    t2.start()