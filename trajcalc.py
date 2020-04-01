import matplotlib.pyplot as plt
import numpy as np 
from math import *

class trajpoint():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class trajectory():
    timestep = 0.001
    g = 32.2 #ft/s^2
    mass = 0 #lbm
    Cd = 0
    rho = 0.0765 #lbm/ft^3
    Cm = 0
    D = 0.5
    
    def __init__(self, mass, launch_angle, launch_velocity, launch_omega=0):
        self.launch_angle = launch_angle
        self.launch_velocity = launch_velocity
        self.mass = mass
        self.points = []
        initialPoint = trajpoint(0, 0)
        initialPoint.t = 0
        initialPoint.vx = cos(radians(self.launch_angle))*self.launch_velocity
        initialPoint.vy = sin(radians(self.launch_angle))*self.launch_velocity
        initialPoint.v = sqrt(initialPoint.vx**2+initialPoint.vy**2)
        initialPoint.omega = launch_omega #In rad/s
        self.computeAccelerations(initialPoint)
        self.points.append(initialPoint)
    
    def computeAccelerations(self, pt):
        Fd = (self.Cd*self.rho*pi*(self.D/2)**2*pt.v**2)/2
        #Fm = self.S*pt.omega*pt.v
        Fm = (self.Cm*self.rho*pt.v**2)/2
        #print Fd, Fm
        pt.ax = (-Fd*(pt.vx/pt.v)-Fm*(pt.vy/pt.v))/self.mass
        pt.ay = (self.mass*-self.g-Fd*(pt.vy/pt.v)+Fm*(pt.vx/pt.v))/self.mass
        
    def compute(self):
        assert len(self.points) == 1
        previouspt = self.points[0]
        
        while True:
            newx = previouspt.x + previouspt.vx*self.timestep
            newy = previouspt.y + previouspt.vy*self.timestep
            newpt = trajpoint(newx, newy)
            newpt.t = previouspt.t + self.timestep
            newpt.vx = previouspt.vx + previouspt.ax*self.timestep
            newpt.vy = previouspt.vy +previouspt.ay * self.timestep
            newpt.v = sqrt(newpt.vx**2+newpt.vy**2)
            newpt.omega = previouspt.omega - (previouspt.omega*1*self.timestep)
            self.computeAccelerations(newpt)
            previouspt = newpt
            #print newpt. t, newpt.x, newpt.y, newpt.vx, newpt.vy, newpt.ax, newpt.ay
            self.points.append(newpt)
            if newpt.y < 0:
                break

idealtraj = trajectory(0.3, 25, 60)
idealtraj.compute()

dragtraj  = trajectory(0.3, 25, 60)
dragtraj.Cd = 0.4
dragtraj.D = 0.58
dragtraj.compute()

magtraj   = trajectory(0.3, 25, 60, 100)
magtraj.Cm = 0.08
magtraj.D = 0.58
magtraj.compute()

fulltraj  = trajectory(0.3, 25, 60, 100)
#print fulltraj
fulltraj.Cd = 0.4
fulltraj.Cm = 0.08
fulltraj.D = 0.58
fulltraj.compute()

#print [(pt.x, pt.y) for pt in idealtraj.points]
#print [(pt.x, pt.y) for pt in fulltraj.points]

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot([pt.x for pt in idealtraj.points], [pt.y for pt in idealtraj.points], c='k', label="Ideal")
ax.plot([pt.x for pt in dragtraj.points], [pt.y for pt in dragtraj.points], c='r', label="W/ Drag")
ax.plot([pt.x for pt in magtraj.points], [pt.y for pt in magtraj.points], c='b', label="W/ Magnus")
ax.plot([pt.x for pt in fulltraj.points], [pt.y for pt in fulltraj.points], c='g', label="Full")
ax.set_aspect(1)
ax.legend(loc="upper left")
plt.show()