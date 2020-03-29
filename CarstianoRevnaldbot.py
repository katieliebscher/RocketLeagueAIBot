import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3

from Actions import *
from Debug import *

#USAGE: ALWAYS PUT OUR BOT ON LEFT SIDE OF RLBOT GUI
#TODO Create check for future ball position and whether it's close to either goal
#TODO Create check for distance between ball and car if ball is near opponents goal, then find proper distance
#TODO Create methods to calculate where to drive to hit ball at proper angle for defense and offense
#TODO Create action for jumping and hitting the ball at proper angle

# Global counter check

class MyBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.counter = 0

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        ball_location = Vec3(packet.game_ball.physics.location)

        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)
        car_to_ball = ball_location - car_location
        car_to_ball_len = car_to_ball.length()

        if car_to_ball_len > 1000:
            ball_future_location = get_ball_predicted_pos(self, 30)
            car_to_ball = ball_future_location - car_location

        
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
        
        #GOAL 0 is defended by bots on right side of GUI (Bot's on left side score on goal 0)
        opponentGoalDist = calculate_ball_to_goal(ball_location, info.goals[opponentGoalIndex])

        #GOAL 1 is defended by bots on left side of GUI (Bot's on right side score on goal 1)
        ourGoalDist = calculate_ball_to_goal(ball_location, info.goals[ourGoalIndex])



        if not packet.game_info.is_round_active:
            self.counter = 0
            action_display = str(self.counter)

        if is_kickoff(packet):
            # Check if I am within the first few frames
            if self.counter < 5:
                drive_toward_ball(self, my_car, car_to_ball)
                self.controller_state.boost = True
                action_display = str(self.counter)
                self.counter += 1
            else:
                action_display = "kick off"
                drive_for_kickoff(self, my_car, car_to_ball, ball_location)

        # Check if ball is near our goal
        elif ourGoalDist < 4000:
            #Drive to defensive position
            action_display = defend_goal(self, my_car, info.goals[ourGoalIndex], packet.game_ball)


        # Check if ball is near opponent's goal
        elif opponentGoalDist < 4000:
            action_display = "offensive"
            ball_future_location = get_ball_predicted_pos(self, 40)
            car_to_ball = ball_future_location - car_location
            #Drive to offensive position
            drive_toward_ball(self, my_car, car_to_ball)
            

        # Check if boost level is low
        elif get_car_boost_level(my_car) < 35:
            action_display = "getting boost"
            drive_toward_boost(self, my_car, car_to_boost)

        # Default    
        else:
            action_display = "just drivin"
            #TODO Figure out how to properly time boosts
            #Current boost activation is in defend_goal
            self.controller_state.boost = False
            drive_toward_ball(self, my_car, car_to_ball)
    
        draw_debug_message(self.renderer, my_car, action_display)

        return self.controller_state

def is_kickoff(packet) -> bool:
    return packet.game_info.is_kickoff_pause

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


    
    

