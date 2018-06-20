from button import *

while True: 
	button = Button(25)
	button = Button(25, debounce=1.0)
	buttonPress = button.is_pressed()
	if buttonPress == True:
		buttonStatus = [buttonPress, "Emergency Call is needed"]
		print "Status:", buttonStatus[0],", MSG:", buttonStatus[1]
