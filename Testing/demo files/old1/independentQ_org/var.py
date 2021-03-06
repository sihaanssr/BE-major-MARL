'''
Created on 21/09/2016

@author: carolina
'''
import os, sys
import subprocess
sys.path.append("/home/carolina/programs/sumo-0.27.1/tools")
import agent
exec(compile(open("./agent.py").read(), "./agent.py", 'exec'))

global PORT, secondsInHour, hoursInDay, secondsInDay, followPolicy
ports = [8813, 8814, 8815, 8816, 8817, 8818, 8819, 8820] 
PORT = ports[0]
secondsInHour = 60*60
hoursInDay = 24
secondsInDay = hoursInDay*secondsInHour

totalDaysObs = 5 #5
totalDaysTrain = 100
totalDaysTest = 2
minTimeInGreen = 14
minTimeInYellow = 4
lastDay = -1

global project 
project = 'miniCity'
accessNames = ['north', 'east', 'south', 'west']

#============== Agent definition
agents = {}
SLs = [0,1,2,3,4,5]

#agent 0: ak13cl45
ID = 0
listLanes = ['A0N_0', 'A0N_1', 'A0N_2', 'A0W_0', 'A0W_1']
listEdges = ['A0N', 'A0W']
numberLanes = [3,2]
actionPhases = [0,2]
auxPhases = [[-1, 1],[3, -1]]
planNames = ['Plan2_0', 'Plan3_0', 'Plan4_0']
planProgram = {} 
planProgram[planNames[0]] = [3, 0, 1, 2, 3]
planProgram[planNames[1]] = [3, 0, 1, 2, 3]
planProgram[planNames[2]] = [3, 0, 1, 2, 3]
neigbors = [1, 3]
beta = [1,2]
theta = [1.75, 1.75]
agents[0] = agent(ID, listLanes, listEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta)


#agent 1: ak13cl46
ID = 1
listLanes = ['A1N_0', 'A1N_1', 'A1N_2', 'A1E_0', 'A1E_1']
listEdges = ['A1N', 'A1E']
numberLanes = [3,2]
actionPhases = [0,2]
auxPhases = [[-1, 1],[3, -1]]
planNames = ['Plan2_1', 'Plan3_1', 'Plan4_1']
planProgram = {} 
planProgram[planNames[0]] = [3, 0, 1, 2, 3]
planProgram[planNames[1]] = [3, 0, 1, 2, 3]
planProgram[planNames[2]] = [3, 0, 1, 2, 3]
neigbors = [0, 2, 4]
beta = [1,2]
theta = [1.75, 1.75]
agents[1] = agent(ID, listLanes, listEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta)


#agent 2: ak13cl47
ID = 2
listLanes = ['A2N_0', 'A2N_1', 'A2N_2', 'A2E_0', 'A2E_1']
listEdges = ['A2N', 'A2E']
numberLanes = [3,2]
actionPhases = [0,2]
auxPhases = [[-1, 1],[3, -1]]
planNames = ['Plan2_2', 'Plan3_2', 'Plan4_2']
planProgram = {} 
planProgram[planNames[0]] = [2, 3, 0, 1, 2]
planProgram[planNames[1]] = [0, 1, 2, 3, 0]
planProgram[planNames[2]] = [2, 3, 0, 1, 2]
neigbors = [1, 4, 5]
beta = [1,2]
theta = [1.75, 1.75]
agents[2] = agent(ID, listLanes, listEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta)


#agent 3: ak7cl45
ID = 3
listLanes = ['A3N_0', 'A3N_1', 'A3N_2', 'A3S_0', 'A3S_1', 'A3S_2', 'A3W_0', 'A3W_1']
listEdges = ['A3N', 'A3S', 'A3W']
numberLanes = [3,3,2]
actionPhases = [0,2]
auxPhases = [[-1, 1],[3, -1]]
planNames = ['Plan2_3', 'Plan3_3', 'Plan4_3']
planProgram = {} 
planProgram[planNames[0]] = [2, 3, 0, 1, 2]
planProgram[planNames[1]] = [0, 1, 2, 3, 0]
planProgram[planNames[2]] = [2, 3, 0, 1, 2]
neigbors = [0, 4]
beta = [1,2]
theta = [1.75, 1.75]
agents[3] = agent(ID, listLanes, listEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta)


