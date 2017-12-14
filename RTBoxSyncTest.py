#from RTBoxSyncTest import RTBoxSyncTest; RTBoxSyncTest(interval=1.0, n=30)
import RTBox
import time
import numpy as np
from threading import Timer

def show(t):
    """Plot the result if matplotlib available, print result otherwise"""
    n = t.shape[0]
    t[:,0] = (t[:,0] - np.mean(t[:,0])) * 1000 # ms
    t[:,1] -= t[0,1]
    c = np.polyfit(t[:,1], t[:,0], 1)
    r = t[:,0] - (t[:,1]*c[0] + c[1]) # residual
    se = np.sqrt(sum(r**2)/(n-2)) / (np.std(t[:,1]) * np.sqrt(n-1))
    rst = 'Variation range: %.2g | %.2g ms \n(before | after removing drift)' \
                  % (np.ptp(t[:,0]), np.ptp(r))
    if abs(c[0]/se)>10: rst += '\nRecommend to run clockRatio()'
    print(rst.replace('\n', '. '))
    try:
        import matplotlib.pyplot as plt
        plt.plot(t[:,1], t[:,0], 'b.', t[:,1], r, 'r+')
        plt.ylim((-1, 1))
        plt.xlabel('Seconds')
        plt.ylabel('Clock diff variation (ms)')
        plt.text(t.shape[0]/10, 0.6, rst)
        plt.show()
    except: pass
    
def RTBoxSyncTest(interval=1.0, n=30):
    """Measure host and RTBox clock difference at interval for n times"""

    def timer_func():
        t[i[0],:] = box.clockDiff()[:2] # update one row
        i[0] += 1
        if i[0]<n: Timer(interval, timer_func).start()
        else: show(t)
    
    i = [0] # trick to avoid global
    interval = interval-0.02 # run time 20 ms
    box = RTBox.RTBox()
    t = np.zeros((n, 2)) # store result
    
    print('RTBoxSyncTest at background will finish at ' +
          time.ctime(time.time()+interval*n))
    timer_func()

if __name__ == '__main__': RTBoxSyncTest()
