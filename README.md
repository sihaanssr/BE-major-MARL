# Multiagent Reinforcement Learning for traffic light signal control

## Testing
After you have installed [SUMO simulator](https://sumo.dlr.de/docs/index.html), you can test the following policies for the following network:
![](https://github.com/sihaanssr/BE-major-MARL/blob/master/Testing/demo%20files/gui/img/map.svg)

* Fixed time policy
* Independent Q-Learning for every agent
* MARL with best response for coordination
* MARL with variable elimination algorithm
* Some state-of-the-art methods

In a terminal (run with Python3):

```bash
cd Testing/demo files/gui
python gui_demo.py
```
In all likelihood this will fail saying with a ```qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.``` error.
To fix this reinstall xcb like so
```bash
sudo apt-get install --reinstall libxcb-xinerama0
```

```bash
cd ../FT
python testTF.py
cd ../indeQ
python marl.py
cd ../brQ
python marl.py
cd ../veQ
python marl.py
cd ../xuQ
python marl.py
```