#agent 4: ak7cl46
ID = 4
listLanes = ['A4N_0', 'A4N_1', 'A4N_2', 'A4E_0', 'A4E_1', 'A4S_0', 'A4S_1', 'A4S_2']
listEdges = ['A4N', 'A4E', 'A4S']
numberLanes = [3,2,3]
actionPhases = [0,2]
auxPhases = [[-1, 1],[3, -1]]
planNames = ['Plan2_4', 'Plan3_4', 'Plan4_4']
planProgram = {} 
planProgram[planNames[0]] = [2, 3, 0, 1, 2]
planProgram[planNames[1]] = [0, 1, 2, 3, 0]
planProgram[planNames[2]] = [2, 3, 0, 1, 2]
neigbors = [1, 2, 3, 5]
beta = [1,2]
theta = [1.75, 1.75]
agents[4] = agent(ID, listLanes, listEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta)


#agent 5: ak7cl47
ID = 5
listLanes = ['A5N_0', 'A5N_1', 'A5N_2', 'A5E_0', 'A5E_1', 'A5S_0', 'A5S_1', 'A5S_2']
listEdges = ['A5N', 'A5E', 'A5S']
numberLanes = [3,2,3]
actionPhases = [0,2]
auxPhases = [[-1, 1],[3, -1]]
planNames = ['Plan2_5', 'Plan3_5', 'Plan4_5']
planProgram = {} 
planProgram[planNames[0]] = [2, 3, 0, 1, 2]
planProgram[planNames[1]] = [0, 1, 2, 3, 0]
planProgram[planNames[2]] = [2, 3, 0, 1, 2]
neigbors = [2, 4]
beta = [1,2]
theta = [1.75, 1.75]
agents[5] = agent(ID, listLanes, listEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta)

del ID, listLanes, listEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta

numAgents = len(agents)

#============== Other definition

#neighborsList = [[0,1],[0,3],[1,2],[1,4],[2,5],[3,4],[4,5]]
neighborsList = [[0,1],[0,3],[1,0],[1,2],[1,4],[2,1],[2,4],[2,5],[3,0],[3,4],[4,1],[4,2],[4,3],[4,5],[5,2],[5,4]]
# neighboursUpdated = [False, False, False, False, False, False, False, False, False, False, False, False]
neighborsPerAgent = []
for agt in range(numAgents):
    neighborsPerAgent.append([i for i in range(len(neighborsList)) if(agt in neighborsList[i])])
numNeighbourPairs = len(neighborsList)



