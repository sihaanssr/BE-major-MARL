'''
Created on 4/09/2016

@author: carolina
'''

class agentTF():
    
    def __init__(self, ID, listLanes, listEdges, lengthEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors):
        self.SL = ID
        self.listLanes = listLanes
        self.listEdges = listEdges
        self.lengthEdges = lengthEdges
        self.numberLanes = numberLanes
        self.NESW = map(lambda z: 1*(z>0),numberLanes)
        self.numEdges = len(listEdges)
        self.numLanes = len(listLanes)
        self.actionPhases = actionPhases
        self.auxPhases = auxPhases
        self.planProgram = planProgram
        self.numActions = len(actionPhases)
        #self.updatedState = False
        self.neighbors = neigbors
        self.numNeighbors = len(neigbors)
        
        #Reward properties
        self.beta = [1,2]
        self.theta = [1.75, 1.75] 
        
        #Almacenar informacion del agente por lane (colas, tiempo de espera)      
        self.laneQueueTracker = {}
        self.laneWaitingTracker = {} 
        self.laneSpeedTracker = {}
        for lane in self.listLanes:
            self.laneQueueTracker[lane] = 0
            self.laneWaitingTracker[lane] = 0  
            self.laneSpeedTracker[lane] = 0          
        
        #Almacenar informacion del agente por edge (colas, tiempo de espera)  
        self.queueTracker = {}
        self.waitingTracker = {}
        self.speedTracker = {}
        for edge in self.listEdges:
            self.queueTracker[edge] = 0
            self.waitingTracker[edge] = 0
            self.speedTracker[edge] = 0
        
        self.secsThisPhase = 0
        self.currPhaseID = 0
        self.newPhaseID = 0
        self.currReward = 0
    
    def initAgent(self):
        self.secsThisPhase = 0
        self.currPhaseID = 0
    
    def updateReward(self):
        reward = 0
        for key in self.listEdges:
            reward -= ((self.beta[0]*self.queueTracker[key])*self.theta[0] + (self.beta[1]*self.waitingTracker[key])**self.theta[1]) 
        self.currReward = reward