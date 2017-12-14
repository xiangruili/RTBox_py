#!/usr/bin/env python
import RTBox
    
def RTBoxFirmwareUpdate(hexFileName=None):
    """ Update RTBox firmware from a hex file. """
        
    def cleanup(err=None):
        """close serial port and raise error if applicable"""
        ser.write(b'R') # return to application
        box.close()
        if err!=None: raise ValueError(err)

    def checkerr(task):
        """ check returned '\r' from bootloader, raise error if not"""
        b = ser.read(1)
        if len(b)<1 or ord(b)!=13: cleanup(' Failed to ' + task)

    if hexFileName==None: # file diaglog if no hex file input
        try:
            import tkinter as tk
            from tkinter import filedialog
        except:
            import Tkinter as tk
            import tkFileDialog as filedialog
            
        root = tk.Tk(); root.withdraw()
        hexFileName = filedialog.askopenfilename(title='Select HEX file', 
                                    filetypes=[('hex files', '.hex')])
    if len(hexFileName)<1: return
    
    print(' Checking HEX file ...')
    with open(hexFileName) as fid: s = fid.read().strip().splitlines()
    
    for ln in s: # find 1st data line
        if ln[7:9]=='00': break
    adr = [int(ln[3:5], 16), int(ln[5:7], 16)]
    i0 = adr[0]<<8 + adr[1] # start address
    
    for ln in s[::-1]: # find last data line
        if ln[7:9]=='00': break
    nByte = int(ln[1:3], 16) + (int(ln[3:5], 16)<<8) + int(ln[5:7], 16) - i0
    
    bytePL = 16 # bytes of each write
    nPage = (nByte+bytePL-1) // bytePL
    C = bytearray([255]) * (nPage*bytePL) # initialize with 0xff
    for ln in s:
        if ln[7:9]!='00': continue # not data line, skip
        b = [int(ln[i:i+2],16) for i in range(1,len(ln),2)]
        if -sum(b[:-1]) % 256 != b[-1]:
            raise ValueError('Checksum error at line %g. HEX file corrupted.' % i)
        i1 = b[1]*256 + b[2] - i0 # start address for the line
        C[i1:i1+b[0]] = b[4:-1] # data
        
    try: ind = C.index(b'USTCRTBOX')
    except: ValueError('Not valid RTBox hex file')
    v = float(C[ind+18:ind+21])
    if v>100: v = v/100
    
    C = [C[i*bytePL:(i+1)*bytePL] for i in range(nPage)] # pages
    
    box = RTBox.RTBox()
    ser = box._ser
    ser.timeout = 1.0
    try: ser.setTimeouts(1.0)
    except: ser.timeout = 1.0
    
    if int(v) != int(box._p.version): # major version different
        try:
            import tkinter as tk
            from tkinter import messagebox
        except:
            import Tkinter as tk
            import tkMessageBox as messagebox
            
        root = tk.Tk(); root.withdraw()
        yn = messagebox.askquestion('Version Warning',
           'Hardware and firmware may not be compatible.\n' + 
           'Are you sure you want to continue?', default='no')
        if yn=='no': cleanup(); return
        
    ser.write(b'xBS')
    idn = bytearray(ser.read(7))
    if idn != b'AVRBOOT': cleanup('Failed to enter boot loader.')
    
    # now we are in AVRBOOT, ready to upload firmware HEX
    ser.write(b'Tt') # set device type
    checkerr('set device type')
    print(' Erasing flash ...')
    ser.write(b'e') # erase
    checkerr('erase flash');
    
    ser.write(bytearray([65, adr[0], adr[1]])) # 'A' normally 0x0000
    checkerr('set address')
    
    print(' Writing flash ...')
    cmd = bytearray([66, 0, bytePL, 70]) # cmd high/low bytes, Flash
    for i in range(nPage):
        ser.write(cmd)
        ser.write(C[i]) # write a page
        checkerr('write flash page ' + str(i))
    
    ser.write(bytearray([65, adr[0], adr[1]])) # verify
    checkerr('set address')
    
    print(' Verifying flash ...');
    cmd = bytearray([103, 0, bytePL, 70]) # 'g' cmd high/low bytes, Flash
    for i in range(nPage):
        ser.write(cmd)
        ln = bytearray(ser.read(bytePL)) # read a page back
        if len(ln)<bytePL or ln!=C[i]:
            cleanup(' Failed to verify page '+str(i) +'. Please try again.')
    print(' All done successfully')
    cleanup()

if __name__ == '__main__': # not execute when imported
    import sys
    file = None if len(sys.argv)<2 else sys.argv[1]
    RTBoxFirmwareUpdate(file)
