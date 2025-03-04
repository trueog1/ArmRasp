#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
from perception_class import Perception

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
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(self.sleep_time)

    def moving_arm(self):
        while True:
            if self.perception.current_colour != "None":
                current_color = self.perception.current_colour
                self.set_rgb(current_color)

                world_X, world_Y, rotation_angle = self.perception.last_x, self.perception.last_y, self.perception.rotation_angle
                result = self.AK.setPitchRangeMoving((world_X, world_Y, self.desired_approach_height_grasp), -90, -90, 0)  

                if result:
                    time.sleep(result[2]/1000)

                    servo2_angle = getAngle(world_X, world_Y, rotation_angle) #计算夹持器需要旋转的角度
                    Board.setBusServoPulse(1, self.servo1 - 280, 500)  # 爪子张开
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.5)

                    AK.setPitchRangeMoving((world_X, world_Y, 1.5), -90, -90, 0, 1000)
                    time.sleep(1.5)

                    Board.setBusServoPulse(1, self.servo1, 500)  #夹持器闭合
                    time.sleep(0.8)

                    Board.setBusServoPulse(2, 500, 500)
                    AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 1000)  #机械臂抬起
                    time.sleep(1)

                    result = AK.setPitchRangeMoving((self.coordinate[current_color][0], self.coordinate[current_color][1], 12), -90, -90, 0)   
                    time.sleep(result[2]/1000)

                    servo2_angle = getAngle(self.coordinate[current_color][0], self.coordinate[current_color][1], -90)
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.5)

                    AK.setPitchRangeMoving((self.coordinate[current_color][0], self.coordinate[current_color][1], self.coordinate[current_color][2] + 3), -90, -90, 0, 500)
                    time.sleep(0.5)

                    AK.setPitchRangeMoving((self.coordinate[current_color]), -90, -90, 0, 1000)
                    time.sleep(0.8)

                    Board.setBusServoPulse(1, self.servo1 - 200, 500)  # 爪子张开  ，放下物体
                    time.sleep(0.8)

                    AK.setPitchRangeMoving((self.coordinate[current_color][0], self.coordinate[current_color][1], 12), -90, -90, 0, 800)
                    time.sleep(0.8)

                    self.initMove()  # 回到初始位置
                    time.sleep(1.5)

                    current_color = 'None'
                    self.set_rgb(current_color)

if __name__ == "__main__":
    perception = Perception()
    motion = Move(perception)

    t1 = threading.Thread(target=perception.finding_objects)
    t2 = threading.Thread(target=motion.moving_arm)

    t1.start()
    t2.start()

