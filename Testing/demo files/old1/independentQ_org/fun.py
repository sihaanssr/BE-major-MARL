'''
Created on 22/09/2016

@author: carolina
'''
import os, sys
import subprocess
#sys.path.append("/Users/carolinaHiguera/Programas/sumo-0.27.1/tools")
#sys.path.append("/home/camilo/programs/sumo-0.27.1/tools")
sys.path.append("/home/carolina/Programas/sumo-0.27.1/tools")
import traci
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sklearn
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import var
import arrivalRateGen

listMeanReward = []
listMedianReward = []
listMinReward = []

def computeReward(agtID, queueTracker, waitingTracker):
    reward = 0
    for key in var.agents[agtID].listEdges:
        reward -= ((var.agents[agtID].beta[0]*queueTracker[key])**var.agents[agtID].theta[0] + (var.agents[agtID].beta[1]*waitingTracker[key])**var.agents[agtID].theta[1]) 
    return reward

def learnDiscretization(daysToObserve):
    global listMeanReward, listMedianReward, listMinReward
    
    for sl in var.SLs:
        var.agents[sl].initAgent()
    
    stateData = {}
    for agt in range(0,var.numAgents):
        stateData[agt]={}
        for h in range(0,var.hoursInDay):
            stateData[agt][h]={}
            for act in var.agents[agt].actionPhases:
                stateData[agt][h][act]=np.array([])    
    
    
    for day in range(daysToObserve):

        fileOut = open("days.csv","w")
        fileOut.write("Observation day: "+str(day)+"\n")
        fileOut.close()

        # generate the random route schedule for the day
        arrivalRateGen.writeRoutes(day+1)
        projectName = var.project + "-tf.sumo.cfg"
