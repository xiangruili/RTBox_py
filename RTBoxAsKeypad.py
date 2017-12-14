"""from RTBoxAsKeypad import RTBoxAsKeypad; kp = RTBoxAsKeypad()
RTBoxAsKeypad sets the RTBox as a keypad, so it can be used in the same way as a
keyboard. In Matlab or Python, it doesn't make much sense to use the RTBox this
way. But if one likes to use the RTBox hardware with other software toolkit,
this may be useful. Python has to leave open for this to work.
Note that, as a keypad, the hardware won't have any delay or bias as regular
keyboard will, but the system delay of key detection will apply to the timing.
170412 By Xiangrui Li (xiangrui.li at gmail.com) """

import RTBox
from time import sleep
from threading import Timer
from pynput.keyboard import Controller

class RTBoxAsKeypad:
    """ kp = RTBoxAsKeypad() # start it and leave python open
    kp.stop() # stop keypad after done, or quit python
    Open RTBox serial port and start to simulate key press. The optional input is
    the interval to check RTBox event. Most OS has interval of 8ms for keyboard
    event, so it won't help much to set this shorter than 8 ms."""
    def __init__(self, intvl=0.008):
        """ kp = RTBoxAsKeypad() # start it and leave python open """
        self.interval = intvl
        self.keys = ['1', '2', '3', '4', 'S', 'L', '5', 'A']
        self._kb = Controller() # make key press and release

        box = RTBox.RTBox(); box.close()
        self._ser = box._ser
        self._ser.open()
        self._ser.write(b'x') # simple mode: 1 byte per event
        self.enableTrigger()  
        self._timer_func()
       
    def start(self):
        """ Start to register keys after it is stopped. """
        if self._ser.is_open: return
        self._ser.open()
        self._timer_func()

    def stop(self):
        """ Close serial port to stop the key registration. """
        self._ser.close()

    def enableTrigger(self):
        """ Enable trigger after it is disabled by itself. The four triggers are 5,
        S, L and A for TR, sound, light and aux respectively"""
        self._ser.write(bytearray([101, 0b111101])) # e, all except release
        self._ser.read(1)

    def _timer_func(self):
        """ Worker function called by timer. """
        if not self._ser.is_open: return # stop timer
        try:    n = self._ser.bytesAvailable()
        except: n = self._ser.in_waiting

        for i in range(n):
            b = bin(ord(self._ser.read(1)))[::-1]
            if b.count('1')==1: # ignore if +1 bits set
                k = self.keys[b.find('1')]
                self._kb.press(k); sleep(0.04); self._kb.release(k)
            
        t = Timer(self.interval, self._timer_func)
        t.daemon = True # ensure timer stops when exit 
        t.start()
