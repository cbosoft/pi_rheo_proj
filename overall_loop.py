#
# Master program
# Uses the other libraries to control the experiment and record the data

# Imports
import sys
sys.path.insert(0, "lib")
import adc
import control
import motor

# def loop:
	# if time snce last iteration >= control sample time:
		# get motor speed
		# get motor control action (delta speed)
		# apply new motor speed
	# get pend value
	# get camera frame #!! only if this is fast enough, I don't know how quick the rest of the script will be!!#
	# record time, motor speed, pend value