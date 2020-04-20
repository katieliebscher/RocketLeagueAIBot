import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3

from Actions import *
from Debug import *


class MyBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.num_cars = 0
        # Controller inputs
        self.controller_state.throttle = 0
        self.controller_state.steer = 0
        self.controller_state.pitch = 0
        self.controller_state.yaw = 0
        self.controller_state.roll = 0
        self.controller_state.boost = False
        self.controller_state.jump = False
        self.controller_state.handbrake = False
        # Game values
        self.bot_loc_x = 0
        self.bot_loc_y = 0
        self.bot_loc_z = 0
        self.bot_speed_x = 0
        self.bot_speed_y = 0
        self.bot_speed_z = 0
        self.bot_rot_yaw = 0
        self.bot_rot_roll = 0
        self.bot_rot_pitch = 0
        self.bot_jumped = False
        self.bot_doublejumped = False
        self.bot_ground = False
        self.bot_sonic = False
        self.bot_dodge = False
        self.bot_boost = 0
        self.bot_max_speed = [1410, 2300]  # normal, boost
        self.bot_boost_to_max_speed = [27, 57, 30]  # to normal, to boost, from normal to boost
        self.ball_loc_x = 0
        self.ball_loc_y = 0
        self.ball_loc_z = 0
        self.ball_speed_x = 0
        self.ball_speed_y = 0
        self.ball_speed_z = 0
        self.ball_ang_speed_x = 0
        self.ball_ang_speed_y = 0
        self.ball_ang_speed_z = 0
        self.ball_lt_x = 0
        self.ball_lt_y = 0
        self.ball_lt_z = 0
        self.ball_lt_time = 0
        self.game_time = 0
        self.game_ball_touched = False
        # game values converted
        self.bot_yaw = 0
        self.bot_pitch = 0
        self.bot_roll = 0
        self.angle_front_to_target = 0
        self.angle_car_ball = 0
        # custom values
        self.angle_car_ball = 0
        self.distance_car_ball = 0
        self.bot_speed_linear = 0
        self.ball_initial_speed_z = 0
        self.ball_initial_pos_z = 0
        self.ball_test_for_start = False

        self.ttt = 0.00
        self.lt_time = 0.00
        self.prediction = [[], []]
        self.printed = False

        self.predicted_loc = [[0, 0, 0], [[0, 0, 0], [0, 0, 0], [0, 0, 0]], [0], [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]
        self.game_time_lst = []
        self.ball_speed_x_lst = []
        self.ball_speed_y_lst = []
        self.ball_speed_z_lst = []
        self.ball_ang_speed_x_lst = []
        self.ball_ang_speed_y_lst = []
        self.ball_ang_speed_z_lst = []
        self.ball_loc_x_lst = []
        self.ball_loc_y_lst = []
        self.ball_loc_z_lst = []

        self.bounce_n = 0
        self.hit = False
        self.realtime = [[], []]
        self.time_to_hit = 1
        self.jump_time_end = 0
        self.flick_time = 0
        self.stop_flick = False
        self.last_predict = 0

    def distance(self, x1, y1, z1, x2, y2, z2):
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
        return distance

    def get_values(self, values):
        self.controller_state.boost = False

        if self.jump_time_end < self.game_time:
            self.controller_state.jump = False

        if self.stop_flick:
            self.controller_state.pitch = 0
            self.controller_state.roll = 0
            self.flick_time = 0
            self.stop_flick = False
            # print('flip stopped')

        if self.flick_time < self.game_time and self.flick_time != 0:
            self.controller_state.jump = True
            self.stop_flick = True
            # print('stopping flick')

        # Update game data variables
        self.bot_team = values.game_cars[self.index].team

        self.bot_loc = Vec3(values.game_cars[self.index].physics.location)
        self.bot_rot = values.game_cars[self.index].physics.rotation
        self.ball_loc = Vec3(values.game_ball.physics.location)
        self.ball_lt = values.game_ball.latest_touch
        self.bot_yaw = values.game_cars[self.index].physics.rotation.yaw
        # get game values
        self.bot_loc_x = values.game_cars[self.index].physics.location.x
        self.bot_loc_y = values.game_cars[self.index].physics.location.y
        self.bot_loc_z = values.game_cars[self.index].physics.location.z
        self.bot_speed_x = values.game_cars[self.index].physics.velocity.x
        self.bot_speed_y = values.game_cars[self.index].physics.velocity.y
        self.bot_speed_z = values.game_cars[self.index].physics.velocity.z
        self.bot_jumped = values.game_cars[self.index].jumped
        self.bot_doublejumped = values.game_cars[self.index].double_jumped
        self.bot_sonic = values.game_cars[self.index].is_super_sonic
        self.bot_ground = values.game_cars[self.index].has_wheel_contact
        self.bot_boost = values.game_cars[self.index].boost

        self.ball_loc_x = values.game_ball.physics.location.x
        self.ball_loc_x_lst += [self.ball_loc_x]
        self.ball_loc_y = values.game_ball.physics.location.y
        self.ball_loc_y_lst += [self.ball_loc_y]
        self.ball_loc_z = values.game_ball.physics.location.z
        self.ball_loc_z_lst += [self.ball_loc_z]
        self.ball_speed_x = values.game_ball.physics.velocity.x
        self.ball_speed_x_lst += [self.ball_speed_x]
        self.ball_speed_y = values.game_ball.physics.velocity.y
        self.ball_speed_y_lst += [self.ball_speed_y]
        self.ball_speed_z = values.game_ball.physics.velocity.z
        self.ball_speed_z_lst += [self.ball_speed_z]
        self.ball_ang_speed_x = values.game_ball.physics.angular_velocity.x
        self.ball_ang_speed_x_lst += [self.ball_ang_speed_x]
        self.ball_ang_speed_y = values.game_ball.physics.angular_velocity.y
        self.ball_ang_speed_y_lst += [self.ball_ang_speed_y]
        self.ball_ang_speed_z = values.game_ball.physics.angular_velocity.z
        self.ball_ang_speed_z_lst += [self.ball_ang_speed_z]
        self.ball_lt_x = values.game_ball.latest_touch.hit_location.x
        self.ball_lt_y = values.game_ball.latest_touch.hit_location.y
        self.ball_lt_z = values.game_ball.latest_touch.hit_location.z
        self.ball_lt_time = values.game_ball.latest_touch.time_seconds
        self.ball_lt_normal_x = values.game_ball.latest_touch.hit_normal.x
        self.ball_lt_normal_y = values.game_ball.latest_touch.hit_normal.y
        self.ball_lt_normal_z = values.game_ball.latest_touch.hit_normal.z

        self.game_time = values.game_info.seconds_elapsed
        self.game_time_lst += [self.game_time]
        self.game_time_left = values.game_info.game_time_remaining
        self.game_overtime = values.game_info.is_overtime
        self.game_active = values.game_info.is_round_active
        self.game_ended = values.game_info.is_match_ended
        self.renderCalls = []
        # self.game_ball_touched = values.game_info.is_kickoff_pause
        if values.game_info.is_kickoff_pause:
            self.game_ball_touched = False
        else:
            self.game_ball_touched = True

        self.num_cars = values.num_cars

        # get custom values
        self.realime = [self.game_time_lst, [[self.ball_loc_x_lst], [self.ball_loc_y_lst], [self.ball_loc_z_lst]]]
        self.angle_car_ball = math.degrees(
            math.atan2(self.ball_loc_y - self.bot_loc.y, self.ball_loc_x - self.bot_loc.x)) - self.bot_rot_yaw
        self.distance_car_ball = self.distance(self.bot_loc_x, self.bot_loc_y, self.bot_loc_z, self.ball_loc_x,
                                               self.ball_loc_y, self.ball_loc_z) - 93
        self.bot_speed_linear = self.distance(self.bot_speed_x, self.bot_speed_y, self.bot_speed_z, 0, 0, 0)

        # Convert car's yaw, pitch and roll and convert from Unreal Rotator units to degrees
        self.bot_rot_yaw = abs(self.bot_rot.yaw) / (2 * math.pi) * 360
        if self.bot_rot.yaw < 0:
            self.bot_rot_yaw *= -1
        self.bot_rot_pitch = abs(self.bot_rot.pitch) / (2 * math.pi) * 360
        if self.bot_rot.pitch < 0:
            self.bot_rot_pitch *= -1
        self.bot_rot_roll = abs(self.bot_rot.roll) / (2 * math.pi) * 360
        if self.bot_rot.roll < 0:
            self.bot_rot_roll *= -1
        
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.get_values(packet) #Update agent information
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

        # Check if it is the kickoff
        if is_kickoff(packet):
            action_display = "kick off"
            drive_for_kickoff(self,  car_to_ball)

        # Check if ball is near our goal
        # elif ourGoalDist < 4000:
        #     #Drive to defensive position
        #     action_display = defend_goal(self, my_car, info.goals[ourGoalIndex], packet.game_ball)


        # Check if ball is near opponent's goal
        elif opponentGoalDist < 5000:
            action_display = "offensive"

        # # Check if boost level is low
        # elif get_car_boost_level(my_car) < 35:
        #     action_display = "getting boost"
        #     drive_toward_boost(self, my_car, car_to_boost)


        # Default    
        else:
            action_display = "offensive"
            #Current boost activation is in defend_goal
            self.controller_state.boost = False

        draw_debug_message(self.renderer, my_car, action_display)
        if(action_display == "blocking shot"):
            draw_block_debug(self.renderer, my_car, info.goals[ourGoalIndex],  packet.game_ball)
        if(action_display == "offensive"):
            play_offense(self)



        if(action_display == "getting boost"):
            self.renderer.begin_rendering()
            self.renderer.draw_line_3d(self.bot_loc, car_to_boost, self.renderer.yellow())
            self.renderer.end_rendering()
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





