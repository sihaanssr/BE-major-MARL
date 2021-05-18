'''
Created on 21/09/2016

@author: ubuntu
'''
import var
execfile("./var.py")
import arrivalRateGen
execfile("./arrivalRateGen.py")
import fun
execfile("./fun.py")
import train2_RL
execfile("./train2_RL.py")
import test2_RL
execfile("./test2_RL.py")

#=========== DISCRETIZE SPACE STATE FOR EACH AGENT
arrivalRateGen.createPolyFlow()
fun.learnDiscretization(var.totalDaysObs)
fun.writeDataClusters()

#=========== TRAINING PROCESS
print('---------- Training --------------')
#train2_RL.train()

#=========== TESTING PROCESS
print('---------- Testing ---------------')
test2_RL.test(var.totalDaysTrain)

print('--- End Simulation ---')
