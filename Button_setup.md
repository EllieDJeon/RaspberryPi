# Installation  
To install the library on your Raspberry Pi, enter the following commands in LX Terminal.

For Python 3 use:
```
$ git clone https://github.com/simonmonk/squid.git
$ cd squid
$ sudo python3 setup.py install
$ pico button_test.py

```


```
from button import *
while True: 
        button = Button(25)
        button = Button(25, debounce=1.0)
        z = button.is_pressed()
        if z == True:
                print(z,"Emergency Call is needed")
```
