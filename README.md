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


