import numpy as np
import math
class angle:
    def __init__(self):
        self.midpoint_self = np.zeros((3))
        self.midpoint_right = np.zeros((3))
        self.y = 60
        self.x = 0
        self.a = 90
        self.p = 0
        self.turn_left = 0
        self.turn_right = 0
    
    def range_angle(self, data, predict):
        self.midpoint_left = data[0:3][data[0:3]!=0]
        self.midpoint_right = data[10:13][data[10:13]!=0]
        x = (self.midpoint_left+self.midpoint_right)//2
        self.x = np.mean(x)
        if self.x < 320:
            self.x = 320-self.x
        else:
            self.x = self.x-320
        self.a = math.degrees(math.atan(self.x/self.y))
        if predict == 1:
            if np.mean(x) < 320:
                self.a = 90+self.a
            else:
                self.a = 90-self.a
        elif predict == 2:
            self.a = 95-self.a
        elif predict == 3:
            self.a = 85+self.a
        elif predict == 4:
            self.turn_right = 1
            self.a = 95-self.a
        elif predict == 5:
            self.turn_left = 1
            self.a = 85+self.a
        
        if self.a > 130:
            self.a = 130
        elif self.a < 50:
            self.a = 50
        return self.a
    
    def calculate_angle(self, data, predict):
        if self.turn_left != 0:
            if predict == 3 or predict == 5:
                self.range_angle(data, predict)
                self.turn_left = 0
            else:
                return self.a
        elif self.turn_right != 0:
            if predict == 2 or predict == 4:
                self.range_angle(data, predict)
                self.turn_right = 0
            else:
                return self.a
        else:
            self.range_angle(data, predict)
            
        return self.a
