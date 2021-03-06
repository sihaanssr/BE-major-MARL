'''
Created on 8/09/2016

@author: ubuntuHiguera
'''
import os, sys
import subprocess
#sys.path.append("/Users/ubuntuHiguera/Programas/sumo-0.27.1/tools")
sys.path.append("/home/ubuntu/Programas/sumo-0.27.1/tools")
import traci
import random
import pandas as pd
import numpy as np
import math

import var
import arrivalRateGen

def test(dayLoad):
    inYellow = False
    secInYellow = 0
    dynamic = 1;
    for sl in var.SLs:
        var.agents[sl].loadKnowledge(dayLoad-1)
    
    for day in range(var.totalDaysTest):
        print("Testing day: "+str(day))
        arrivalRateGen.writeRoutes(day+1)
        projectName = var.project + ".sumocfg"
#         sumoProcess = subprocess.Popen(['/Users/ubuntuHiguera/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
#                 "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
        sumoProcess = subprocess.Popen(['/home/ubuntu/Programas/sumo-0.27.1/bin/sumo-gui', "-c", projectName, \
                "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
        traci.init(var.PORT)
        
        dfRewVals = {}
        dfQueueTracker = {}
        dfWaitingTracker = {}
        dfC02Emission = {}
        dfFuelConsumption = {}
        dfNOxEmission = {}
        dfNoiseEmission = {}
        dfActions = pd.DataFrame()
        
        for sl in var.SLs:        
            dfRewVals[sl] = pd.DataFrame()
            dfQueueTracker[sl] = pd.DataFrame()
            dfWaitingTracker[sl] = pd.DataFrame() 
            dfC02Emission[sl] = pd.DataFrame()
            dfFuelConsumption[sl] = pd.DataFrame()
            dfNOxEmission[sl] = pd.DataFrame()
            dfNoiseEmission[sl] = pd.DataFrame()
        
        currHod = 0
        currSod = 0
        
        while currSod < var.secondsInDay: 
            if currHod != currSod/var.secondsInHour:
                currHod = int(currSod/var.secondsInHour)
                print '    testing day = ', day
                print '    hour = ', currHod
            
            if(inYellow): #Check duration of yellow phase
                secInYellow += 1
                if(secInYellow >= var.minTimeInYellow):
                    secInYellow = 0
                    inYellow = False
                    for sl in var.SLs:
                        if(var.agents[sl].currPhaseID != var.agents[sl].newPhaseID):
                            traci.trafficlights.setPhase(str(sl),var.agents[sl].newPhaseID)                            
                            var.agents[sl].currPhaseID = var.agents[sl].newPhaseID
            
            #============== IS TIME TO MAKE A DECISION FOR SOME AGENT?
            if(currSod%var.minTimeInGreen == 0): #if min time in green is over
                
                #=========== UPDATE INFORMATION OF ALL AGENTS
                for sl in var.SLs:
                    #================= count halted vehicles (4 elements)
                    for lane in var.agents[sl].listLanes:
                        var.agents[sl].laneQueueTracker[lane] = traci.lane.getLastStepHaltingNumber(str(lane))
                    idx = 0
                    for edge in var.agents[sl].listEdges:
                        var.agents[sl].queueTracker[edge] = 0
                        for lane in range(var.agents[sl].numberLanes[idx]):
                            var.agents[sl].queueTracker[edge] += var.agents[sl].laneQueueTracker[str(edge) + '_' + str(lane)]
                        idx += 1
                    aux = [currSod]
                    for edge in var.agents[sl].listEdges:
                        aux.append(var.agents[sl].queueTracker[edge])
                    df = pd.DataFrame([aux])
                    dfQueueTracker[sl] = dfQueueTracker[sl].append(df, ignore_index=True) 
                    
                    
                    # ================ cum waiting time in minutes
                    for lane in var.agents[sl].listLanes:
                        var.agents[sl].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60
                    idx = 0;
                    for edge in var.agents[sl].listEdges:
                        var.agents[sl].waitingTracker[edge] = 0
                        for lane in range(var.agents[sl].numberLanes[idx]):
                            var.agents[sl].waitingTracker[edge] += var.agents[sl].laneWaitingTracker[str(edge) + '_' + str(lane)]
                        idx += 1 
                    aux = [currSod]
                    for edge in var.agents[sl].listEdges:
                        aux.append(var.agents[sl].waitingTracker[edge])
                    df = pd.DataFrame([aux])
                    dfWaitingTracker[sl] = dfWaitingTracker[sl].append(df, ignore_index=True)
                    
                    
                    # ================ C02 emmissions in mg
                    aux = [currSod]
                    for edge in var.agents[sl].listEdges:                        
                        aux.append(traci.edge.getCO2Emission(str(edge)))
                    df = pd.DataFrame([aux])
                    dfC02Emission[sl] = dfC02Emission[sl].append(df, ignore_index=True)
                    
                    # ================ NOx emmissions in mg
                    aux = [currSod]
                    for edge in var.agents[sl].listEdges:                        
                        aux.append(traci.edge.getNOxEmission(str(edge)))
                    df = pd.DataFrame([aux])
                    dfNOxEmission[sl] = dfNOxEmission[sl].append(df, ignore_index=True)
                    
                    # ================ fuel consumption in ml 
                    aux = [currSod]
                    for edge in var.agents[sl].listEdges:                        
                        aux.append(traci.edge.getFuelConsumption(str(edge)))
                    df = pd.DataFrame([aux])
                    dfFuelConsumption[sl] = dfFuelConsumption[sl].append(df, ignore_index=True)
                    
                    # ================ noise emission in db 
                    aux = [currSod]
                    for edge in var.agents[sl].listEdges:                        
                        aux.append(traci.edge.getNoiseEmission(str(edge)))
                    df = pd.DataFrame([aux])
                    dfNoiseEmission[sl] = dfNoiseEmission[sl].append(df, ignore_index=True)
                
                    #Update reward of each agent and save its information
                    var.agents[sl].updateReward()
                    df = pd.DataFrame([[currSod, var.agents[sl].currReward]])
                    dfRewVals[sl] = dfRewVals[sl].append(df, ignore_index=True)
                    
                #=========== APPLY LEARNING FOR EACH AGENTS
                for sl in var.SLs:
                    var.agents[sl].followPolicy(currHod)
                #update joint actions
                for sl in var.SLs:
                    var.agents[sl].updateJointAaction()
                
                #Save sequence of actions taken by  agents
                aux = [currSod]
                for sl in var.SLs:
                    aux.append(var.agents[sl].newPhaseID)
                    df = pd.DataFrame([aux])
                dfActions = dfActions.append(df, ignore_index=True)                             
                
                #=========== APPLY NEW PHASES
                for sl in var.SLs:
                    if(var.agents[sl].currPhaseID == var.agents[sl].newPhaseID): #extend current phase
                        traci.trafficlights.setPhase(str(sl),var.agents[sl].newPhaseID)
                        #traci.trafficlights.setPhaseDuration(str(sl), var.minTimeInGreen)
                    else: #change to new phase
                        currPhase = var.agents[sl].actionPhases.index(var.agents[sl].currPhaseID)
                        newPhase = var.agents[sl].actionPhases.index(var.agents[sl].newPhaseID)
                        auxPhase = var.agents[sl].auxPhases[currPhase][newPhase]
                        traci.trafficlights.setPhase(str(sl), auxPhase)
                        #traci.trafficlights.setPhaseDuration(str(sl), var.minTimeInYellow)
                        inYellow = True
                        
            currSod += 1
            traci.simulationStep() 
        traci.close() #End on day of simulation
        
        if(day==0):
            dfRewValsSummaryMaster = {} 
            for sl in var.SLs:
                dfRewValsSummaryMaster[sl] = {}   
        
        #Save actions for each  agent
        aux = ['hour']
        for sl in var.SLs:
            aux.append('agt' + str(sl))
        dfActions.columns = aux
        dfActions['hour'] = dfActions['hour']/(1.0*var.secondsInHour)
        dfActions.to_csv('dfActions_test_day'+str(day)+'.csv')
        
        #Save reward information for each  agent
        for sl in var.SLs:
            dfRewVals[sl].columns = ['hour', 'day ' + str(day)]
            dfRewVals[sl]['hour'] = dfRewVals[sl]['hour']/(1.0*var.secondsInHour)
            dfRewVals[sl].to_csv('dfRewVals_test_agt'+str(sl)+'_day'+str(day)+'.csv')
            
            dfMean = dfRewVals[sl].mean(axis=0)
            dfMedian = dfRewVals[sl].median(axis = 0)
            dfMin = dfRewVals[sl].min(axis=0)
            df = pd.DataFrame([[str(day), dfMean[1], dfMedian[1], dfMin[1]]])
            df.columns = ['day', 'mean', 'median', 'min']
            
            if day == 0:
                dfRewValsSummaryMaster[sl] = df
            else:
                dfRewValsSummaryMaster[sl] = dfRewValsSummaryMaster[sl].append(df, ignore_index=True)    
                dfRewValsSummaryMaster[sl].columns = ['day', 'mean', 'median', 'min']            
            dfRewValsSummaryMaster[sl].to_csv('dfRewValsSummary_test_agt' + str(sl) + '.csv')
        
        #Save traffic information for each Agent
        for sl in var.SLs:
            colNames = ['hour']
            for edge in var.agents[sl].listEdges:
                colNames.append(edge)
                
            dfQueueTracker[sl].columns = colNames
            dfQueueTracker[sl]['hour'] = dfQueueTracker[sl]['hour']/(1.0*var.secondsInHour)
            dfQueueTracker[sl].to_csv('dfQueue_test_agt' + str(sl) + '_day' + str(day) + '.csv')
            
            dfWaitingTracker[sl].columns = colNames
            dfWaitingTracker[sl]['hour'] = dfWaitingTracker[sl]['hour']/(1.0*var.secondsInHour)
            dfWaitingTracker[sl].to_csv('dfWaiting_test_agt' + str(sl) + '_day' + str(day) + '.csv')
            
            dfC02Emission[sl].columns = colNames
            dfC02Emission[sl]['hour'] = dfC02Emission[sl]['hour']/(1.0*var.secondsInHour)
            dfC02Emission[sl].to_csv('dfCO2Emissions_test_agt' + str(sl) + '_day' + str(day) + '.csv')
            
            dfNOxEmission[sl].columns = colNames
            dfNOxEmission[sl]['hour'] = dfNOxEmission[sl]['hour']/(1.0*var.secondsInHour)
            dfNOxEmission[sl].to_csv('dfNOxEmissions_test_agt' + str(sl) + '_day' + str(day) + '.csv')
        
            dfFuelConsumption[sl].columns = colNames
            dfFuelConsumption[sl]['hour'] = dfFuelConsumption[sl]['hour']/(1.0*var.secondsInHour)
            dfFuelConsumption[sl].to_csv('dfFuelConsumption_test_agt' + str(sl) + '_day' + str(day) + '.csv')
            
            dfNoiseEmission[sl].columns = colNames
            dfNoiseEmission[sl]['hour'] = dfNoiseEmission[sl]['hour']/(1.0*var.secondsInHour)
            dfNoiseEmission[sl].to_csv('dfNoiseEmission_test_agt' + str(sl) + '_day' + str(day) + '.csv')
                
