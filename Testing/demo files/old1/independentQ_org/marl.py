'''
Created on 21/09/2016

@author: ubuntu
'''
import var
exec(compile(open("./var.py").read(), "./var.py", 'exec'))
import arrivalRateGen
exec(compile(open("./arrivalRateGen.py").read(), "./arrivalRateGen.py", 'exec'))
#import fun
#exec(compile(open("./fun.py").read(), "./fun.py", 'exec'))
#import train2_RL
#exec(compile(open("./train2_RL.py").read(), "./train2_RL.py", 'exec'))
import test2_RL
exec(compile(open("./test2_RL.py").read(), "./test2_RL.py", 'exec'))

#=========== DISCRETIZE SPACE STATE FOR EACH AGENT
arrivalRateGen.createPolyFlow()
#fun.learnDiscretization(var.totalDaysObs)
# fun.writeDataClusters()

#=========== TRAINING PROCESS
#print('---------- Training --------------')
# train2_RL.train()

#=========== TESTING PROCESS
print('---------- Testing ---------------')
test2_RL.test(var.totalDaysTrain)

print('--- End Simulation ---')