routesList = [
    "A0W A9N ", \
    "A0W A14W A3W A18N ", \
    "A0W A14W A3W A20W ", \
    "A0W A14W A3W A4S A5S A19S ", \
    "A2N A8E ", \
    "A2N A1N A7E ", \
    "A2N A1N A0N A6E ", \
    "A2N A1N A0N A9N ", \
    "A2N A1N A0N A14W A3W A18N ", \
    "A2N A1N A0N A14W A3W A20W ", \
    "A2N A1N A0N A14W A3W A4S A5S A19S ", \
    "A5N A16E A17S ", \
    "A5N A16E A12E A13S ", \
    "A5N A16E A12E A2E A8E ", \
    "A5N A16E A12E A2E A1N A7E ", \
    "A5N A16E A12E A2E A1N A0N A6E ", \
    "A5N A16E A12E A2E A1N A0N A9N ", \
    "A5N A16E A12E A2E A1N A0N A14W A3W A18N ", \
    "A5N A16E A12E A2E A1N A0N A14W A3W A20W ", \
    "A5N A16E A12E A2E A1N A0N A14W A3W A4S A5S A19S ", \
    "A5N A4N A15E A16S A17S ", \
    "A5N A4N A15E A16S A12E A13S ", \
    "A5N A4N A15E A16S A12E A2E A8E ", \
    "A5N A4N A15E A16S A12E A2E A1N A7E ", \
    "A5N A4N A15E A16S A12E A2E A1N A0N A6E ", \
    "A5N A4N A15E A16S A12E A2E A1N A0N A9N ", \
    "A5N A4N A15E A16S A12E A2E A1N A0N A14W A3W A18N ", \
    "A5N A4N A15E A16S A12E A2E A1N A0N A14W A3W A20W ", \
    "A5N A4N A15E A16S A12E A2E A1N A0N A14W A3W A4S A5S A19S ", \
    "A5N A4N A15E A11E A12S A13S ", \
    "A5N A4N A15E A11E A12S A2E A8E ", \
    "A5N A4N A15E A11E A12S A2E A1N A7E ", \
    "A5N A4N A15E A11E A12S A2E A1N A0N A6E ", \
    "A5N A4N A15E A11E A12S A2E A1N A0N A9N ", \
    "A5N A4N A15E A11E A12S A2E A1N A0N A14W A3W A18N ", \
    "A5N A4N A15E A11E A12S A2E A1N A0N A14W A3W A20W ", \
    "A5N A4N A15E A11E A12S A2E A1N A0N A14W A3W A4S A5S A19S ", \
    "A5N A4N A15E A11E A1E A7E ", \
    "A5N A4N A15E A11E A1E A0N A6E ", \
    "A5N A4N A15E A11E A1E A0N A9N ", \
    "A5N A4N A15E A11E A1E A0N A14W A3W A18N ", \
    "A5N A4N A15E A11E A1E A0N A14W A3W A20W ", \
    "A5N A4N A15E A11E A1E A0N A14W A3W A4S A5S A19S ", \
    "A5N A4N A3N A18N ", \
    "A3S A20W ", \
    "A3S A4S A5S A19S ", \
    "A4E A5S A19S ", \
    "A4E A3N A18N ", \
    "A4E A15E A16S A17S ", \
    "A4E A15E A16S A12E A13S ", \
    "A4E A15E A16S A12E A2E A8E ", \
    "A4E A15E A16S A12E A2E A1N A7E ", \
    "A4E A15E A16S A12E A2E A1N A0N A6E ", \
    "A4E A15E A16S A12E A2E A1N A0N A9N ", \
    "A4E A15E A16S A12E A2E A1N A0N A14W A3W A18N ", \
    "A4E A15E A16S A12E A2E A1N A0N A14W A3W A20W ", \
    "A4E A15E A16S A12E A2E A1N A0N A14W A3W A4S A5S A19S ", \
    "A4E A15E A11E A12S A13S ", \
    "A4E A15E A11E A12S A2E A8E ", \
    "A4E A15E A11E A12S A2E A1N A7E ", \
    "A4E A15E A11E A12S A2E A1N A0N A6E ", \
    "A4E A15E A11E A12S A2E A1N A0N A9N ", \
    "A4E A15E A11E A12S A2E A1N A0N A14W A3W A18N ", \
    "A4E A15E A11E A12S A2E A1N A0N A14W A3W A20W ", \
    "A4E A15E A11E A12S A2E A1N A0N A14W A3W A4S A5S A19S ", \
    "A4E A15E A11E A1E A7E ", \
    "A4E A15E A11E A1E A0N A6E ", \
    "A4E A15E A11E A1E A0N A9N ", \
    "A4E A15E A11E A1E A0N A14W A3W A18N ", \
    "A4E A15E A11E A1E A0N A14W A3W A20W ", \
    "A4E A15E A11E A1E A0N A14W A3W A4S A5S A19S ", \
    "A5E A19S ", \
    "A5E A4N A15E A16S A17S ", \
    "A5E A4N A15E A16S A12E A13S ", \
    "A5E A4N A15E A16S A12E A2E A8E ", \
    "A5E A4N A15E A16S A12E A2E A1N A7E ", \
    "A5E A4N A15E A16S A12E A2E A1N A0N A6E ", \
    "A5E A4N A15E A16S A12E A2E A1N A0N A9N ", \
    "A5E A4N A15E A16S A12E A2E A1N A0N A14W A3W A18N ", \
    "A5E A4N A15E A16S A12E A2E A1N A0N A14W A3W A20W ", \
    "A5E A4N A15E A16S A12E A2E A1N A0N A14W A3W A4S A5S A19S ", \
    "A5E A4N A15E A11E A12S A13S ", \
    "A5E A4N A15E A11E A12S A2E A8E ", \
    "A5E A4N A15E A11E A12S A2E A1N A7E ", \
    "A5E A4N A15E A11E A12S A2E A1N A0N A6E ", \
    "A5E A4N A15E A11E A12S A2E A1N A0N A9N ", \
    "A5E A4N A15E A11E A12S A2E A1N A0N A14W A3W A18N ", \
    "A5E A4N A15E A11E A12S A2E A1N A0N A14W A3W A20W ", \
    "A5E A4N A15E A11E A12S A2E A1N A0N A14W A3W A4S A5S A19S ", \
    "A5E A4N A15E A11E A1E A7E ", \
    "A5E A4N A15E A11E A1E A0N A6E ", \
    "A5E A4N A15E A11E A1E A0N A9N ", \
    "A5E A4N A15E A11E A1E A0N A14W A3W A18N ", \
    "A5E A4N A15E A11E A1E A0N A14W A3W A20W ", \
    "A5E A4N A15E A11E A1E A0N A14W A3W A4S A5S A19S ", \
    "A5E A4N A3N A18N ", \
    "A5E A16E A17S ", \
    "A5E A16E A12E A13S ", \
    "A5E A16E A12E A2E A8E ", \
    "A5E A16E A12E A2E A1N A7E ", \
    "A5E A16E A12E A2E A1N A0N A6E ", \
    "A5E A16E A12E A2E A1N A0N A9N ", \
    "A5E A16E A12E A2E A1N A0N A14W A3W A18N ", \
    "A5E A16E A12E A2E A1N A0N A14W A3W A20W ", \
    "A5E A16E A12E A2E A1N A0N A14W A3W A4S A5S A19S ", \
]
