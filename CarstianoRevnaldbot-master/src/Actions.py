import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3

from Debug import *
from Calculations import *
from util.Matrix import *
from util import *


# TODO calculate turning radius and turning radius needed, if you can't make the turn then brake
# Path Prediction

def get_ball_predicted_pos(self, sliceNum) -> Vec3:
    ball_prediction = self.get_ball_prediction_struct()
    return Vec3(ball_prediction.slices[sliceNum].physics.location)


# General Driving
def drive_for_kickoff(self, target) -> str:
    # Find the direction of our car using the Orientation class
    car_orientation = Orientation(self.bot_rot)
    car_direction = car_orientation.forward
    car_yaw = car_orientation.yaw
    steer_correction_radians = find_correction(car_direction, target, car_yaw)

    if steer_correction_radians < math.radians(-10):
        # If the target is more than 10 degrees right from the centre, steer left
        turn = -1
        action_display = "turn left"
    elif steer_correction_radians > math.radians(10):
        # If the target is more than 10 degrees left from the centre, steer right
        turn = 1
        action_display = "turn right"
    else:
        # If the target is less than 10 degrees from the centre, steer straight
        turn = 0
        action_display = "drive straight"

    self.controller_state.throttle = 1.0
    self.controller_state.steer = turn
    self.controller_state.boost = True

    car_location = self.bot_loc
    if (car_location.dist(target) < 900):
        jump(self)

    return action_display
    
def calculate_ball_to_goal(ball_location, goal)-> float:
    return ball_location.dist(goal.location)

def get_car_boost_level(self) -> float:
    return self.bot_boost


def drive_toward(self, target):

     # Find the direction of our car using the Orientation class
    car_orientation = Orientation(self.bot_rot)
    car_direction = car_orientation.forward
    car_yaw = car_orientation.yaw
    steer_correction_radians = find_correction(car_direction, target, car_yaw)

    if inside_turning_radius(self, target):
        self.renderer.begin_rendering()
        self.controller_state.throttle = 0.0
        self.controller_state.hand_brake = True
    else:
        self.controller_state.throttle = 1.0
        self.controller_state.hand_brake = False
        
    if steer_correction_radians < math.radians(-10):
        # If the target is more than 10 degrees right from the centre, steer left
        turn = -1
    elif steer_correction_radians > math.radians(10):
        # If the target is more than 10 degrees left from the centre, steer right
        turn = 1
    else:
        # If the target is less than 10 degrees from the centre, steer straight
        turn = 0

    
    #self.controller_state.throttle = 1.0
    self.controller_state.steer = turn

def find_correction(current: Vec3, ideal: Vec3, yaw) -> float:
    # Finds the angle from current to ideal vector in the xy-plane. Angle will be between -pi and +pi.
    angle_between_bot_and_target = math.atan2(ideal.y - current.y, ideal.x - current.x)
    diff = angle_between_bot_and_target - yaw
    # Make sure that diff is between -pi and +pi.
    if abs(diff) > math.pi:
        if diff < 0:
            diff += 2 * math.pi
        else:
            diff -= 2 * math.pi

    return diff

def turning_radius(car_speed) -> float:  # Thx Dom
    radius = 156 + 0.1 * car_speed + 0.000069 * car_speed ** 2 + 0.000000164 * car_speed ** 3 - 5.62e-11 * car_speed ** 4
    return radius

def inside_turning_radius(self, target) -> bool:

    rotation_matrix = Matrix3D(
    [
        self.bot_rot_pitch,
        self.bot_rot_yaw,
        self.bot_rot_roll,
    ])
    local = rotation_matrix.dot(target)
    local = Vec3(local)
    car_speed = Vec3(self.bot_speed)
    car_speed = car_speed.length()
    turn_radius = turning_radius(car_speed)
    return turn_radius > min((local - Vec3(0, -turn_radius, 0)).length(), (local - Vec3(0, turn_radius, 0)).length())

# Jumping (And eventually, hopefully, air movement)

def jump(self, pitch=-1, roll=.05, jump_timeout=0.1, flick_timeout=0.15):
    if self.flick_time == 0 and self.bot_ground:
        self.controller_state.jump = True
        self.jump_time_end = self.game_time + jump_timeout
        self.flick_time = self.game_time + flick_timeout
        if pitch > 1:
            pitch = 1
        elif pitch < -1:
            pitch = -1
        self.controller_state.pitch = pitch
        roll = roll * 1.3
        if roll > 1:
            roll = 1
        elif roll < -1:
            roll = -1
        self.controller_state.roll = roll


# Braking
def brake_by(self, my_car, location):
     # Make car break
    self.controller_state.boost = False
    self.controller_state.hand_brake = True
    self.controller_state.throttle = 0

