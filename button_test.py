from button import *

while True: 
	button = Button(25)
	button = Button(25, debounce=1.0)
	z = button.is_pressed()
	if z == True:
		print(z,"Emergency Call is needed")
