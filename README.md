# RocketLeagueAIBot: Carstiano Revnaldbot

This project is for the University of Notre Dame Course: Game-Based AI Bots

### Control Mechanism and High Level Strategy
The win conditions of this game are 1. Score goals and 2. Prevent the other team from scoring goals. We then created a Behvaior Tree which implements our high level strategy aimed at successfully accomplishing these win conditions.
![Btree](Btree.png)


### Dependencies
These are the dependencies that will be installed when the Rocket League Bot Gui is first run. They are:

- backports
- certifi
- chardet
- colorama
- configparser.py
- crayons
- dataclasses.py
- flatbuffers
- idna
- inputs.py
- numpy
- psutil
- py4j
- PyQt5
- requests
- rlbot
- rlbot_gui
- RLUtilities
- selenium
- urllib3
- webdriver_manager
- websockets

### Download Instructions and Configuration
In order to use this bot, download this repository and run the following commands.

1. `make install`

2. `setup.bat`

These commands will download the RLBot GUI and install all of the above dependencies.

#### Note: The GUI requires Windows Operating System and an existing copy of Rocket League (which can be purchased on Steam).

Run the .exe file and drag the bot named "Carstiano Revnaldbot" to either of the team fields.
Other team members or opponents are not required, but can be added by also dragging the bots to the respective teams.
By clicking "Start", the GUI will start a game in Rocket League with the bot(s).
The game continues until time runs out or "Stop" is clicked in the GUI.


### Features Implemented
Offensive:

1. Ball Adjusting Path Prediction: When the bot is in offensive mode, the bot calculates both the distance to the ball and to the goal and adjusts the proper amount of time ahead the bot should use to calculate the desired future location.

2. Shots on Goal: Bot properly calculates the direction the ball is traveling, the direction to the goal and is able to choose the proper direction in which to jump in order to properly aim its shot.

Defensive:

1. Flip Kick Defense: When a bot is in the defensive mode, it checks if the ball is in close enough range to use a flip kick the ball away from the goal. This is done using vectors, we are able to check the location and direction of the car with respect to the goal and ball, and then select the proper direction for the bot to flip.

2. Goal Blocking and Orientation: If the bot is still in defensive mode, but is not close enough to the ball to kick, then the bot will instead choose to sprint to the goal and orient itself towards the ball in order to "kick" it away from the goal once it is within range.

General Gameplay: 

1. Nearest Boost Path Finding: When a bot is neither offensive nor defensive, and when the bot has low boost, we have implemented a search algorithm which allows for the bot to find the nearest boost.

2. Bot Driving Up Goal Walls: In an attempt to debug issues regarding directionality, our bot has functionality which attempts to prevent it from driving up the walls of the goal. With this, we can avoid incorrect movement as a result of z-axis movement.

3. Implemented Ball Path Prediction: Depending on the game state, the bot will utilize different variations of path finding in order to choose the best future location in order to properly hit the ball in the desired direction.  

### Expert Knowledge

The main piece of expert knowledge that has been incorporated into this bot is the idea that on defense, a bot should choose to block a shot first as its main priority. If the ball is within range, the bot choose to deflect the ball away from the goal rather than reorienting itself in between the ball and the goal first. Also, we know that if the bot is too far away from the goal when it is playing defense getting back to that end of the field is paramount and the bot uses its boost to sprint towards to goal in order to protect from being scored on. 

### Future Feature Extensions

1. Heuristic Boost Path Prediction: In the future, if a heuristic search algorithm is used for the boost path prediction, we could update this search algorithm to choose a boost which is both near and in the direction which the car wishes to go. The current model does not take into account the location of the ball, or desired future location for the car, instead it simply checks the closest boost.

2. Ariels: Utilize the flip kick base code and implement arial features. This would be accomplished by utilizing similar path prediction and timing prediction for car location, however the proper z-axis vector calculations would need to be taken into account as well.
