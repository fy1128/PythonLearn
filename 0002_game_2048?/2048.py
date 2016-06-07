#!/usr/bin/env python

import sys
import evdev
import os
import time
import random

NumberArray = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

KeyValue = evdev.InputDevice('/dev/input/event0')

KeyDict = {	evdev.ecodes.KEY_UP:[0,-1],
			evdev.ecodes.KEY_DOWN:[0,1],
			evdev.ecodes.KEY_LEFT:[-1,0],
			evdev.ecodes.KEY_RIGHT:[1,0]}

def ClrScreen():
	os.system('clear')
	#KeyValue.write(evdev.ecodes.EV_KEY,evdev.ecodes.KEY_LEFTCTRL,1)
	#KeyValue.write(evdev.ecodes.EV_KEY,evdev.ecodes.KEY_L,1)
	#KeyValue.write(evdev.ecodes.EV_KEY,evdev.ecodes.KEY_L,0)
	#KeyValue.write(evdev.ecodes.EV_KEY,evdev.ecodes.KEY_LEFTCTRL,0)
	pass
	
def Draw(offset = [0,0]):
	lr = 2 + offset[0]
	ud = 2 * (2 + offset[1])
	lr *= '\t'
	ud *= '\n'
	ClrScreen()
	sys.stdout.write(ud)
	for i in range(4):
		sys.stdout.write(lr + '+-------+-------+-------+-------+\n')
		sys.stdout.write(lr + '|\t|\t|\t|\t|\n' + lr)
		for j in range(4):
			if NumberArray[i][j] :
				sys.stdout.write('|' + str(NumberArray[i][j]) + '\t')
			else :
				sys.stdout.write('|' + '\t')
		sys.stdout.write('|\n' + lr + '|\t|\t|\t|\t|\n')
	sys.stdout.write(lr + '+-------+-------+-------+-------+\n')
	sys.stdout.write(ud)

def ReDraw(KeyDictVal = [0,0]):
	Draw(KeyDictVal)
	time.sleep(0.1)
	Draw()

def GenRandomNumber():
	x = 4 if random.randint(0,9) >= 8 else 2
	# find empty cage
	cate = []
	for xx in range(0,4):
		for yy in range(0,4):
			if 0 == NumberArray[xx][yy]:
				cate.append((xx,yy))
	if 0 == len(cate):
		return -1
	xx,yy = cate[random.randint(0,len(cate) - 1)]
	NumberArray[xx][yy] = x

def MergerNumber():
	#OK i'm lazy....
	for xx in range(0,4):
		lastval = 0
		yy = 1
		while yy < 4:
			if 0 == NumberArray[xx][yy]:
				yy += 1
			elif NumberArray[xx][lastval] == NumberArray[xx][yy]:
				NumberArray[xx][lastval] *= 2
				NumberArray[xx][yy] = 0
				yy = 1
				lastval = 0
				continue
			else:
				yy += 1
				lastval += 1
		zero = 0
		yy = 1
		while yy < 4:
			if 0 != NumberArray[xx][zero]:
				zero += 1
			yy += 1
		for yy in range(1,4):
			if 0 == NumberArray[xx][nonzero]:
				NumberArray[xx][nonzero],NumberArray[xx][yy] = NumberArray[xx][yy],NumberArray[xx][nonzero]
			elif NumberArray[xx][nonzero] == NumberArray[xx][yy] :
				NumberArray[xx][yy] = 0
				NumberArray[xx][nonzero] *= 2
			else:
				nonzero += 1
				
			
if __name__ == '__main__' :
	
	GenRandomNumber()
	ReDraw()
	for InputKey in KeyValue.read_loop():
		if (InputKey.type == evdev.ecodes.EV_KEY) and (0 == InputKey.value):
			# we wait for key up
			#print evdev.categorize(InputKey)
			KeyDictVal = KeyDict.get(InputKey.code,[0,0])
			if [0,0] != KeyDictVal :
				# valid key input
				MergerNumber()
				GenRandomNumber()
				ReDraw(KeyDictVal)
			pass
	print 'Game Over'