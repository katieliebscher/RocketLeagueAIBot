import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3

from Debug import *
from Calculations import *
from util.Matrix import *

def draw_debug(renderer, car, ball, action_display):
    renderer.begin_rendering()
    # draw a line from the car to the ball
    renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()

def draw_debug_message(renderer, car, action_display):
    renderer.begin_rendering()
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()

def draw_block_debug(renderer, my_car, goal, ball):
    # Calculate car reorientation
    car_orientation = Orientation(my_car.physics.rotation)
    car_direction = car_orientation.forward
    goal_direction = Vec3(goal.direction)

    angle = car_direction.ang_to(goal_direction)
    
    #if car forward vector is parallel to goal, fine
    #if car forward vector is > pi/2 & < pi go to pi (believe this means we are left of goal)
    #if car forward vector is < pi/2 & > 0 go to 0 (believe this means we are right of goal)
    action_display = str(angle)
    renderer.begin_rendering()
    # draw a line from the car to the ball
    renderer.draw_line_3d(my_car.physics.location, goal.direction, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(my_car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()