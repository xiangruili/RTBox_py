#!/usr/bin/env python
"""
Demo code to show how to measure the delay of real light onset from win.flip().

This will show a flash square at the center of the screen and you will need to
attach the light sensor to the flash, so the RTBox can detect the light signal.

The delay can be used to calibrate the absolute RT for a study. For CRT, it is
normally about half of the flip interval, ~8 ms at 60Hz refresh rate. But it 
could be one or more frames longer for LCD etc.

My LCD panel gives: In millisecond, median_offset = 10.4; std = 0.039; N = 10

By Xiangrui Li (xiangrui.li at gmail.com)
20170324 wrote it
"""
from psychopy import visual, event, core
import numpy as np

# Next line can be removed if you add your RTBox.py folder to PYTHONPATH
#import sys; sys.path.append('my_RTBox.py_folder')
import RTBox

box = RTBox.RTBox() # open RTBox, return instance 'box' for later access
box.disable('all') # avoid other events
box.enable('light') # enable light detection

# create full screen. Black background is used to aoid to trigger light
win = visual.Window(fullscr=True, color=(-1, -1, -1), allowGUI=False)

# make the light patch at screen center
loc = ((-0.1, -0.05), (0.1, -0.05), (0.1, 0.05), (-0.1, 0.05))
stim = visual.ShapeStim(win, fillColor='white', vertices=loc)

nTrial = 10
instr = visual.TextStim(win, pos=(0.0, 0.7), height=0.05, text= 
            ('Attach the light sensor to the patch\n'
             'and secure it with a piece of tape.\n\n'
             'Press spacebar to start.'))
instr.draw()
stim.draw()
win.flip() # show instruction

event.waitKeys(maxWait=999, keyList=['space']) # wait for spacebar

win.flip() # turn off instruction

rt = np.repeat(np.nan, nTrial) # allocate time with nan

for i in range(nTrial):
    core.wait(0.2) # no random, this "subject" won't cheat :)
    stim.draw()
    box.clear() # clear buffer, and enable light detection
    t0 = win.flip() # light on, and get nominal onset time
    win.flip() # light off after 1 frame. The "subject" has a sharp eye!

    (secs, _) = box.secs() # read "response" by light: real onset time
    if len(secs): rt[i] = secs[0]-t0 # the "subject" never misses a trial :)

rt *= 1000
rst = (np.median(rt), np.std(rt), nTrial)
print('In millisecond, median_offset = %.3g; std = %.2g; N = %g' % rst)

box.close()
win.close()
core.quit()
