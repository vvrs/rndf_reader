#!/usr/bin/env python

import numpy as np

resol = 100

def length(a,b,c,d):
	return np.sqrt((b-a)**2+(d-c)**2)

#http://paulbourke.net/geometry/pointlineplane/
def distancePointLine(point,lineStart,lineEnd):
	lineMagn = np.linalg.norm(lineStart-lineEnd)
	u = (((point[0]-lineStart[0])*(lineEnd[0]-lineStart[0]))+\
		((point[1]-lineStart[1])*(lineEnd[1]-lineStart[1])))/\
		(lineMagn*lineMagn)
	x=lineStart[0]+u*(lineEnd[0]-lineStart[0]);
	y=lineStart[1]+u*(lineEnd[1]-lineStart[1]);
	newp = np.array([x,y])
	return np.linalg.norm(newp-point)

def generateK(cps,maxdeviation,maxcurvature):

	K = 0.1
	octe = 0
	ocurv = 'Inf'
	while(abs(K-1.)>0.001):
		cp1,cp2 = generate_cps(cps[0],cps[1],cps[2],cps[3],K)
		Bx,By = generate_curve(cps[1],cp1,cp2,cps[2])
		Bdx,Bdy = b_dot(cps[1],cp1,cp2,cps[2])
		Bddx,Bddy = b_ddot(cps[1],cp1,cp2,cps[2])
		cte = []
		curv = []
		for i in range(len(Bx)):
			ls = np.array(cps[1])
			le = np.array(cps[2])
			point = np.array([Bx[i],By[i]])
			pcte = distancePointLine(point,ls,le)
			pcurv = abs(((Bdx[i]*Bddy[i] - Bdy[i]*Bddx[i]))/(((Bdx[i]**2)+(Bdy[i]**2))**(3./2.)))
			curv.append(pcurv)
			cte.append(pcte)
		octe = max(cte)
		ocurv = max(curv)
		if(max(curv)>maxcurvature):
			K+=0.01
		else:
			return K,max(cte),max(curv)
	return K,octe,ocurv


def generate_cps(p1,p2,p3,p4,K):
	x0 = p1[0]
	y0 = p1[1]
	x1 = p2[0]
	y1 = p2[1]
	x2 = p3[0]
	y2 = p3[1]
	x3 = p4[0]
	y3 = p4[1]

	xc1 = (x0+x1)/2.0
	yc1 = (y0+y1)/2.0
	xc2 = (x1+x2)/2.0
	yc2 = (y1+y2)/2.0
	xc3 = (x2+x3)/2.0
	yc3 = (y2+y3)/2.0

	len1 = length(x0,x1,y0,y1)
	len2 = length(x1,x2,y1,y2)
	len3 = length(x2,x3,y2,y3)

	k1 = len1/(len1+len2)
	k2 = len2/(len2+len3)

	# K=0.1

	xm1 = xc1+(xc2-xc1)*k1
	ym1 = yc1+(yc2-yc1)*k1

	xm2 = xc2+(xc3-xc2)*k2
	ym2 = yc2+(yc3-yc2)*k2

	ctrl1_x = xm1+(xc2-xm1)*K + x1 - xm1
	ctrl1_y = ym1+(yc2-ym1)*K + y1 - ym1

	ctrl2_x = xm2+(xc2-xm2)*K + x2 - xm2
	ctrl2_y = ym2+(yc2-ym2)*K + y2 - ym2

	cp1 = [ctrl1_x,ctrl1_y]
	cp2 = [ctrl2_x,ctrl2_y]

	return cp1,cp2



def generate_curve(p1,p2,p3,p4):
	global resol
	t = np.linspace(0,1,resol)
	Bx = (1-t)**3*p1[0] + 3*(1-t)**2*t*p2[0] + 3*(1-t)*t**2*p3[0] + t**3*p4[0]
	By = (1-t)**3*p1[1] + 3*(1-t)**2*t*p2[1] + 3*(1-t)*t**2*p3[1] + t**3*p4[1]
	
	return Bx,By

def generate_segments(wp,maxdeviation,maxcurvature):#K):
	# def generate_segments(wp):#K):
	n = np.shape(wp)[0]
	segments = {}
	# print wp,"inside generate segments function\n\n\n"
	for i in range(n-2):
		# print [wp[i,0],wp[i,1]]
		if i==0:
			# print 'first segment'
			p1 = [wp[i,0],wp[i,1]]
			p2 = [wp[i,0],wp[i,1]]
			p3 = [wp[i+1,0],wp[i+1,1]]
			p4 = [wp[i+2,0],wp[i+2,1]]
		else:
			p1 = [wp[i-1,0],wp[i-1,1]]
			p2 = [wp[i,0],wp[i,1]]
			p3 = [wp[i+1,0],wp[i+1,1]]
			p4 = [wp[i+2,0],wp[i+2,1]]
		k,a,b = generateK([p1,p2,p3,p4],maxdeviation,maxcurvature) #uncomment for new
		# print k,a,b
		cp1,cp2 = generate_cps(p1,p2,p3,p4,k)
		segments[i]= [p2,cp1,cp2,p3]

	p1=[wp[-3,0],wp[-3,1]]
	p2=[wp[-2,0],wp[-2,1]]
	p3=[wp[-1,0],wp[-1,1]]
	p4=[wp[-1,0],wp[-1,1]]
	k,a,b = generateK([p1,p2,p3,p4],maxdeviation,maxcurvature)
	# print k,a,b
	cp1,cp2 = generate_cps(p1,p2,p3,p4,k)
	segments[n-2]= [p2,cp1,cp2,p3]
	return segments

def b_dot(p1,p2,p3,p4):

	t=np.linspace(0,1,resol)

	Bdx = (1-t)**2*3*(p2[0]-p1[0]) + 2*(1-t)*t*3*(p3[0]-p2[0]) + t**2*3*(p4[0]-p3[0])
	Bdy = (1-t)**2*3*(p2[1]-p1[1]) + 2*(1-t)*t*3*(p3[1]-p2[1]) + t**2*3*(p4[1]-p3[1])

	return Bdx,Bdy

def b_ddot(p1,p2,p3,p4):

	t=np.linspace(0,1,resol)

	Bdx = 6*(1-t)*p1[0]+3*(-4+6*t)*p2[0]+3*(2-6*t)*p3[0]+6*t*p4[0]
	Bdy = 6*(1-t)*p1[1]+3*(-4+6*t)*p2[1]+3*(2-6*t)*p3[1]+6*t*p4[1]
	return Bdx,Bdy

def interpolate_points(p1,p2,mindist=15):
	d = np.linalg.norm(p1-p2)
	pp = np.floor(d/mindist)
	ip = np.zeros((int(pp+2),2))
	for i in range(1,int(pp)+1):
		dt = (i*mindist)
		t = dt/d
		ip[i,:] = ((1-t)*p1+ t*p2)
	ip[0,:] = p1
	ip[-1,:]= p2
	return ip

def interpolate_multi(a,md=15):
	b = np.zeros((1,2))
	b[0,:] = a[0,:]
	for i in range(np.shape(a)[0]-1):
	    b=np.insert(b,np.shape(b)[0],interpolate_points(a[i,:],a[i+1,:],mindist=md)[1:],axis=0)
	return b