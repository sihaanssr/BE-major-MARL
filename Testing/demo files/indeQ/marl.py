'''
Created on 21/09/2016

@author: ubuntu
'''
import var
exec(compile(open("./var.py", "rb").read(), "./var.py", 'exec'))
import arrivalRateGen
exec(compile(open("./arrivalRateGen.py", "rb").read(), "./arrivalRateGen.py", 'exec'))
#import fun
#exec(compile(open("./fun.py", "rb").read(), "./fun.py", 'exec'))
#import train2_RL
#exec(compile(open("./train2_RL.py", "rb").read(), "./train2_RL.py", 'exec'))
import test2_RL
exec(compile(open("./test2_RL.py", "rb").read(), "./test2_RL.py", 'exec'))

#=========== DISCRETIZE SPACE STATE FOR EACH AGENT
#arrivalRateGen.createPolyFlow()
#fun.learnDiscretization(var.totalDaysObs)
#fun.writeDataClusters()

#=========== TRAINING PROCESS
#print('---------- Training --------------')
#train2_RL.train()

#=========== TESTING PROCESS
print('---------- Testing ---------------')
test2_RL.test(var.totalDaysTrain)

print('--- End Simulation ---')
