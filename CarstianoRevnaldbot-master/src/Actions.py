import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3

from Debug import *
from Calculations import *
from util.Matrix import *


# TODO calculate turning radius and turning radius needed, if you can't make the turn then brake
# Path Prediction

def get_ball_predicted_pos(self, sliceNum) -> Vec3:
    ball_prediction = self.get_ball_prediction_struct()
    return Vec3(ball_prediction.slices[sliceNum].physics.location)

   
# General Driving
def drive_for_kickoff(self, my_car, car_to_desired_location) -> str:
    # Find the direction of our car using the Orientation class
    car_orientation = Orientation(my_car.physics.rotation)
    car_direction = car_orientation.forward
    car_yaw = my_car.physics.rotation.yaw
    steer_correction_radians = find_correction(car_direction, car_to_desired_location, car_yaw)

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

    car_location = Vec3(my_car.physics.location)
    if (car_location.dist(car_to_desired_location) < 900):
        jump(self)

    return action_display  

def drive_toward_ball(self, my_car, car_to_ball):
    drive_toward(self, my_car, car_to_ball)
    
def calculate_ball_to_goal(ball_location, goal)-> float:
    return ball_location.dist(goal.location)

def get_car_boost_level(my_car) -> float:
    return my_car.boost

def drive_toward_boost(self, my_car, car_to_boost):
    drive_toward(self, my_car, car_to_boost)

def drive_toward(self, my_car, car_to_desired_location) -> str:
    self.controller_state.boost = False
     # Find the direction of our car using the Orientation class
    car_orientation = Orientation(my_car.physics.rotation)
    car_direction = car_orientation.forward
    car_yaw = my_car.physics.rotation.yaw
    steer_correction_radians = find_correction(car_direction, car_to_desired_location, car_yaw)

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
    return action_display

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

def inside_turning_radius(my_car, car_to_desired_location) -> bool:

    rotation_matrix = Matrix3D(
    [
        my_car.physics.rotation.pitch,
        my_car.physics.rotation.yaw,
        my_car.physics.rotation.roll,
    ])
    local = rotation_matrix.dot(car_to_desired_location)
    local = Vec3(local)
    car_speed = my_car.physics.velocity
    car_speed = Vec3(car_speed).length()
    turn_radius = turning_radius(car_speed)
    return turn_radius > min((local - Vec3(0, -turn_radius, 0)).length(), (local - Vec3(0, turn_radius, 0)).length())

# Jumping (And eventually, hopefully, air movement)

def jump(self):
    self.controller_state.jump = True


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
def defend_goal(self, my_car, goal, ball) -> str:
    block_shot(self, my_car, goal, ball)
    car_location = Vec3(my_car.physics.location)
    goal_location = Vec3(goal.location)
    car_to_goal = goal_location - car_location

    ball_future_location = get_ball_predicted_pos(self, 30)
    car_to_ball = ball_future_location - my_car.physics.location
    action_display = "defending"
    # checks if car is at goal location
    car_speed = Vec3(my_car.physics.velocity).length()

    if car_to_goal.length() > 1000:  
        drive_toward(self, my_car, car_to_goal)
        action_display = "driving to goal"
    elif car_to_goal.length() < 1000 and car_speed > 600:
        brake_and_orient(self, my_car, goal, ball)
        block_shot(self, my_car, goal, ball)
        action_display = "blocking shot"
        # Car is at goal
    else:
        drive_toward(self, my_car, car_to_ball)

    return action_display


def block_shot(self, my_car, goal, ball):
   
    # Calculate car reorientation
    car_orientation = Orientation(my_car.physics.rotation)
    car_direction = car_orientation.forward
    goal_direction = Vec3(goal.direction)

    angle_to_goal = car_direction.ang_to(goal_direction)
    
    
    ball_future_location = get_ball_predicted_pos(self, 30)
    my_car_location = Vec3(my_car.physics.location)
    car_to_ball = my_car_location.dist(ball_future_location)

    if angle_to_goal < math.pi/2 and angle_to_goal > 0:
        print("< pi/2 and > 0 jumpin left")
        self.controller_state.jump = True
        self.controller_state.steer = -1
    elif angle_to_goal > math.pi/2 and angle_to_goal < math.pi:
        print("< pi and > pi/2 jumpin right")
        self.controller_state.jump = True
        self.controller_state.steer = 1
    else:
        self.controller_state.jump = False
    if car_to_ball < 100:
        print("less than 100")
        self.controller_state.jump = True
    else:
        self.controller_state.jump = False
    #if car forward vector is parallel to goal, fine
    #if car forward vector is > pi/2 & < pi go to pi (believe this means we are left of goal)
    #if car forward vector is < pi/2 & > 0 go to 0 (believe this means we are right of goal)
    


# Offense
