'''
Created on 9/10/2016

@author: carolina
'''
import os, sys
import subprocess
#sys.path.append("/Users/CarolinaHiguera/Programas/sumo-0.27.1/tools")
#sys.path.append("/home/carolina/Programas/sumo-0.27.1/tools")

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(tools)
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
sumoBinary = "sumo-gui" #sumo-gui
sumoCmd = [sumoBinary, "-c", "../miniCity/miniCity.sumo.cfg", "--no-step-log", "true"]

import random
import pandas as pd
import numpy as np
import math
import os

import var
import arrivalRateGen

FIFO = '/tmp/sumo_tf'

#arrivalRateGen.createPolyFlow()

#Inicio prueba TF
inYellow = False
secInYellow = 0


for day in range(5):
    fileOut = open("days.csv","w")
    fileOut.write(str(day)+"\n")
    fileOut.close()
        
    print(("Testing day: "+str(day)))
    arrivalRateGen.writeRoutes(day+1)
    projectName = var.project + ".sumocfg"

    #sumoProcess = subprocess.Popen(['/home/carolina/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
    #        "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
    #traci.init(var.PORT)
    traci.start(sumoCmd)
    
    dfRewVals = {}
    dfQueueTracker = {}
    dfWaitingTracker = {}
    dfC02Emission = {}
    dfFuelConsumption = {}
    dfNOxEmission = {}
    dfNoiseEmission = {}
    dfSpeed = {}
    dfActions = pd.DataFrame()
    
    for v in var.Vertex:        
        dfRewVals[v] = pd.DataFrame()
        dfQueueTracker[v] = pd.DataFrame()
        dfWaitingTracker[v] = pd.DataFrame() 
        dfC02Emission[v] = pd.DataFrame()
        dfFuelConsumption[v] = pd.DataFrame()
        dfNOxEmission[v] = pd.DataFrame()
        dfNoiseEmission[v] = pd.DataFrame()
        dfSpeed[v] = pd.DataFrame() 
    
    currHod = 0
    currSod = 0
    
    while currSod < var.secondsInDay: 
        if currHod != currSod/var.secondsInHour:
            currHod = int(currSod/var.secondsInHour)
            print('    testing day = ', day)
            print('    hour = ', currHod)
               
        
        #============== IS TIME TO MAKE A COLLECTIVE DECISION?
        if(currSod%(var.minTimeInYellow + var.minTimeInGreen) == 0): 
            #=========== UPDATE INFORMATION OF ALL VERTEX AGENTS
            for v in var.Vertex:
                #================= count halted vehicles (4 elements)
                for lane in var.vertexAgents[v].listLanes:
                    var.vertexAgents[v].laneQueueTracker[lane] = traci.lane.getLastStepHaltingNumber(str(lane))
                idx = 0
                for edge in var.vertexAgents[v].listEdges:
                    var.vertexAgents[v].queueTracker[edge] = 0
                    for lane in range(var.vertexAgents[v].numberLanes[idx]):
                        var.vertexAgents[v].queueTracker[edge] += var.vertexAgents[v].laneQueueTracker[str(edge) + '_' + str(lane)]
                    idx += 1
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:
                    aux.append(var.vertexAgents[v].queueTracker[edge])
                df = pd.DataFrame([aux])
                dfQueueTracker[v] = dfQueueTracker[v].append(df, ignore_index=True) 
                #print(dfQueueTracker[v])
                                    
                # ================ cum waiting time in minutes
                for lane in var.vertexAgents[v].listLanes:
                    var.vertexAgents[v].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60
                idx = 0;
                for edge in var.vertexAgents[v].listEdges:
                    var.vertexAgents[v].waitingTracker[edge] = 0
                    for lane in range(var.vertexAgents[v].numberLanes[idx]):
                        var.vertexAgents[v].waitingTracker[edge] += var.vertexAgents[v].laneWaitingTracker[str(edge) + '_' + str(lane)]
                    idx += 1 
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:
                    aux.append(var.vertexAgents[v].waitingTracker[edge])
                df = pd.DataFrame([aux])
                dfWaitingTracker[v] = dfWaitingTracker[v].append(df, ignore_index=True)
                print(dfWaitingTracker[v].to_string())
                # ================ C02 emmissions in mg
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:
                    aux.append(traci.edge.getCO2Emission(str(edge)))
                df = pd.DataFrame([aux])
                dfC02Emission[v] = dfC02Emission[v].append(df, ignore_index=True)
                
                # ================ NOx emmissions in mg
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:                        
                    aux.append(traci.edge.getNOxEmission(str(edge)))
                df = pd.DataFrame([aux])
                dfNOxEmission[v] = dfNOxEmission[v].append(df, ignore_index=True)
                
                # ================ fuel consumption in ml 
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:                        
                    aux.append(traci.edge.getFuelConsumption(str(edge)))
                df = pd.DataFrame([aux])
                dfFuelConsumption[v] = dfFuelConsumption[v].append(df, ignore_index=True)
                
                # ================ noise emission in db 
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:                        
                    aux.append(traci.edge.getNoiseEmission(str(edge)))
                df = pd.DataFrame([aux])
                dfNoiseEmission[v] = dfNoiseEmission[v].append(df, ignore_index=True)

                # ================ speed in m/s
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:                        
                    aux.append(traci.edge.getLastStepMeanSpeed(str(edge)))
                df = pd.DataFrame([aux])
                dfSpeed[v] = dfSpeed[v].append(df, ignore_index=True)
            
                #Update reward of each vertex agent and save its information
                var.vertexAgents[v].updateReward()
                df = pd.DataFrame([[currSod, var.vertexAgents[v].currReward]])
                dfRewVals[v] = dfRewVals[v].append(df, ignore_index=True)
            
                            
            #Save sequence of actions taken by vertex agents
            aux = [currSod]
            for v in var.Vertex:
                aux.append(int(traci.trafficlights.getPhase(str(v))))
            df = pd.DataFrame([aux])
            dfActions = dfActions.append(df, ignore_index=True)            
            
        print('enviando datos')
        fifo = open(FIFO, 'w')
        dfQueueTracker[v].tail(1).to_string(fifo)
        # fifo.write('hello\n')
        fifo.close()

        print('datos enviados')

        fifo = open(FIFO, 'r')
        fifo.read()
        fifo.close()

        print('dar step')

        currSod += 1
        traci.simulationStep() 
    traci.close() #End on day of simulation
    
    if(day==0):
        dfRewValsSummaryMaster = {} 
        for v in var.Vertex:
            dfRewValsSummaryMaster[v] = {} 
    
            
    #Save actions for each vertex agent
    aux = ['hour']
    for v in var.Vertex:
        aux.append('int' + str(var.vertexAgents[v].SL))
    dfActions.columns = aux
    dfActions['hour'] = dfActions['hour']/(1.0*var.secondsInHour)
    #dfActions.to_csv('dfActions_testTF_day'+str(day)+'.csv')
    
    #Save reward information for each vertex agent
    for v in var.Vertex:
        dfRewVals[v].columns = ['hour', 'day ' + str(day)]
        dfRewVals[v]['hour'] = dfRewVals[v]['hour']/(1.0*var.secondsInHour)
        #dfRewVals[v].to_csv('dfRewVals_testTF_int'+str(v)+'_day'+str(day)+'.csv')
        
        dfMean = dfRewVals[v].mean(axis=0)
        dfMedian = dfRewVals[v].median(axis = 0)
        dfMin = dfRewVals[v].min(axis=0)
        df = pd.DataFrame([[str(day), dfMean[1], dfMedian[1], dfMin[1]]])
        df.columns = ['day', 'mean', 'median', 'min']
        
        if day == 0:
            dfRewValsSummaryMaster[v] = df
        else:
            dfRewValsSummaryMaster[v] = dfRewValsSummaryMaster[v].append(df, ignore_index=True)    
            dfRewValsSummaryMaster[v].columns = ['day', 'mean', 'median', 'min']            
        #dfRewValsSummaryMaster[v].to_csv('dfRewValsSummary_testTF_int' + str(v) + '.csv')
    
    #Save traffic information for each vertex Agent
    for v in var.Vertex:
        colNames = ['hour']
        for edge in var.vertexAgents[v].listEdges:
            colNames.append(edge)
        
        dfQueueTracker[v].columns = colNames
        dfQueueTracker[v]['hour'] = dfQueueTracker[v]['hour']/(1.0*var.secondsInHour)
        #dfQueueTracker[v].to_csv('dfQueue_testTF_int' + str(v) + '_day' + str(day) + '.csv')
        
        dfWaitingTracker[v].columns = colNames
        dfWaitingTracker[v]['hour'] = dfWaitingTracker[v]['hour']/(1.0*var.secondsInHour)
        #dfWaitingTracker[v].to_csv('dfWaiting_testTF_int' + str(v) + '_day' + str(day) + '.csv')
    
        dfC02Emission[v].columns = colNames
        dfC02Emission[v]['hour'] = dfC02Emission[v]['hour']/(1.0*var.secondsInHour)
        #dfC02Emission[v].to_csv('dfC02Emission_testTF_int' + str(v) + '_day' + str(day) + '.csv')
        
        dfNOxEmission[v].columns = colNames
        dfNOxEmission[v]['hour'] = dfNOxEmission[v]['hour']/(1.0*var.secondsInHour)
        #dfNOxEmission[v].to_csv('dfNOxEmission_testTF_int' + str(v) + '_day' + str(day) + '.csv')
        
        dfFuelConsumption[v].columns = colNames
        dfFuelConsumption[v]['hour'] = dfFuelConsumption[v]['hour']/(1.0*var.secondsInHour)
        #dfFuelConsumption[v].to_csv('dfFuelConsumption_testTF_int' + str(v) + '_day' + str(day) + '.csv')
        
        dfNoiseEmission[v].columns = colNames
        dfNoiseEmission[v]['hour'] = dfNoiseEmission[v]['hour']/(1.0*var.secondsInHour)
        #dfNoiseEmission[v].to_csv('dfNoiseEmission_testTF_int' + str(v) + '_day' + str(day) + '.csv')
    
        dfSpeed[v].columns = colNames
        dfSpeed[v]['hour'] = dfSpeed[v]['hour']/(1.0*var.secondsInHour)
        dfSpeed[v].to_csv('dfSpeed_testTF_int' + str(v) + '_day' + str(day) + '.csv')
    
    fileOut = open("days.csv","w")
    fileOut.write("End Testing")
    fileOut.close()
