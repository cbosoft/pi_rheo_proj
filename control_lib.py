#
# Controller class. Provides support for controling a process using python.
# Simply gets a control action based upon a set point and an input value.
# 
# Uses the valocity discrete time algorithm for control action.
#
# To be implemented in the future:
#	# Continuous time algorithm
#	# Auto tuning

# Imports
from time import time

class PIDcontroller(object):
	KP = 0													# Proportional Gain	
	KI = 0													# Integral Gain
	KD = 0													# Derivative Gain
	P_On = False
	I_On = False
	D_On = False
	
	set_point = 0											# Set point used to find the error
	
	ca = [0,0,0]											# three most recent values of the control action
	e = [0,0,0]												# three most recent values of the error
	
	time_of_last = 0										# time of last run, in seconds
	sample_time = 0.1										# time between runs, in seconds
	
	# class initialisation method
	def __init__(self, KP_, KI_, KD_, sample_time_):
		
		self.sample_time = sample_time_						# initial sample time
		
		if (KP_ == 0):										# if KP is zero, turn off proportional control
			self.P_On = False
		else:
			self.P_On = True
			self.KP = KP_
		
		if (KI_ == 0):										# if KI is zero, turn off integral control
			self.I_On = False
		else:
			self.I_On = True
			self.KI = KI_
		
		if (KD_ == 0):
			self.D_On = False								#if KD is zero, turn off derivative control
		else:
			self.D_On = True
			self.KD = KD_
	
	# simple method that moves values up in array
	def shift_arrs(self):
		temp = self.ca[1]
		self.ca[1] = self.ca[2]
		self.ca[0] = temp
		temp = self.e[1]
		self.e[1] = self.e[2]
		self.e[0] = temp
	
	# get required control action
	def get_control_action(self, u_val):
		# Control action is a function of the k parameters, the previous control actions, the previous errors, and the sample time
		
		# Get actual time between samples
		if (self.time_of_last == 0):
			self.time_of_last = time()
			self.sample_time = 0.1 							# rough initial sample time
		else:
			self.sample_time = time() - time_of_last 		# set sample time to actual time between samples
			self.time_of_last = time()
		
		self.shift_arrs()									# move stored values down, making space for next set
		
		self.e[2] = self.set_point - u_val					# get new error
		
		self.ca[2] = self.ca[1]								# use velocity discrete time algorithm to obtain the required control action
		
		if (self.P_On):
			self.ca[2] += self.KP * (self.e[2] - self.e[1])
		
		if (self.I_On):
			self.ca[2] += self.KI * self.sample_time * self.e[2]
		
		if (self.D_On):
			self.ca[2] += (self.KD / self.sample_time) * (self.e[2] - (2 * self.e[1]) + self.e[0])
		return self.ca[2]