def brake_and_orient(self, my_car, goal, ball):
    
    # Make car break
    self.controller_state.boost = False
    self.controller_state.hand_brake = True
    self.controller_state.throttle = 0.0

    # Calculate car reorientation
    car_orientation = Orientation(my_car.physics.rotation)
    car_direction = car_orientation.forward
    car_yaw = my_car.physics.rotation.yaw
    ball_future_location = get_ball_predicted_pos(self, 30)
    car_to_ball = ball_future_location - my_car.physics.location
    steer_correction_radians = find_correction(car_direction, car_to_ball, car_yaw)

    if my_car.physics.velocity.x <= 30.0 and my_car.physics.velocity.y <= 30.0:
        if steer_correction_radians < math.radians(-10):
            # If the target is more than 10 degrees right from the centre, steer left
            turn = -1
        elif steer_correction_radians > math.radians(10):
            # If the target is more than 10 degrees left from the centre, steer right
            turn = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            turn = 0

        self.controller_state.hand_brake = False
        self.controller_state.throttle = 1.0
        self.controller_state.steer = turn
    
# Defense
def play_defense(self) -> Vec3:
     # Information needed
    self.renderer.begin_rendering()
    
    # Information needed
    # 1.) The predicted ball path
    ball_prediction = self.get_ball_prediction_struct()
    if ball_prediction is not None:
        prediction_slices = ball_prediction.slices[0:120]
        locations = []
        for i in range(0, len(prediction_slices)):
            locations.append(prediction_slices[i].physics.location)
        self.renderer.draw_polyline_3d(locations, self.renderer.red())
    
    center = Vec3(0, 5150 * sign(self.team), 200)

    timeIndex = determineTarget(self)
    target = Vec3(locations[timeIndex])
    goal = target - self.bot_loc

    self.renderer.draw_line_3d(self.ball_loc, center, self.renderer.green())
    self.renderer.draw_line_3d(self.bot_loc,  target, self.renderer.black())

    future_list = []
    for i in range(0, 120):
        tempTarget = Vec3(locations[i])
        temppt1 = findAngle(tempTarget, center)
        future_list.append(temppt1)

    total_dif = 0
    for i in range(1, 120):
        prevVal = future_list[i - 1]
        curVal = future_list[i]
        if prevVal > curVal:
            total_dif += 1
        else:
            total_dif -= 1

    ballY = self.ball_loc.y
    carY = self.bot_loc.y

    ballX = self.ball_loc.x
    carX = self.bot_loc.x
    if (abs(ballY - carY) < 40):
        if (ballX > carX + 10): #Ball is further right than the car, steer right
            self.controller_state.steer = 1
            jump(self, roll=-1)
    
        elif (ballX - 10 < carX):
            #if (ballX - 20 > carX): # Ball is close enough to jump at it
            self.controller_state.steer = -1
            jump(self, roll=1)
    elif(abs(ballX-carX) < 40):
        if (ballY > carY + 10): #Ball is further right than the car, steer right
            self.controller_state.steer = 1
            jump(self, roll=1)
    
        elif (ballY - 10 < carY):
            self.controller_state.steer = -1
            jump(self, roll=-1)
    else: #Drive to goal and defend there 
        info = self.get_field_info()
        goal = info.goals[self.bot_team]
        car_location = Vec3(self.bot_loc)
        goal_location = Vec3(goal.location)
        car_to_goal = goal_location - car_location

        ball_future_location = get_ball_predicted_pos(self, 30)
        car_to_ball = ball_future_location - self.bot_loc
        action_display = "defending"
        # checks if car is at goal location
        car_speed = Vec3(self.bot_loc).length()
        
        if car_to_goal.length() > 2000: #If car is very far from goal, boost and go to goal
          #  self.renderer.draw_string_3d(self.bot_loc,  2, 2, "sprinting to goal" , self.renderer.white())
            self.controller_state.boost = True
            drive_toward(self, car_to_goal)

        elif car_to_goal.length() > 500:  #Car is close to goal, no need to boost
           # self.renderer.draw_string_3d(self.bot_loc,  2, 2, "driving to goal", self.renderer.white())
            self.controller_state.boost = False
            drive_toward(self, car_to_goal) 

        elif (self.bot_loc_x < goal.location.x): #Don't go in goal
            self.controller_state.boost = False
            self.controller_state.throttle = -1.0
            self.controller_state.hand_brake = False
         #   self.renderer.draw_string_3d(self.bot_loc,  2, 2, "In goal backing up", self.renderer.white())    
        
        else: #track ball 
         #   self.renderer.draw_string_3d(self.bot_loc,  2, 2, "tracking ball", self.renderer.white())
            self.controller_state.boost = False
            drive_toward(self, ball_future_location)

    self.renderer.end_rendering()
    return goal
    


