import numpy as np
import itertools 
import math 
import pickle
import matplotlib.pyplot as plt
from multiprocessing import Pool, freeze_support
from scipy import stats
import csv
#from sklearn.model_selection import train_test_split
#from sklearn.linear_model import LinearRegression
#from sklearn.metrics import r2_score,mean_squared_error
#import pandas as pd

#GAME PARAMETERS
AUTO_INNER_GOAL_PTS = 6
TELE_INNER_GOAL_PTS = 3
AUTO_OUTER_GOAL_PTS = 4
TELE_OUTER_GOAL_PTS = 2

HPS_TO_NEAR_TRENCH = 20
HPS_TO_FAR_TRENCH = 34
HPS_TO_INIT_LINE = 40
HPS_TO_GOAL = 50

TELE_TIME = 135

#SIM PARAMETERS
ACC_REF_ST_DEV = np.arange(6., 16., 1) #At init line

class ShootPosition():
    def __init__(self, name, inner_size, outer_size, distance_from_HPS):
        self.name = name
        self.innerSize = inner_size
        self.outerSize = outer_size
        self.HPSdist = distance_from_HPS

SHOOT_POSITION = [ShootPosition('init line', 6, 15, HPS_TO_INIT_LINE),
                  ShootPosition('against goal', 2, 36, HPS_TO_GOAL),
                  ShootPosition('far trench', 10, 24, HPS_TO_FAR_TRENCH),
                  ShootPosition('near trench', 4, 10, HPS_TO_NEAR_TRENCH)
                  ]
                  
AUTO_SHOOT_POS = [ShootPosition('init line', 6, 15, HPS_TO_INIT_LINE),
                  ShootPosition('against goal', 2, 36, HPS_TO_GOAL)
                  ]

LOCKON_TIME = 1
SHOOT_RATE = np.arange(0.2, 1, 0.2) #Seconds per ball
DRIVE_SPEED = np.arange(8, 13, 1) #Feet per second

HPS_LOAD_TIME = np.arange(2, 5, 0.5)

DEFENSE_IMPACT = np.arange(0.3, 1, 0.1)

AUTO_ADDL_BALLS = [0, 1, 3, 5]

CLIMB_TIME = np.arange(4, 10, 1)

class ParamSet():
    def __init__(self, acc_st_dev, shoot_position, auto_shoot_position, shoot_rate, drive_speed, load_time, defense_impact, auto_addl_balls, climb_time):
        self.accStDev = acc_st_dev
        self.shootPosition = shoot_position
        self.autoShootPos = auto_shoot_position
        self.shootRate = shoot_rate
        self.driveSpeed = drive_speed
        self.loadTime = load_time
        self.defenseImpact = defense_impact
        self.autoAddlBalls = auto_addl_balls
        self.climbTime = climb_time
    
def compute(run):
    #Compute auto score 
    auto_total_balls = 3 + run.autoAddlBalls
    run.autoInnerBalls = int(auto_total_balls * math.erf(( run.autoShootPos.innerSize/run.accStDev)/ math.sqrt(2)))
    run.autoOuterBalls = int(auto_total_balls * math.erf(( run.autoShootPos.outerSize/run.accStDev)/ math.sqrt(2))) - run.autoInnerBalls
    
    run.autoScore = (run.autoInnerBalls * AUTO_INNER_GOAL_PTS) + (run.autoOuterBalls * AUTO_OUTER_GOAL_PTS)
    
    effectiveSpeed = run.driveSpeed * run.defenseImpact
    time_to_hps = HPS_TO_INIT_LINE / effectiveSpeed
    time_to_shootpos = run.shootPosition.HPSdist / effectiveSpeed
    shoot_time = 5 * run.shootRate
 
    first_cycle_time = time_to_hps + run.loadTime + time_to_shootpos + LOCKON_TIME + shoot_time
    run.cycle_time = cycle_time = time_to_shootpos + run.loadTime + time_to_shootpos + LOCKON_TIME + shoot_time
    time_to_cycle = TELE_TIME - (first_cycle_time + run.climbTime)

    run.cycles = int(time_to_cycle / cycle_time) + 1
    
    run.teleBalls = run.cycles * 5
    run.teleInnerBalls = int(run.teleBalls * math.erf(( run.shootPosition.innerSize/run.accStDev)/ math.sqrt(2)))
    run.teleOuterBalls = int(run.teleBalls * math.erf(( run.shootPosition.outerSize/run.accStDev)/ math.sqrt(2))) - run.teleInnerBalls
    #print run.teleInnerBalls, run.teleOuterBalls
    run.teleScore = (run.teleInnerBalls * TELE_INNER_GOAL_PTS) + (run.teleOuterBalls * TELE_OUTER_GOAL_PTS)
    
    run.totalScore = run.autoScore + run.teleScore
    
    #print run.totalScore
    return run
    
if __name__ == "__main__":
    freeze_support()
    
    params = [ACC_REF_ST_DEV, SHOOT_POSITION, AUTO_SHOOT_POS, SHOOT_RATE, DRIVE_SPEED, HPS_LOAD_TIME, DEFENSE_IMPACT, AUTO_ADDL_BALLS, CLIMB_TIME]
    print params
    paramSetVars = list(itertools.product(*params))

    paramSets = []

    for ps in paramSetVars:
        paramSets.append(ParamSet(ps[0], ps[1], ps[2], ps[3], ps[4], ps[5], ps[6], ps[7], ps[8]))

    print "%d permutations"%len(paramSets)
    p = Pool(8)

    results = p.map(compute, paramSets)
    print "Done!"
    #for r in results[:1000]:
    #    print r.accStDev, r.totalScore, r.autoInnerBalls, r.autoOuterBalls, r.teleInnerBalls, r.teleOuterBalls
    #plt.hist([x.totalScore for x in results], 30)

    xs = [x.accStDev for x in results]
    ys = [x.totalScore for x in results]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
    print "Accuracy:", slope, r_value**2

    xs = [x.driveSpeed for x in results]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
    print "Drive speed:", slope, r_value**2

    xs = [x.autoAddlBalls for x in results]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
    print "Auto intake balls:", slope, r_value**2

    xs = [x.shootRate for x in results]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
    print "Shoot Rate:", slope, r_value**2

    xs = [x.loadTime for x in results]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
    print "Loading time:", slope, r_value**2
    #heatmap, xedges, yedges = np.histogram2d(xs, ys, bins=50)
    #extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    #plt.imshow(heatmap.T, extent=extent, origin='lower')
    #plt.show()

    with open("D:\\FRC\\FRC2020\\FRC2020\\Simulation\\results.csv", 'w') as csvfile:
        csvw = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvw.writerow(['Accuracy', 'ShootPos', 'AutoShootPos', 'ShootRate', 'DriveSpeed', 'LoadTime', 'DefenseImpact', 'AutoAddlBalls', 'ClimbTime', 'AutoInner', 'AutoOuter', 'TeleInner', 'TeleOuter', 'TotalScore'])
        for i, r in enumerate(results):
            if i%10000 == 0:
                print "Writing line %d"%i
            csvw.writerow([r.accStDev, r.shootPosition.name, r.autoShootPos.name, r.shootRate, r.driveSpeed, r.loadTime, r.defenseImpact, r.autoAddlBalls, r.climbTime, r.autoInnerBalls, r.autoOuterBalls, r.teleInnerBalls, r.teleOuterBalls, r.totalScore])
