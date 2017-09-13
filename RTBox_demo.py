#!/usr/bin/env python
"""
Demo code for RTBox.py.

This shows a drifting gabor, with orientation tilting from vertical to 
either 11 clock or 1 clock. The task is to answer the orientation.

By Xiangrui Li (xiangrui.li at gmail.com)
20170318 wrote it
"""
from psychopy import visual, event, core

# Next line can be removed if your RTBox.py folder is in PYTHONPATH
#import sys; sys.path.append('my_RTBox.py_folder');
import RTBox
np = RTBox.np # numpy

box = RTBox.RTBox() # open RTBox, return the instance for later access
#box = RTBox.RTBox(boxID='') # use left/right arrow key to simulate RTBox buttons
#box.hostClock(core.getTime) # set clock used for stimulus. No need with psychopy
box.buttonNames(['left', 'left', 'right', 'right']) # make 4 buttons as 2

# create a window to draw in
win = visual.Window([600, 600], allowGUI=False)
#fps = win.getActualFrameRate()

# make a gabor
gabor = visual.GratingStim(win, tex="sin", mask="gauss", texRes=256, 
           contrast=0.5, size=[1.0, 1.0], sf=[4, 0])

nTrial = 10
instr = visual.TextStim(win, height=0.08, text= 
            ('Task: press button 1 or 2 if the gabor tilts to 11 clock, '
             'and press button 3 or 4 if the gabor tilts to 1 clock.\n\n'
             'Respond as fast as you can.\n\n'
             'We will do ' + str(nTrial) +' trials.\n\n'
             'Get ready and press spacebar to start.'))
instr.draw()
t0 = win.flip() # show instruction
if abs(box.hostSecs()-t0) > 0.001: # make sure the same clock used
    win.close(); box.close()
    raise ValueError('RTBox using different clock from win.flip()')
# If this fails, the solution will be to ignore the timestamp by flip, but
# call t0 = box.hostSecs() immediately after flip in the trial loop.

box.waitKeys('space') # start by spacebar press by experimenter
#event.waitKeys(keyList=['space']) # wait for spacebar

win.flip() # turn off instruction

rSeed = np.random.RandomState(core.getAbsTime()) # record rand seed
tiltLeft = np.repeat(True, nTrial)
tiltLeft[:int(nTrial/2)] = False # set half False
np.random.shuffle(tiltLeft)

# pre-allocate result
ok = np.repeat(None, nTrial) # will stay as None for missed trials
rt = np.repeat(np.nan, nTrial)

for i in range(nTrial):
    core.wait(1.0+np.random.ranf()*2) # random interval of 1 to 3 secs
    
    gabor.ori = (0.5-tiltLeft[i]) * 30  # 15 deg tilt
    gabor.draw()
    box.clear() # run this right before stim onset of each trial
    
    # win.callOnFlip(box.TTL, 5) # send TTL after next flip(), or box.TTL(5) after flip()
    t0 = win.flip() # gabor on, and return onset time
    # box.TTL(5) # TTL for EEG event marker, run it following flip
    
    for iframe in range(9): # stim duration: 10 frames
        gabor.phase += 0.01
        gabor.draw()
        win.flip()

    win.flip() # gabor off
    
    if event.getKeys(['esc', 'escape']): break # stop if esc pressed
    
    (secs, btns) = box.secs(2.0) # read response, wait up to 2 secs
    if len(secs) < 1: continue # move to next trial if missed response
    rt[i] = secs[0] - t0 # record the RT of first button press
    ok[i] = tiltLeft[i]==(btns[0]=='left') # response correct?

#import pickle
#pickle.dump([rSeed, tiltLeft, rt, ok], open('myRst.pickle', 'w')) # Python3: 'wb'
#[rSeed, tiltLeft, rt, ok] = pickle.load(open('myRst.pickle', 'r')) # load
print('median_RT = %.2g; std = %.2g; N = %g' % 
       (np.nanmedian(rt), np.nanstd(rt), nTrial-sum(np.isnan(rt))))
print('correct = %g/%g; missed = %g/%g' % 
       (sum(np.equal(ok, True)), nTrial, sum(np.equal(ok, None)), nTrial))

box.close() # not strictly needed
win.close()
core.quit()
