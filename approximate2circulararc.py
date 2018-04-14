#!/usr/bin/env python

'''
	This script is to approximate a circular arc to a bezier curve

	Input:
		- waypoint ids
		- left turn (0) or right turn (1)
		- two points (P1,P2) on the circle in counter-clock wise 
			(Location of the waypoints between which the circular arc is being fit)
		- center of the circle (C)
		(Angle between CP1,CP2 should not exceed 180. In this case split the arc)
	Output:
		- Control points written in a text file
'''

import numpy as np 
import matplotlib.pyplot as plt 
from math import *
from bezier_interpolation_def import *



#https://math.stackexchange.com/questions/873224/calculate-control-points-of-cubic-bezier-curve-approximating-a-part-of-a-circle
def rotateP(a):
	b = np.array([-1*a[1],a[0]])
	return b

def bezierControlPoints(p1,p4,c):

	p1 = np.array(p1)
	p4 = np.array(p4)
	c = np.array(c)
	r = np.linalg.norm(p1-c)
	angle = acos(np.dot((p1-c),(p4-c))/(r**2))
	alpha = (4./3.)*tan(angle/4.)
	p2 = p1+alpha*(rotateP(p1-c))
	p3 = p4-alpha*(rotateP(p4-c))

	return p2,p3

#----------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':

	plt.axis('equal')

	ncps = open("newcps2.txt",'a')
	waypoints = raw_input("Enter waypoints:: ")
	right = input("Left turn or right turn \n ( 0: left \t 1: Right )\t:: ")
	p1 = raw_input("P1::  ")
	p1 = [float(p1.split(",")[0]),float(p1.split(",")[1])]

	p4 = raw_input("P4::  ")
	p4 = [float(p4.split(",")[0]),float(p4.split(",")[1])]


	center = raw_input("center::  ")
	center = [float(center.split(",")[0]),float(center.split(",")[1])]

	p2,p3 = bezierControlPoints(p1,p4,center)
	p2 = [round(p2[0],3),round(p2[1],3)]
	p3 = [round(p3[0],3),round(p3[1],3)]
	if(right):
		ncps.write(str(waypoints)+"|"+str(p4)+"|"+str(p3)+"|"+str(p2)+"|"+str(p1)+"|\n")
	else:
		ncps.write(str(waypoints)+"|"+str(p1)+"|"+str(p2)+"|"+str(p3)+"|"+str(p4)+"|\n")
	Bx,By = generate_curve(p1,p2,p3,p4)

	# plot to verify the generated bezier curve
	plt.plot(Bx,By)
	plt.show()
	ncps.close()