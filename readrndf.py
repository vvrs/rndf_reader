#/usr/bin/env python

'''
	This script has classes defined to read RNDF file. These classes segregate the different
	sections in order for the other scripts to have access to the data, and create waypoints 
	dictionary and Adjacency list.

	Usage:

		Create an instance of the class 'waypointsDict' and call the method 'dict()'
		to create a dictionary of all the waypoints (waypoint ids as keys and locations as values)
		
		Ex:
			wpd = waypointsDict('example.rndf')
			wpDict = wpd.dict()

		Here, we are following the top-bottom approach to read an RNDF file.

		'segmentsDict' breaks the file and stores the information as a dictionary where segment id 
		is the key and the information of the lanes is the value

		Ex:
			sd = segmentDict('example.rndf')
			sDict = sd.dict()

		'rndfSegments' class reads info that we get from segment dictionary. This class provides access 
		to the information of the segment such as segment name, segment id, and number of lanes present
		in the segment. Also, it has method to break the segment information and generate a dictionary
		which stores lane information mapped to lane serial number

		Ex:
			rndfSeg = rndfSegments(segmentInfo) # get segmentInfo from the above dictionary 'sDict'
			segName = rndfSeg.name
			segID   = rndfSeg.segment_id
			segNumLanes = rndfSeg.num_lanes
			segLanes = rndfSeg.laneDict()

		'rndfLanes' class takes information from the rndfSegments class and gives access to the lane id, 
		lane width, boundary information and also creates the list of exit points, stop points, waypoints 
		dictionary.

		Ex:
			rndfLan = rndfLanes() 
			laneId = rndfLan.laneId
			numWaypoints = rndfLan.numWaypoints
			laneWidth = rndfLan.laneWidth
			leftBoundary = rndfLan.leftBoundary
			rightBoundary = rndfLan.rightBoundary
			checkPoints = rndfLan.checkPoints
			stopPoints = rndfLan.stopPoints
			exitPoints  = rndfLan.exitPoints 
			waypointDict = rndfLan.waypointDict
'''

import re
from collections import OrderedDict
import StringIO
import time
from bezier_interpolation_def import *
from random import *

class waypointsDict:
	def __init__(self,file):
		self.f = open(file)
		self.ff = self.f.readlines()
		self.waypoints_dict = OrderedDict()

	def dict(self):
		pattern  = r"^\d*\.\d*\d.\d*" #pattern for SegmentNum.LaneNum.WaypointNum
		for i in range(len(self.ff)):
			match = re.search(pattern,self.ff[i])
			if(match):
				t = self.ff[i].split()
				self.waypoints_dict[(t[0])] = [float(t[1]),float(t[2])]
		return self.waypoints_dict

class segmentsDict:
	def __init__(self,file):
		self.f = open(file)
		self.fr = self.f.read()
		self.f = open(file)
		self.ff = self.f.readlines()
		self.num_segments = None
		# self.ff = self.f.readlines()
		self.segments_dict = OrderedDict()

	def dict(self):
		for i in range(len(self.ff)):
			if(re.match('num_segment',self.ff[i])):
				self.num_segments = int(self.ff[i].split()[1])
		for i in range(1,self.num_segments+1):	
			pattern  = r"(?s)(segment\s"+str(i)+").*?(end_segment)" #pattern for SegmentNum.LaneNum.WaypointNum
			match = re.search(pattern,self.fr)
			self.segments_dict[i] = match.group()
		return self.segments_dict


class rndfSegments:
	def __init__(self,text):
		self.text = text
		self.ff = StringIO.StringIO(self.text)
		self.ff = self.ff.readlines()
		self.name = None
		self.num_lanes = None
		self.segment_id = None
		self.lane_dict = OrderedDict()
	def info(self):
		for i in range(len(self.ff)):
			if(re.match('^segment\s',self.ff[i])):
				self.segment_id = int(self.ff[i].split()[1])
			if(re.match('num_lanes',self.ff[i])):
				self.num_lanes = int(self.ff[i].split()[1])
			if(re.match('segment_name',self.ff[i])):
				self.name = self.ff[i].split()[1]
			if(re.match('lane\s',self.ff[i])):
				break
	def print_info(self):
		print self.name,self.segment_id,self.num_lanes

	def laneDict(self):
		for i in range(1,self.num_lanes+1):	
			pattern  = r"(?s)(lane\s"+str(self.segment_id)+"."+str(i)+").*?(end_lane)" #pattern for SegmentNum.LaneNum.WaypointNum
			match = re.search(pattern,self.text)
			self.lane_dict[i] = match.group()
		return self.lane_dict

class rndfLanes:
	def __init__(self,text):
		self.text = text
		self.ff = StringIO.StringIO(self.text)
		self.ff = self.ff.readlines()
		self.laneId = None
		self.numWaypoints = None
		self.laneWidth = None
		self.leftBoundary = None
		self.rightBoundary = None
		self.checkPoints = []
		self.stopPoints = []
		self.exitPoints = []
		self.waypointDict = OrderedDict()
	def info(self):
		for i in range(len(self.ff)):
			wpPattern = r"^\d*\.\d*\d.\d*" 
			cl = self.ff[i]
			t = cl.split()
			if(re.match(wpPattern,cl)):
				self.waypointDict[(t[0])] = [float(t[1]),float(t[2]),self.laneWidth]
			if(re.match('^lane\s',cl)):
				self.laneId = t[1]
			if(re.match('^num_waypoints',cl)):
				self.numWaypoints = int(t[1])
			if(re.match('^lane_width',cl)):
				self.laneWidth = int(t[1])
			if(re.match('^left_boundary',cl)):
				self.leftBoundary = t[1]
			if(re.match('^right_boundary',cl)):
				self.rightBoundary = t[1]
			if(re.match('^stop',cl)):
				self.stopPoints.append(t[1])
			if(re.match('^checkpoint',cl)):
				self.checkPoints.append([t[1],t[2]])
			if(re.match('^exit',cl)):
				self.exitPoints.append([t[1],t[2]])