def defend_goal(self) -> str:
    self.renderer.begin_rendering()
    info = self.get_field_info()
    goal = info.goals[self.bot_team]
    car_location = Vec3(self.bot_loc)
    goal_location = Vec3(goal.location)
    car_to_goal = goal_location - car_location

    ball_future_location = get_ball_predicted_pos(self, 30)
    car_to_ball = ball_future_location - self.bot_loc
    action_display = "defending"
    # checks if car is at goal location
    car_speed = Vec3(self.bot_loc).length()

    if car_to_goal.length() > 2000:
        self.renderer.draw_string_3d(self.bot_loc,  2, 2,str(car_to_goal.length()) , self.renderer.white())
        self.controller_state.boost = True
        drive_toward(self, car_to_goal)
    elif car_to_goal.length() > 500:  
        self.renderer.draw_string_3d(self.bot_loc,  2, 2, "driving to goal", self.renderer.white())
        self.controller_state.boost = False
        drive_toward(self, car_to_goal)
    elif (self.bot_loc_x < goal.location.x): #Don't go in goal
        self.controller_state.boost = False
        self.controller_state.throttle = -1.0
        self.controller_state.hand_brake = False
        self.renderer.draw_string_3d(self.bot_loc,  2, 2, "In goal backing up", self.renderer.white())     
    else:
        self.renderer.draw_string_3d(self.bot_loc,  2, 2, "tracking ball", self.renderer.white())
        self.controller_state.boost = False
        drive_toward(self, ball_future_location)

    self.renderer.end_rendering()
    return action_display

# Offense
def play_offense(self) -> Vec3:
    # Information needed
    self.renderer.begin_rendering()

    # Information needed
    # 1.) The predicted ball path
    ball_prediction = self.get_ball_prediction_struct()
    if ball_prediction is not None:
        prediction_slices = ball_prediction.slices[0:120]
        locations = []
        for i in range(0, len(prediction_slices)):
            locations.append(prediction_slices[i].physics.location)
        self.renderer.draw_polyline_3d(locations, self.renderer.red())

    center = Vec3(0, 5150 * -sign(self.team), 200)

    timeIndex = determineTarget(self)
    target = Vec3(locations[timeIndex])
    goal = target - self.bot_loc

    self.renderer.draw_line_3d(self.ball_loc, center, self.renderer.green())
    self.renderer.draw_line_3d(self.bot_loc,  target, self.renderer.black())

    future_list = []
    for i in range(0, 120):
        tempTarget = Vec3(locations[i])
        temppt1 = findAngle(tempTarget, center)
        future_list.append(temppt1)

    total_dif = 0
    for i in range(1, 120):
        prevVal = future_list[i - 1]
        curVal = future_list[i]
        if prevVal > curVal:
            total_dif += 1
        else:
            total_dif -= 1

    ballY = self.ball_loc.y
    carY = self.bot_loc.y
    behind = False
    if abs(center.y - ballY) < abs(center.y - carY):  # Car is behind the ball
        behind = True

    if total_dif > 70: # The future location and ball are generally moving in the same direction
        car_location = self.bot_loc
        ballX = self.ball_loc.x
        carX = self.bot_loc.x

        if (ballX > carX + 10): #Ball is further right than the car, steer right
            self.controller_state.steer = 1
        elif(ballX - 10 < carX):
            self.controller_state.steer = -1

        if car_location.dist(target) < 400 and self.ball_loc.z <= 120 and future_list[timeIndex < 5] and behind == True:
            #Ball is to the left
            jump(self)

    #print(Vec3(locations[119]).dist(center))
    if behind == True or Vec3(locations[119]).dist(center) <= 2400:
        drive_toward(self, goal)
    else:
        target = Vec3(locations[60])
        goal = target - self.bot_loc
        self.renderer.draw_line_3d(self.bot_loc, target, self.renderer.white())
        drive_toward(self, goal)


    self.renderer.end_rendering()
    return goal

def sign(x):
    if x <= 0:
        return -1
    else:
        return 1

def determineTarget(self) -> int:
    oldValue = Vec3.dist(self.ball_loc, self.bot_loc) #Scales between 0 and 120 seconds
    oldMin = 200
    oldMax = 8000
    newMax = 120
    newMin = 0
    oldRange = oldMax - oldMin
    newRange = newMax - newMin
    target = int((((oldValue - oldMin) * newRange) // oldRange) + newMin)
    return(target)

def relative_location(center: Vec3, ori: Orientation, target: Vec3) -> Vec3:
    """
    Returns target as a relative location from center's point of view, using the given orientation. The components of
    the returned vector describes:

    * x: how far in front
    * y: how far right
    * z: how far above
    """
    x = (target - center).dot(ori.forward)
    y = (target - center).dot(ori.right)
    z = (target - center).dot(ori.up)
    return Vec3(x, y, z)

def findAngle(vec1: Vec3, vec2: Vec3) -> float:
    x1 = vec1.x
    y1 = vec1.y
    x2 = vec2.x
    y2 = vec2.y
    top_section = (x1 * x2) + (y1 * y2)
    bottom_section = math.sqrt(x1**2 + y1**2) * math.sqrt(x2**2 + y2**2)
    if bottom_section == 0:
        return 0
    return math.acos(top_section/bottom_section)