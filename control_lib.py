# Imports
import time

class PIDcontroller:
	KP = 0
	KI = 0
	KD = 0
	P_On = False
	I_On = False
	D_On = False
	
	set_point = 0
	
	ca = [0,0,0]
	e = [0,0,0]
	
	time_of_last = 0
	sample_time = 0.1
	
	def __init__(self, KP_, KI_, KD_, sample_time_):
		self.sample_time  sample_time_;
		if (KP_ == 0):
			self.P_On = False
		else:
			self.P_On = True
			self.KP = KP_
		
		if (KI_ == 0):
			self.I_On = False
		else:
			self.I_On = True
			self.KI = KI_
		
		if (KD_ == 0):
			self.D_On = False
		else:
			self.D_On = True
			self.KD = KD_
	
	def shift_arrs(self):
		temp = self.ca[1]
		self.ca[1] = self.ca[2]
		self.ca[0] = temp
		temp = self.e[1]
		self.e[1] = self.e[2]
		self.e[0] = temp
	
	def get_control_action(self, u_val):
		# Control action is a function of the k parameters, the previous control actions, the previous errors, and the sample time
		
		# Get actual time between samples (will vary, use an average?)
		if (self.time_of_last == 0):
			self.time_of_last = int(round(time.time()))
			self.sample_time = 0.1 #rough initial sample time
		else:
			self.sample_time = int(round(time.time())) - time_of_last #set sample time to actual time between samples
			self.time_of_last = int(round(time.time()))
		
		# move stored values down, making space for next set
		self.shift_arrs()
		
		#get new error
		self.e[2] = self.set_point - u_val
		
		#use velocity discrete time algorithm to obtain the required control action
		self.ca[2] = self.ca[1] + self.KP * (self.e[2] - self.e[1]) + self.KI * self.sample_time * self.e[2] + (self.KD / self.sample_time) * (self.e[2] - (2 * self.e[1]) + self.e[0])
		return self.ca[2]
		
		
		
		
		
		
		
		
		
		
		
		
		