#         sumoProcess = subprocess.Popen(['/Users/carolinaHiguera/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
#                 "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
        sumoProcess = subprocess.Popen(['/home/carolina/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
            "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr)

        traci.init(var.PORT)
        
        dfRewVals = {}
        dfQueueTracker = {}
        dfWaitingTracker = {}
        
        for sl in var.SLs:        
            dfRewVals[sl] = pd.DataFrame()
            dfQueueTracker[sl] = pd.DataFrame()
            dfWaitingTracker[sl] = pd.DataFrame()        
        
        hod = 0
        currSod = 0
                
        while currSod < var.secondsInDay:
            for sl in var.SLs:
                planName = traci.trafficlights.getProgram(str(sl))
                idPhase = int(traci.trafficlights.getPhase(str(sl)))
                phase = var.agents[sl].planProgram[planName][idPhase]
                if(var.agents[sl].currPhaseID == phase and currSod != 0): # if phase HAS NOT changed
                    var.agents[sl].secsThisPhase += 1 # increase the seconds in the currentPhase 
                else: # IF THE PHASE HAS CHANGED
                    var.agents[sl].secsThisPhase = 0
                    var.agents[sl].currPhaseID = phase
            
            #end of yellow phase for some intersection?
            changePhase = [0 == (var.agents[sl].currPhaseID)%2 for sl in var.SLs]
            changeSec = [0 == var.agents[sl].secsThisPhase for sl in var.SLs]
            change = [1==changePhase[i]*changeSec[i] for i in var.SLs]
            
#             if(var.agents[0].currPhaseID==0 and var.agents[1].currPhaseID==0):
#                 print('si esta')
            
            if (True in change):
                agentChanged = [sl for sl in range(var.numAgents) if((changePhase[sl]*changeSec[sl])==1)] #Agents ID who changed phase
                
                #============  HOD
                if hod != currSod/var.secondsInHour:
                    hod = int(currSod/var.secondsInHour)
                    print('observation day = ', day)
                    print('hour = ', hod)
                    
                                   
                
                #=========== UPDATE INFORMATION OF ALL AGENTS WHO CHANGED THEIR PHASE
                for agt in agentChanged:
                    #================= count halted vehicles (4 elements)
                    for lane in var.agents[agt].listLanes:
                        var.agents[agt].laneQueueTracker[lane] = traci.lane.getLastStepHaltingNumber(str(lane))
                    idx = 0
                    for edge in var.agents[agt].listEdges:
                        var.agents[agt].queueTracker[edge] = 0
                        for lane in range(var.agents[agt].numberLanes[idx]):
                            var.agents[agt].queueTracker[edge] += var.agents[agt].laneQueueTracker[str(edge) + '_' + str(lane)]
                        idx += 1
                    
                    # ================ cum waiting time in minutes
                    for lane in var.agents[agt].listLanes:
                        var.agents[agt].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60
                    idx = 0;
                    for edge in var.agents[agt].listEdges:
                        var.agents[agt].waitingTracker[edge] = 0
                        for lane in range(var.agents[agt].numberLanes[idx]):
                            var.agents[agt].waitingTracker[edge] += var.agents[agt].laneWaitingTracker[str(edge) + '_' + str(lane)]
                        idx += 1 
                    
                #============= UPDATE STATES FOR EACH NEIGHBOUR PAIR
                for agt in agentChanged:
                    stateDataEntry = []
                    for edge in var.agents[agt].listEdges:
                        stateDataEntry.append(var.agents[agt].queueTracker[edge])
                    for edge in var.agents[agt].listEdges:
                        stateDataEntry.append(var.agents[agt].waitingTracker[edge])
                    currAction = var.agents[agt].currPhaseID
                    if len(stateData[agt][hod][currAction]) == 0:
                        stateData[agt][hod][currAction] = np.array([stateDataEntry])
                    else:
                        stateData[agt][hod][currAction] = np.vstack([stateData[agt][hod][currAction], stateDataEntry])
                    
#                     nAgt = var.neighborsPerAgent[agt]
#                     for nb in nAgt:
#                         pair = var.neighborsList[nb]
#                         stateDataEntry = []
#                         for sl in pair:                        
#                             for edge in var.agents[sl].listEdges:
#                                 stateDataEntry.append(var.agents[sl].queueTracker[edge])
#                             for edge in var.agents[sl].listEdges:
#                                 stateDataEntry.append(var.agents[sl].waitingTracker[edge])
#                         currJointAction = var.agents[pair[0]].getJointAction(pair[1])
#                         if len(stateData[nb][hod][currJointAction]) == 0:
#                             stateData[nb][hod][currJointAction] = np.array([stateDataEntry])
#                         else:
#                             stateData[nb][hod][currJointAction] = np.vstack([stateData[nb][hod][currJointAction], stateDataEntry])
                                             
                    # ================= track reward function
                    currRewValue = computeReward(agt, var.agents[agt].queueTracker, var.agents[agt].waitingTracker)
                    df = pd.DataFrame([[currSod, currRewValue]]) 
                    dfRewVals[agt] = dfRewVals[agt].append(df, ignore_index=True)
            currSod += 1           
            traci.simulationStep() 
        traci.close() #End one day of observation    
        
        aux = {}
        for i in range(0,3):
            aux[i] = []
        for sl in var.SLs:
            aux[0].append(dfRewVals[sl].mean(axis = 0)[1])
            aux[1].append(dfRewVals[sl].median(axis = 0)[1])
            aux[2].append(dfRewVals[sl].min(axis = 0)[1])
        listMeanReward.append(aux[0])
        listMedianReward.append(aux[1])
        listMinReward.append(aux[2]) 
                  
    #End of observation days
 
    for agt in range(0,var.numAgents):    
        fileOut = open("recoveryStates_agt"+str(agt)+".csv","w")
        for h in range(0,var.hoursInDay):
            var.agents[agt].numClustersTracker[h] = {}
            var.agents[agt].dictClusterObjects[h] = {}
            for act in var.agents[agt].actionPhases:
                if(len(stateData[agt][h][act]) != 0):
                    var.agents[agt].numClustersTracker[h][act] = int(sum(np.std(stateData[agt][h][act], axis = 0)))
                    if(var.agents[agt].numClustersTracker[h][act] > len(stateData[agt][h][act])):
                        var.agents[agt].numClustersTracker[h][act] = len(stateData[agt][h][act])
                    print('------- Number of clusters -------')
                    print(('agent = ' + str(agt)))
                    print('h = ', h)
                    print('action = ', act)
                    print('numClustersTracker[h][act] = ', var.agents[agt].numClustersTracker[h][act])
                    
                    var.agents[agt].dictClusterObjects[h][act] = KMeans(n_clusters = var.agents[agt].numClustersTracker[h][act])                    
                    var.agents[agt].dictClusterObjects[h][act].fit(stateData[agt][h][act]) 
                    coord = var.agents[agt].dictClusterObjects[h][act].cluster_centers_
                    for k in range(0,var.agents[agt].numClustersTracker[h][act]):
                        fileOut.write(str(h) + "  "  + str(act))
                        list(map(lambda y: fileOut.write("  " + str(y)), coord[k]))
                        fileOut.write("\n")
                else:
                    print(('\n ERROR: Missing data for h:'+str(h)+' (act):'+str(act) + 'for agent '+str(agt)))
        fileOut.close() 
            
        
    for sl in var.SLs:        
        totalClusters = 0;
        for h in range(var.hoursInDay): 
            for act in var.agents[sl].actionPhases:
                totalClusters += var.agents[sl].numClustersTracker[h][act]
        print(('agent ' + str(sl)  + ' ---> totalClusters = ' + str(totalClusters)))
        var.agents[sl].numStates = totalClusters
    
    for sl in var.SLs:        
        stateCounter = 0
        for h in range(var.hoursInDay): 
            var.agents[sl].mapDiscreteStates[h] = {}
            for act in var.agents[sl].actionPhases:
                var.agents[sl].mapDiscreteStates[h][act] = {}
                for c in range(var.agents[sl].numClustersTracker[h][act]):
                    var.agents[sl].mapDiscreteStates[h][act][c] = stateCounter
                    stateCounter += 1
                        
def writeDataClusters():
    dfClusters = pd.DataFrame()
    for agt in range(var.numAgents):        
        for h in range(var.hoursInDay):
            aux = [agt]
            aux.append(h)
            for act in var.agents[agt].actionPhases:
                aux.append(var.agents[agt].numClustersTracker[h][act])
            df = pd.DataFrame([aux])
            dfClusters = dfClusters.append(df, ignore_index=True) 
    aux = ['agt', 'hour', 'F0', 'F1']
    dfClusters.columns = aux
    dfClusters.to_csv('dfClusters.csv')
            

# def plotClusterHistograms():
#     dfClusters = {}
#     for n in range(var.numNeighbourPairs):
#         i = var.neighborsList[n][0]
#         j = var.neighborsList[n][1]
#         dfClusters[n] = pd.DataFrame.from_dict(var.agents[i].numClustersTracker[j], orient = 'index')
#         colNames = []
#         for ki_kj in range(var.agents[i].numActions[j]):
#             colNames.append('Fase '+str(var.agents[i].jointActions[j][ki_kj]))
#         dfClusters[i].columns = colNames
#         dfClusters[i].plot(kind = 'bar', stacked = True)
#         plt.xlabel('Hora')
#         plt.ylabel('Numero de estados discretos escogidos')
#         plt.title('(Agt_i: ' + str(i) + '- Agt_j: ' + str(j) + '): Estados discretos seleccionados por VQ para cada (hora, fase)')
#         plt.show() 
