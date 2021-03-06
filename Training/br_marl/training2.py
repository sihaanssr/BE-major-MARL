'''
Created on Nov 2018

@author: carolina

BR-MARL
'''

import os, sys
import subprocess
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:   
	sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
sumoBinary = "sumo" #sumo-gui
import random
import pandas as pd
import numpy as np
import math
import var
import gets
import time

dfRewVals = {}
dfQueueTracker = {}
dfWaitingTracker = {} 
dfActions = {}
dfEpsilon = {}
path = '~/Documents/BogotaRL/br_marl/csv_files_train_t1/'

def saveData(currSod):
	global dfQueueTracker, dfWaitingTracker, dfRewVals, dfActions, dfEpsilon
	row = round(currSod/var.sampleTime)
	#Queues and waiting times
	for j in var.junctions.keys():
		auxQ = [currSod]
		auxW = [currSod]
		for edge in range(0,len(var.junctions[j].edges)):
			junction = var.agent_TLS[var.junctions[j].tls].listJunctions.index(j)
			queue = var.agent_TLS[var.junctions[j].tls].queueEdgeTracker[junction][edge]
			waitTime = var.agent_TLS[var.junctions[j].tls].waitingEdgeTracker[junction][edge]
			auxQ.append(queue)
			auxW.append(waitTime)
		dfQueueTracker[j].loc[row] = np.array([auxQ])
		dfWaitingTracker[j].loc[row] = np.array([auxW])		
	#Rewards, actions and epsilon
	auxA = [currSod]
	auxE = [currSod]
	for tls in var.agent_TLS.keys():
		auxR = [currSod]            
		auxR.append(var.agent_TLS[tls].currReward)		
		auxA.append(var.agent_TLS[tls].currAction)
		auxE.append(var.agent_TLS[tls].epsilon)
		df = pd.DataFrame([auxR])
		dfRewVals[tls].loc[row] = np.array([auxR])
	dfActions.loc[row] = np.array([auxA]) 
	dfEpsilon.loc[row] = np.array([auxE])

def data2files(day):
	global dfQueueTracker, dfWaitingTracker, dfRewVals, dfActions, dfEpsilon, path
	#Save actions and epsilons in file
	aux = ['sec']
	for tls in var.agent_TLS.keys():
		aux.append(tls)
	dfActions.columns = aux
	dfEpsilon.columns = aux
	dfActions.to_csv(path + 'br_actions_day' + str(day) + '.csv')
	dfEpsilon.to_csv(path + 'br_epsilon_day' + str(day) + '.csv')
	
	#Save rewards in file
	aux = ['sec', 'rew1']
	for tls in var.agent_TLS.keys():
		dfRewVals[tls].columns = aux
		dfRewVals[tls].to_csv(path + 'br_rewards_' + str(tls) + '_day' + str(day) + '.csv')
	
	#Save queues and times for each junction
	for j in var.junctions.keys():
		aux = ['currSod']        
		for edge in var.junctions[j].edges:
			aux.append(edge)
		dfQueueTracker[j].columns = aux
		dfWaitingTracker[j].columns = aux
		dfQueueTracker[j].to_csv(path + 'br_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv')
		dfWaitingTracker[j].to_csv(path + 'br_times_' + var.junctions[j].name + '_day' + str(day) + '.csv')
		
	#Save learning for each agent
	for tls in var.agent_TLS.keys():
		var.agent_TLS[tls].saveLearning(day, path)


def debug_phase(tls, currSod):
	ryg_state = traci.trafficlight.getRedYellowGreenState(str(tls))
	p_index = var.agent_TLS[tls].phases.index(ryg_state)
	print('Sec: '+str(currSod) + '   Phase: '+str(ryg_state))


def ini_dataframes():
	global dfQueueTracker, dfWaitingTracker, dfRewVals, dfActions, dfEpsilon  
	dfRewVals = {}
	dfQueueTracker = {}
	dfWaitingTracker = {} 
	rows = round(var.secondsInDay/var.sampleTime)
	for j in var.junctions.keys():
		cols = len(var.junctions[j].edges) + 1
		dfQueueTracker[j] = pd.DataFrame(index=range(rows), columns=range(cols))
		dfWaitingTracker[j] = pd.DataFrame(index=range(rows), columns=range(cols))
	for tls in var.agent_TLS.keys():
		dfRewVals[tls] = pd.DataFrame(index=range(rows), columns=range(2))
	dfActions = pd.DataFrame(index=range(rows), columns=range(1+len(var.agent_TLS)))
	dfEpsilon = pd.DataFrame(index=range(rows), columns=range(1+len(var.agent_TLS)))



def br_marl_learning():  
	for tls in var.agent_TLS.keys():
		var.agent_TLS[tls].ini4learning(path)
			
	for day in range(var.start_episode, var.episodes):
		fileOut = open("days.csv","w")
		fileOut.write("Training day: "+str(day)+"\n")
		fileOut.close()
		
		sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
		traci.start(sumoCmd)     
		
		ini_dataframes()	
		for tls in var.agent_TLS.keys():
			var.agent_TLS[tls].set_first_action()
		
		#Begins simulation of 1 day           
		for currSod in range(0,var.secondsInDay):
			if(currSod == 0):  
				gets.getObservation()
				for tls in var.agent_TLS.keys():                    
					var.agent_TLS[tls].getJointState(currSod)
					var.agent_TLS[tls].getJointAction()
					traci.trafficlight.setRedYellowGreenState(tls, var.agent_TLS[tls].RedYellowGreenState)
			else:    
				#Sample the system

				gets.getObservation2(currSod)

				for tls in var.agent_TLS.keys():
					if var.agent_TLS[tls].finishPhase[1]:
						var.agent_TLS[tls].updateReward1()
						var.agent_TLS[tls].updateStateAction()
						var.agent_TLS[tls].learnPolicy(currSod)
						var.agent_TLS[tls].getAction(day, currSod)
				for tls in var.agent_TLS.keys():
					var.agent_TLS[tls].getJointAction()

			if (currSod%var.sampleTime == 0):
				saveData(currSod)
				
			for tls in var.agent_TLS.keys():
				var.agent_TLS[tls].setPhase(currSod)
				traci.trafficlight.setRedYellowGreenState(tls, var.agent_TLS[tls].RedYellowGreenState)

			traci.simulationStep()
			#debug_phase('tls_14_45', currSod)
			#time.sleep(3)				
				
		traci.close()
		#End simulation of 1 day
		
		data2files(day)
	#-----------------------------------------------------
	fileOut = open("days.csv","w")
	fileOut.write("End training \n")
	fileOut.close()
