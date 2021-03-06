'''
Created on 22/09/2016

@author: carolina
'''
import numpy as np
import pandas as pd
import random
from random import randint
import itertools

import var

class agent():
    
    def __init__(self, ID, listLanes, listEdges, lengthEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta):
        self.SL = ID
        self.listLanes = listLanes
        self.listEdges = listEdges
        self.lengthEdges = lengthEdges
        self.numberLanes = numberLanes
        self.NESW = [1*(z>0) for z in numberLanes]
        self.numEdges = len(listEdges)
        self.numLanes = len(listLanes)
        self.actionPhases = actionPhases
        self.auxPhases = auxPhases
        self.planProgram = planProgram
        self.updatedState = False
        self.neighbors = neigbors
        self.numNeighbors = len(neigbors)
        
        #Reward properties
        self.beta = beta
        self.theta = theta 
        self.gamma = 0.9
        self.epsilon = 1.0
        
        #Almacenar informacion del agente por lane (colas, tiempo de espera)      
        self.laneQueueTracker = {}
        self.laneWaitingTracker = {} 
        for lane in self.listLanes:
            self.laneQueueTracker[lane] = 0
            self.laneWaitingTracker[lane] = 0            
        
        #Almacenar informacion del agente por edge (colas, tiempo de espera)  
        self.queueTracker = {}
        self.waitingTracker = {}
        for edge in self.listEdges:
            self.queueTracker[edge] = 0
            self.waitingTracker[edge] = 0
        
        self.secsThisPhase = 0
        self.currPhaseID = 0
        self.newPhaseID = 0
        self.currReward = 0
        
        #======== Data for each neighbor
        self.numStates = 0
        self.jointActions = {}
        self.numJointActions = 0      
        
        #state, action, laststate
        self.currJointStateID = 0
        self.lastJointStateID = 0
        self.lastJointAction = 0
        
        #State discretization
        self.dictClusterObjects = {}
        self.numClustersTracker = {}            
        self.mapDiscreteStates = {}
        self.cluster_centers = {}      
        
        #Learning tables
        self.QValues = {}
        self.QCounts = {}
        self.QAlpha ={}
        self.pBayes = {}
        self.bayes_num1 = {}
        self.bayes_num2 = {}
        for n in self.neighbors:
            self.pBayes[n]={}
            self.bayes_num1[n]={}
            self.bayes_num2[n]={}
        self.bayes_den1={}
   
    def initAgent(self): 
        aux = np.array(self.actionPhases)
        for n in range(self.numNeighbors):
            nb = self.neighbors[n]
            aux = np.vstack([aux, var.agents[nb].actionPhases])
        self.jointActions = list(itertools.product(*aux))
        self.numJointActions = len(self.jointActions)
        
        self.QValues = np.zeros((self.numStates, self.numJointActions))
        self.QCounts = np.zeros((self.numStates, self.numJointActions))
        self.QAlpha = np.ones((self.numStates, self.numJointActions))
        
        self.bayes_den1 = np.ones((self.numStates, len(self.actionPhases)))
        
        for n in self.neighbors:
            self.pBayes[n] = np.zeros((len(var.agents[n].actionPhases), len(self.actionPhases)*self.numStates))
            self.bayes_num1[n] = np.ones((self.numStates, len(self.actionPhases)*len(var.agents[n].actionPhases)))
            self.bayes_num2[n] = np.ones(len(var.agents[n].actionPhases))
    
        self.secsThisPhase = 0
        self.currPhaseID = 0
    
    def getJointAction(self):
        ph_i = self.currPhaseID
        if(ph_i%2 != 0):
            ph_i -= 1
        jAct = (ph_i,)
        for n in self.neighbors:            
            ph_j = var.agents[n].currPhaseID
            if(ph_j%2 != 0):
                ph_j -= 1
            jAct = jAct + (ph_j,)        
            
        idx = self.jointActions.index(jAct)
        return idx
    
    def updateReward(self):
        reward = 0
        for key in self.listEdges:
            reward -= ((self.beta[0]*self.queueTracker[key])*self.theta[0] + (self.beta[1]*self.waitingTracker[key])**self.theta[1]) 
        self.currReward = reward
    
    def learnPolicy(self, day, currHod):
        #get joint state
        state = []
        for edge in self.listEdges:
            state.append(self.queueTracker[edge])    
        for edge in self.listEdges:
            state.append(self.waitingTracker[edge])
        for nb in self.neighbors:
            for edge in var.agents[nb].listEdges:
                state.append(var.agents[nb].queueTracker[edge])    
            for edge in var.agents[nb].listEdges:
                state.append(var.agents[nb].waitingTracker[edge])
        state = np.array(state)
        stateSubID = int(self.dictClusterObjects[currHod].predict(state))
        self.currJointStateID = self.mapDiscreteStates[currHod][stateSubID]
        
        #UPDATE BELIEF OF OTHER AGENTS
        for n in self.neighbors:
            ai = var.agents[n].currPhaseID;
            ai_ID = var.agents[n].actionPhases.index(ai)
            ani = [x for x in var.agents[n].actionPhases if x != ai]; 
            ani_ID = var.agents[n].actionPhases.index(ani[0])
            ak = self.currPhaseID;          
            ak_ID = self.actionPhases.index(ak)
            jAct = list(itertools.product(var.agents[n].actionPhases, self.actionPhases)).index((ai,ak))
            jAct2 = list(itertools.product(var.agents[n].actionPhases, self.actionPhases)).index((ani[0],ak))
            s = self.currJointStateID
            self.bayes_num1[n][self.currJointStateID,jAct] += 1.0
            self.bayes_den1[self.currJointStateID,ak_ID] +=1.0
            self.bayes_num2[n][ai_ID] += 1.0
