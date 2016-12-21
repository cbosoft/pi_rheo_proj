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
	sample_time = 0
	
	def __init__(self, KP_, KI_, KD_):
		if (KP_ == 0):
			P_On = False
		else:
			P_On = True
			KP = KP_
		
		if (KI_ == 0):
			I_On = False
		else:
			I_On = True
			KI = KI_
		
		if (KD_ == 0):
			D_On = False
		else:
			D_On = True
			KD = KD_
	
	def shift_arrs():
		temp = ca[1]
		ca[1] = ca[2]
		ca[0] = temp
		temp = e[1]
		e[1] = e[2]
		e[0] = temp
	
	def get_control_action(self, u_val):
		# Control action is a function of the k parameters, the previous control actions, the previous errors, and the sample time
		
		# Get actual time between samples (will vary, use an average?)
		if (time_of_last == 0):
			time_of_last = lambda: int(round(time.time() * 1000))
			sample_time = 0.1
		else:
			sample_time = time_of_last - (lambda: int(round(time.time() * 1000)))
			time_of_last = lambda: int(round(time.time() * 1000))
		
		# move stored values down
		shift_arrs()
		e[2] = set_point - u_val
		ca[2] = ca[1] + KP * (e[2] - e[1]) + KI * sample_time * e[2]
		return ca[2]