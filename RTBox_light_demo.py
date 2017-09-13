#!/usr/bin/env python
"""
Demo code for RTBox using light trigger.

This will show a flash with black background, and a flash at at right side of 
the screen. You will need to attach the light sensor to the flash at the 
right side, so the RTBox can detect the light signal.

We could set RTBox to detect two signals each trial, the light trigger
indicating the onset of signal, and the subject button response.
    box.nEventsRead(2) # read function will expect 2 events, default is 1
Then we identify the light and button events and do a subtraction to get RT.
But if a trigger is used to indicate the onset, there is a much easier way:
    (secs, btns) = box.light(2) # wait 2 secs, and get RT directly
Here we need to keep the default box.nEventsRead() as 1, and returned 'secs'
is the time relative to light trigger. The light event and its time are not 
returned anymore. Since we don't need convert boxSecs to hostSecs here, we 
use box.clear(0) so it can run faster by skipping clock sync.

Compared to regular method in which we get light onset time by
    win.flip(); tOnset = box.hostSecs()
the advantage of using light sensor include:
 (1) we don't rely on clock sync so potentially have higher accuracy.
 (2) it takes care of the offset between win.flip() and real onset. This
     offet is about half of the flip interval if the stimulus is at vertical
     center of the screen. In case this offset is not stable for a setup,
     the light sensor is likely the only accurate solution.
The possible disadvantage include:
 (1) we need extra hardware (light sensor) connection and need to program a
     trigger, a light patch at the same vertical location as the stimulus. 
 (2) the light patch could distract the subject.

The recommended solution is to use the light patch to verify that the offset
between win.flip() and real onset is stable, and use the offset to corect
the RT if one cares about the absolute RT. RTBox_cal_demo.py shows how to do 
this.

By Xiangrui Li (xiangrui.li at gmail.com)
20170317 wrote it
"""
from psychopy import visual, event, core
import numpy as np

# Next line can be removed if you add your RTBox.py folder to PYTHONPATH
#import sys; sys.path.append('my_RTBox.py_folder')
import RTBox

box = RTBox.RTBox() # open RTBox, return instance 'box' for later access

"""
Unlike button events, detection of all other triggers will be disabled
by a trigger itself. This means each time we enable light detection,
we can get only one light trigger. We don't need to enable it again
explicitly, since box.clear() in the trial loop will enable it.
"""
box.enable('light') # enable light detection

# create full screen. Black background is used to aoid to trigger light
win = visual.Window(fullscr=True, color=(-1, -1, -1), allowGUI=False)

# make the trigger at right side, and the stim at center
loc = ((0.8, -0.05), (1, -0.05), (1, 0.05), (0.8, 0.05))
trig = visual.ShapeStim(win, fillColor='white', vertices=loc) # at right center
loc = ((-0.1, -0.13), (0.1, -0.13), (0.1, 0.13), (-0.1, 0.13))
stim = visual.ShapeStim(win, fillColor='white', vertices=loc) # at center

nTrial = 10
instr = visual.TextStim(win, height=0.1, text= 
            ('Task: press a button as soon as you see the white square.\n\n'
             'We will do ' + str(nTrial) +' trials.\n\n'
             'Get ready and press spacebar to start.'))
instr.draw()
trig.draw()
win.flip() # show instruction and trigger for you to attach the sensor

event.waitKeys(maxWait=999, keyList=['space']) # wait for spacebar

win.flip() # turn off instruction

rt = np.repeat(np.nan, nTrial) # allocate response time with nan

for i in range(nTrial):
    core.wait(1.0+np.random.ranf()*2) # random interval of 1 to 3 secs
    trig.draw()
    stim.draw()

    box.clear(0) # clear buffer, and enable light trigger. No clock sync needed
    
    win.flip() # both stim and trigger on
    
    stim.draw()
    win.flip() # only stim stays
    
    if event.getKeys(['esc', 'escape']): break # allow esc to stop

    core.wait(0.1) # extra time for stim to stay
    win.flip() # stim off

    (secs, btns) = box.light(2) # wait up to 2 s, secs relative to light
    if len(secs): rt[i] = secs[0] # record RT only there is response
    
rst = (np.nanmedian(rt), np.nanstd(rt), nTrial-sum(np.isnan(rt)))
print('median_RT = %.2g; std = %.2g; N = %g' % rst)

box.close()
win.close()
core.quit()