#             a = self.bayes_num2[n][ai_ID]/(np.sum(self.bayes_num2[n]))
#             b = self.bayes_num1[n][s,jAct]/(self.bayes_num1[n].sum(axis=0)[jAct])
#             c = self.bayes_num2[n][ani_ID]/(np.sum(self.bayes_num2[n]))
#             d = self.bayes_num1[n][s,jAct2]/(self.bayes_num1[n].sum(axis=0)[jAct2])
            
#             jAS = list(itertools.product(self.actionPhases, range(0,self.numStates))).index((ak,s))
#             self.pBayes[n][ai_ID,jAS] = (a*b)/((a*b)+(c*d))
            
        #UPDATE Q
        s = self.lastJointStateID
        s_new = self.currJointStateID
        act = self.lastJointAction
        r = self.currReward
        alpha = self.QAlpha[s,act]
        
        #get bayesian inference
        prob = []
        for action in self.jointActions:
            ak = action[0]
            jAS = list(itertools.product(self.actionPhases, list(range(0,self.numStates)))).index((ak,s_new))
            aux = 1.0
            for i in range(1,len(action)):
                n = self.neighbors[i-1]
                ai = var.agents[n].actionPhases.index(action[i])
                ani = [x for x in var.agents[n].actionPhases if x != action[i]]; 
                ani_ID = var.agents[n].actionPhases.index(ani[0])
                jAct = list(itertools.product(var.agents[n].actionPhases, self.actionPhases)).index((action[i],ak))
                jAct2 = list(itertools.product(var.agents[n].actionPhases, self.actionPhases)).index((ani[0],ak))
                a = self.bayes_num2[n][ai]/(np.sum(self.bayes_num2[n]))
                b = self.bayes_num1[n][s_new,jAct]/(self.bayes_num1[n].sum(axis=0)[jAct])
                c = self.bayes_num2[n][ani_ID]/(np.sum(self.bayes_num2[n]))
                d = self.bayes_num1[n][s_new,jAct2]/(self.bayes_num1[n].sum(axis=0)[jAct2])
                self.pBayes[n][ai,jAS] = (a*b)/((a*b)+(c*d))
                aux = aux * self.pBayes[n][ai,jAS]
            prob.append(aux*self.QValues[s_new, self.jointActions.index(action)])
        maxQ = np.max(prob)
            
        self.QValues[s, act] = (1.0-alpha)*(self.QValues[s, act]) + (alpha)*(r + self.gamma*maxQ)
        self.QCounts[s,act] += 1  
        self.QAlpha[s,act] = 1.0/self.QCounts[s,act]
        
    def updateJointAaction(self): 
        self.lastJointAction = self.getJointAction()
        self.lastJointStateID = self.currJointStateID
    
    def chooseAction(self, day, currHod):
        s = self.currJointStateID
        prob = []
        for action in self.jointActions:
            ak = action[0]
            jAS = list(itertools.product(self.actionPhases, list(range(0,self.numStates)))).index((ak,s))
            aux = 1.0
            for i in range(1,len(action)):
                n = self.neighbors[i-1]
                ai = var.agents[n].actionPhases.index(action[i])
                aux = aux * self.pBayes[n][ai,jAS]
            prob.append(aux*self.QValues[s, self.jointActions.index(action)])
        id_jAct = [x for x in range(len(prob)) if prob[x] == np.max(prob)]
        if(len(id_jAct)==1):
            ak = self.jointActions[id_jAct[0]][0]
        else:
            seed = (1.0*day)+(currHod/23.0)
            random.seed(seed)
            unigen = random.random()
            random.seed()
            aux = random.randint(0,len(id_jAct)-1)
            idx = id_jAct[aux]
            ak = self.jointActions[idx][0]
        
        #decide if explore or exploit
        seed = (1.0*day)+(currHod/23.0)
        random.seed(seed)
        unigen = random.random()
        self.epsilon = np.exp(-(1.0/60.0)*((1.0*day)+(currHod/23.0)))           
        if(unigen < self.epsilon): #Exploration?
            random.seed()
            idx_act = random.randint(0,len(self.actionPhases)-1)
            ak = self.actionPhases[idx_act]
            
        #next phase to apply
        self.newPhaseID = ak
    
    def followPolicy(self, day, currHod):
        #get joint state
        state = [currHod]
        for edge in self.listEdges:
            state.append(self.queueTracker[edge])    
        for edge in self.listEdges:
            state.append(self.waitingTracker[edge])
        for nb in self.neighbors:
            for edge in var.agents[nb].listEdges:
                state.append(var.agents[nb].queueTracker[edge])    
            for edge in var.agents[nb].listEdges:
                state.append(var.agents[nb].waitingTracker[edge])
        state = np.array(state)
        res = np.linalg.norm(state.T-self.cluster_centers, axis=1, ord=2)
        self.currJointStateID = np.argmin(res)

        #stateSubID = int(self.dictClusterObjects[currHod].predict(state))
        #self.currJointStateID = self.mapDiscreteStates[currHod][stateSubID]
        
        s = self.currJointStateID
        prob = []
        for action in self.jointActions:
            ak = action[0]
            jAS = list(itertools.product(self.actionPhases, list(range(0,self.numStates)))).index((ak,s))
            aux = 1.0
            for i in range(1,len(action)):
                n = self.neighbors[i-1]
                ai = var.agents[n].actionPhases.index(action[i])
                aux = aux * self.pBayes[n][ai,jAS]
            prob.append(aux*self.QValues[s, self.jointActions.index(action)])
        id_jAct = [x for x in range(len(prob)) if prob[x] == np.max(prob)]
        if(len(id_jAct)==1):
            ak = self.jointActions[id_jAct[0]][0]
        else:
            seed = (1.0*day)+(currHod/23.0)
            random.seed(seed)
            unigen = random.random()
            random.seed()
            aux = random.randint(0,len(id_jAct)-1)
            idx = id_jAct[aux]
            ak = self.jointActions[idx][0]
        
        #next phase to apply
        self.newPhaseID = ak
        
    
    def loadKnowledge(self, day):
        aux = np.array(self.actionPhases)
        for n in range(self.numNeighbors):
            nb = self.neighbors[n]
            aux = np.vstack([aux, var.agents[nb].actionPhases])
        self.jointActions = list(itertools.product(*aux))
        self.numJointActions = len(self.jointActions)
        self.cluster_centers = pd.read_csv('./states/recoveryStates_'+str(self.SL)+'.csv',
                                sep=' ', skipinitialspace=True, header=None)
        self.cluster_centers = self.cluster_centers.values
        self.numStates = self.cluster_centers.shape[0]

        df=pd.DataFrame.from_csv('./train/QValues_agt' + str(self.SL) + '_day' + str(day) + '.csv')
        self.QValues = df.values
        # df=pd.DataFrame.from_csv('QAlphas_agt' + str(self.SL) + '_day' + str(day) + '.csv')
        # self.QAlpha = df.values
        # df=pd.DataFrame.from_csv('QCounts_agt' + str(self.SL) + '_day' + str(day) + '.csv')
        # self.QCounts = df.values
        # df=pd.DataFrame.from_csv('bayes_den1_agt' + str(self.SL) + '_day' + str(day) + '.csv')
        # self.bayes_den1 = df.values
        
        for nb in self.neighbors:
            # df=pd.DataFrame.from_csv('bayes_num1_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')
            # self.bayes_num1[nb] = df.values
            # df=pd.DataFrame.from_csv('bayes_num2_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')
            # self.bayes_num2[nb] = df.values
            df=pd.DataFrame.from_csv('./train/pBayes_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')
            self.pBayes[nb] = df.values           
                        
        self.secsThisPhase = 0
        self.currPhaseID = 0
        
    
    def saveLearning(self, day):
        df = pd.DataFrame(self.QValues); df.to_csv('QValues_agt' + str(self.SL) + '_day' + str(day) + '.csv')
        df = pd.DataFrame(self.QAlpha);  df.to_csv('QAlphas_agt' + str(self.SL) + '_day' + str(day) + '.csv')
        df = pd.DataFrame(self.QCounts); df.to_csv('QCounts_agt' + str(self.SL) + '_day' + str(day) + '.csv')
        df = pd.DataFrame(self.bayes_den1); df.to_csv('bayes_den1_agt' + str(self.SL) + '_day' + str(day) + '.csv')
        for nb in self.neighbors:            
            df = pd.DataFrame(self.bayes_num1[nb]); df.to_csv('bayes_num1_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')
            df = pd.DataFrame(self.bayes_num2[nb]); df.to_csv('bayes_num2_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')            
            df = pd.DataFrame(self.pBayes[nb]); df.to_csv('pBayes_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')