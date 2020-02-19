import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3
#USAGE: ALWAYS PUT OUR BOT ON LEFT SIDE OF RLBOT GUI
#TODO Create check for future ball position and whether it's close to either goal
#TODO Create check for distance between ball and car if ball is near opponents goal, then find proper distance
#TODO Create methods to calculate where to drive to hit ball at proper angle for defense and offense
#TODO Create action for jumping and hitting the ball at proper angle
#TODO Method to check if the game is in the kickoff state


class MyBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        ball_location = Vec3(packet.game_ball.physics.location)
        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)
        car_to_ball = ball_location - car_location
        info = self.get_field_info()
        boost_location = Vec3(find_nearest_boost(info, car_location, packet))
        car_to_boost = boost_location - car_location

        # Determine which goal our bot is defending/attacking
        ourGoalIndex = my_car.team
        opponentGoalIndex = 0
        if ourGoalIndex == 0:
            opponentGoalIndex = 1
        else:
            opponentGoalIndex = 0
            
        # If Statments in order to implement behavior tree
        #if kickoff --> drive at ball
        kickOff = packet.game_info.is_kickoff_pause

        #GOAL 0 is defended by bots on right side of GUI (Bot's on left side score on goal 0)
        opponentGoalDist = calculate_ball_to_goal(ball_location, info.goals[opponentGoalIndex])

        #GOAL 1 is defended by bots on left side of GUI (Bot's on right side score on goal 1)
        ourGoalDist = calculate_ball_to_goal(ball_location, info.goals[ourGoalIndex])

        # Check if it is the kickoff
        if kickOff:
            drive_toward_ball(self, my_car, car_to_ball)

        # Check if ball is near our goal
        elif ourGoalDist < 4500:
            #Drive to defensive position
            defend_goal(self, my_car, info.goals[ourGoalIndex])

        # Check if ball is near opponent's goal
        elif opponentGoalDist < 150:
            #Drive to offensive position
            drive_toward_ball(self, my_car, car_to_ball)

        # Check if boost level is low
        elif get_car_boost_level(my_car) < 35:
            drive_toward_boost(self, my_car, car_to_boost)

        # Default    
        else:
            #TODO Figure out how to properly time boosts
            #Current boost activation is in defend_goal
            self.controller_state.boost = False
            drive_toward_ball(self, my_car, car_to_ball)

        return self.controller_state

def find_nearest_boost(info, car_location, packet) -> Vec3:
    closest_pad_index = 0
    closest_pad_distance = 100000
    for i in range(info.num_boosts):  # For loop to get location of all pads
        pad = info.boost_pads[i]
        # To get Vect3 coordinate of pad
        padLoc = pad.location
        new_value = car_location.dist(padLoc)
        if new_value < closest_pad_distance:
            if packet.game_boosts[i].is_active:
                closest_pad_distance = new_value
                closest_pad_index = i

    return info.boost_pads[closest_pad_index].location

def find_correction(current: Vec3, ideal: Vec3) -> float:
    # Finds the angle from current to ideal vector in the xy-plane. Angle will be between -pi and +pi.

    # The in-game axes are left handed, so use -x
    current_in_radians = math.atan2(current.y, -current.x)
    ideal_in_radians = math.atan2(ideal.y, -ideal.x)

    diff = ideal_in_radians - current_in_radians

    # Make sure that diff is between -pi and +pi.
    if abs(diff) > math.pi:
        if diff < 0:
            diff += 2 * math.pi
        else:
            diff -= 2 * math.pi

    return diff


def drive_toward_ball(self, my_car, car_to_ball):
    drive_toward(self, my_car, car_to_ball)
 
def calculate_ball_to_goal(ball_location, goal)-> float:
    return ball_location.dist(goal.location)

def get_car_boost_level(my_car) -> float:
    return my_car.boost

def drive_toward_boost(self, my_car, car_to_boost):
    drive_toward(self, my_car, car_to_boost)


def defend_goal(self, my_car, goal):
    car_location = Vec3(my_car.physics.location)
    goal_location = Vec3(goal.location)
    car_to_goal = goal_location - car_location

    # determine whether car needs to boost to get to goal
    if car_location.dist(goal_location) > 400:
            self.controller_state.boost = True  
        else:
            self.controller_state.boost = False

    # checks if car is at goal location
    if car_to_goal.length() > 600:  
#       draw_debug_message(self.renderer, my_car, action_display)
        drive_toward(self, my_car, car_to_goal)
    else:
        brake_and_orient(self, my_car, goal)

def drive_toward(self, my_car, car_to_desired_location):
     # Find the direction of our car using the Orientation class
    car_orientation = Orientation(my_car.physics.rotation)
    car_direction = car_orientation.forward

    steer_correction_radians = find_correction(car_direction, car_to_desired_location)

    if steer_correction_radians > 0:
        # Positive radians in the unit circle is a turn to the left.
        turn = -1.0  # Negative value for a turn to the left.
        action_display = "turn left"
    else:
        turn = 1.0
        action_display = "turn right"

    self.controller_state.throttle = 1.0
    self.controller_state.steer = turn

def brake_and_orient(self, my_car, goal):
    
    # Make car break
    self.controller_state.boost = False
    self.controller_state.hand_brake = True
    self.controller_state.throttle = 0
    action_display = "braking"

    # Calculate car reorientation
    car_orientation = Orientation(my_car.physics.rotation)
    car_direction = car_orientation.forward
    goal_direction = Vec3(goal.direction)
    steer_correction_radians = car_direction.ang_to(goal_direction)

    # Once car is stopped, reorient
    if my_car.physics.velocity.x <= 0 and my_car.physics.velocity.y <= 0:
        if steer_correction_radians > 0:
            # Positive radians in the unit circle is a turn to the left.
            turn = -1.0  # Negative value for a turn to the left.
            action_display = "turn left"
        else:
            turn = 1.0
            action_display = "turn right"
        self.controller_state.hand_brake = False
        self.controller_state.throttle = 1.0
        self.controller_state.steer = turn
    

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
   

    
    

