# When you do not need to use EPICS,
# install PIPython (pip install pipython)
# https://github.com/PI-PhysikInstrumente/PIPython
# KLS?
# KSD CSname X 80 Y ... : define CSname coordinate system.
# KLN CS1 CS2: set CS2 to be a parent of CS1
# KEN CSname: enable CSname
import time
from .decode import decode_KET, decode_KLT, decode_ONT
from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt
import threading

IP = '164.54.122.87'
BASEPV = "12idHXP"
WaveGenID = {"X": 1, "Y": 2, "Z":3, "U": 4, "V": 5, "W": 6}
# WaveGenID for this hexapod is defined as below:
#   1 ~ 8. 1 for X, 2 for Y, 3 for Z, 4 for U, 5 for V, and 6 for W. 7 and 8 are not defined.
# This axis definition can be changed on PIMikroMove software. Look for the wavevegenerator.
class WAV_Exception(Exception):
    pass

def plot_record(data, axis='X'):
    '''Plot results from get_records'''
    if isinstance(data, type({})):
        l_data = [data]
    else:
        l_data = data
    for data in l_data:
        ndata = data[axis][0].size
        plt.plot(range(0, ndata), (data[axis][1]-data[axis][0])*1000000)
        
    plt.ylabel('Real - Target (nm)')
    plt.xlabel(f"Time (/{data['Sample Time']} s)")
    plt.show()

class Hexapod:
    """A class to use pipython"""
    def __init__(self, IPorBasePV, UserCS = "PTYCHO"):
        _direct_connection_needed = False
        if len(IPorBasePV) == 0: # will use InterfaceSetupDlg
            _direct_connection_needed = True
        else:
            _m = IPorBasePV.split('.')
            if len(_m)==4:
                _direct_connection_needed = True
        if _direct_connection_needed:
            from .pigcs import Hexapod as hp
            self.pidev = hp(IPorBasePV)
            self.pidev.connect()
            self.isEPICS = False
            print("C887 is connected directly. Check wth .pidev.")
        else:
            from .pigcs_epics import Hexapod as hp
            self.pidev = hp(IPorBasePV)
            self.pidev.connect()
            self.isEPICS = True
            print("C887 is connected through EPICS. Check wth .pidev.")

        self.mycs = UserCS
        self.axes = ['X', 'Y', 'Z', 'U', 'V', 'W']
        self.wave_start = {'X':0, 'Y':0, 'Z':0, 'U':0, 'V':0, 'W':0}
        self.lock = threading.Lock()

    def disconnect(self):
        if self.isEPICS == False:
            self.pidev.close()

    def set_UserDefaultCSname(self, CS):
        self.mycs = CS

    def get_axes(self, cs=""):
        if len(cs)==0:
            csval = self.get_mycsinfo('ZERO')
        else:
            csval = self.get_mycsinfo(cs)
        del csval['Name']
        del csval['EndCoordinateSystem']
        self.axes = list(csval.keys())
        return csval
        # global allaxes
        # if connectiontype==1:
        #     allaxes = pidev.axes
        # else:
        #     csval = get_mycsinfo('ZERO')
        #     del csval['Name']
        #     del csval['EndCoordinateSystem']
        #     allaxes = list(csval.keys())
        # return allaxes

    def get_allcs(self):
        with self.lock:
            _s = self.pidev.qKLT()
            _v = decode_KLT(_s)
    #        for _m in _v:
    #            print(_m)
            return _v

    def get_mycsinfo(self, cs=""):
        with self.lock:
            if len(cs)==0:
                cs = self.get_CS()
                self.mycs = cs
            _s = self.get_allcs()
            for _m in _s:
                if _m['Name'] == cs:
                    return _m

    def print_return(self, ret):
        _m = ret.split('\n')
        for _a in _m:
            print(_a)

    def activate_CS(self, CS):
        # activate the coordinate system CS
        with self.lock:
            self.pidev.KEN(CS)

    def get_KET(self):
        strv = ''
        with self.lock:
            strv = self.pidev.qKET()
            return decode_KET(strv)

    def get_CS(self):
        """get the name of activated coordination system"""
        strv = self.get_KET()
        if isinstance(strv, type(None)):
            strv = 'ZERO'
        return strv

    def get_CSpos(self, csname):
        """get the positions of activated coordination system"""
        ax = self.get_axes(csname)
        return ax

    def remove_CS(self, csname):
        """remove a coordination system other than ZERO"""
        if csname=='ZERO':
            raise ValueError("Zero cannot be removed.")
        ccs = self.get_KSDname()
        if ccs==csname:
            self.set_default_CS()
        with self.lock:
            self.pidev.KRM(csname)

    def set_default_CS(self):
        """activate ZERO"""
        self.activate_CS(CS = "ZERO")

    def linkCS(self, cs, parent):
        """linking a child to a parent"""
        with self.lock:
            self.pidev.KLN(cs, parent)

    def add_CS(self, **kwargs):  # define new coordinate system.
        """adding a new coordination system, arguments: csname, parent, X, Y, Z, U, V, W"""
        parent = ""
        dic2pass = {}
        CS = ""
        for key, value in kwargs.items():
            if key == 'csname':
                CS = value.upper()
            elif key == 'parent':
                parent = value.upper()
            elif key == "axes":
                for key2, value2 in value.items():
                    dic2pass[key2] = value2
            else:
                dic2pass[key] = value
        if len(parent)==0:
            parent = 'ZERO'
        if len(CS)>0:
            self.set_CSpos(csname=CS, **dic2pass)
        else:
            CS = self.get_KSDname()
            self.set_CSpos(**dic2pass)
        self.linkCS(CS, parent)
        self.activate_CS(CS)

    def set_CSpos(self, **kwargs):
    # set XYZUVW of the currently activated coordination system(not ZERO)  
    # use 'parent' keyword for the parent of KSD.
    # set_CSpos(csname = 'NewCS1', X=1,Y=2,Z=1,U=2,V=1,W=0)  # for new one.
    # set_CSpos(X=1,Z=1) # this change only X and Z positions of the current active KSD.

        _cs =""
        _qcs = False
#        csval = {}
        for key, value in kwargs.items():
            if key == "csname":
                _cs = value.upper()
        if len(_cs)==0:
            _cs = self.get_KSDname()
            if _cs is not None:
                self.set_default_CS()
                _qcs = True
            else:
                raise ValueError("Custom coordination is not activated. Run activate_CS()")
        try:
            csval = self.get_CSpos(_cs)
        except:
            csval = {}
        for key, value in kwargs.items():
            if key in self.axes:
                csval[key] = value
            if key == "csname":
                _cs = value.upper()
            if key == "axes":
                for key2, value2 in value.items():
                    csval[key2] = value2
        with self.lock:
            self.pidev.KSD(csname=_cs, **csval)

        if _qcs:
            time.sleep(0.1)
            self.activate_CS(_cs)

    def get_KSDname(self):
        _s = self.get_KET()
        return _s

## New addition....
    def set_pulses(self, channel, wavetableID, pulse_start=1, pulse_width=1, pulse_period=100):
        # channel: output channel 1 through 4
        # wavetableID : any table ID among wavetable IDs that will be used for the scan.
        #               all those wavetable should have the same number of data points.
        wav = self.get_wavelen()
        try:
            Npnts = wav[wavetableID][1]
        except:
            print("wavetableID is empty.\n")
            Npnts = 0
        pulseN = 1
        pulse_rising_edge_position = [pulse_start]
        pnts4speedupdown = pulse_start
        if Npnts>0:
            try:
                while pulse_start < Npnts:
                    # TWS TriggerOutputChannle WaveletPosition Switch TriggerOutputChannle WaveletPosition Switch
                    self.pidev.send_command(f"TWS {channel} {pulse_start} 2 {channel} {pulse_start+pulse_width} 3")
                    pulse_start = pulse_start + pulse_period
                    if pulse_start > self.wave_pnts - pnts4speedupdown:
                        break
                    pulse_rising_edge_position.append(int(pulse_start))
                    #pulseN = pulseN + 1
                pulseN = len(pulse_rising_edge_position)
                print(f"{pulseN} number of pulses will be generated.")
            except gcserror.GCSError:
                print("Cannot clear triggers.\n")
            self.pulse_positions_index = pulse_rising_edge_position
            #self.pulse_positions = self.wave_x[pulse_rising_edge_position]
        else:
            print(f"The wavetable {wavetableID} might be empty.")
    
    def set_wav_SNAKE(self, time_per_line = 5, number_of_lines = 10, start_X0 = -2.5, X_distance=1, start_Y0 = 0, Y_step = 1, direction=1):
        sec4pnt = 0.001 # 1 milli-second for each pont.
        speed_up_down = 10
        totalpnts = time_per_line/sec4pnt*number_of_lines
        totalpnts4line0 = time_per_line/sec4pnt
        totalpnts4line = totalpnts4line0 + speed_up_down
        N_round = number_of_lines/2 # the number of lines should be even number...
        if totalpnts>self.qWMS():
            raise WAV_Exception("Too long wave.")
        wavetableID4X = 2
        wavetableID4Y = 3
        # setup X
        for i in range(N_round):
            if i==0:
                isappend = 'X'
            else:
                isappend = '&'
            cmd = f"WAV {wavetableID4X} {isappend} RAMP {totalpnts4line*2} {X_distance:.3e} {start_X0} {totalpnts4line*2} 0 {speed_up_down} {totalpnts4line}"
            self.pidev.send_command(cmd)
        # setup Y
        Y_target0 = start_Y0
        for i in range(N_round):
            if i==0:
                isappend = 'X'
            else:
                isappend = '&'
#            Y_target0 = 0
#            Y_step = 1
            # first flat 
            cmd = f"WAV {wavetableID4Y} {isappend} LIN {totalpnts4line0/2} 0 {Y_target0:.3e} {totalpnts4line0/2} 0 0"
            self.pidev.send_command(cmd)
            # linear increase
            cmd = f"WAV {wavetableID4Y} & LIN {totalpnts4line0+speed_up_down*2} {Y_step:.3e} {Y_target0:.3e} {totalpnts4line0+speed_up_down*2} 0 {totalpnts4line0}"
            self.pidev.send_command(cmd)
            # second flat
            if direction>1:
                Y_target0 = Y_target0 + Y_step
            else:
                Y_target0 = Y_target0 - Y_step
            cmd = f"WAV {wavetableID4Y} & LIN {totalpnts4line0/2} 0 {Y_target0:.3e} {totalpnts4line0/2} 0 0"
            self.pidev.send_command(cmd)

    def set_wav_x(self, totaltime=5, totaltravel=5, startposition=-2.5, pnts4speedupdown=10, direction=1):
        self.set_wav_LIN(totaltime, totaltravel, startposition, pnts4speedupdown, direction)

    def set_wav_LIN(self, totaltime=5, totaltravel=5, startposition=-2.5, pnts4speedupdown=10, direction=1, axis = 'X', wavetableID = 1):
        sec4pnt = 0.001 # 1m second for each pont.
        meanspeed_per_points = totaltravel/totaltime*sec4pnt
        #print(pnts4speedupdown, "pnts4speedupdown")
        distance4speedupdown = meanspeed_per_points*pnts4speedupdown
        totaltravel = totaltravel + distance4speedupdown*2
        startposition = startposition - direction*distance4speedupdown
        totalpnts = totaltime/sec4pnt
        #print(f"total time is {totaltime}, sec4pnt is {sec4pnt}, and totalpnts is {totalpnts}, pnts4down is {pnts4speedupdown}")
        totalpnts = totalpnts + pnts4speedupdown*2
        if totalpnts>self.qWMS():
            raise WAV_Exception("Too long wave.")

        #print(f"totalpnts = {totalpnts}, startposition={startposition}, totaltravel={totaltravel}")
        #self.wave_x = direction*np.arange(totalpnts)
        #self.wave_x = self.wave_x/totalpnts*totaltravel+startposition
        self.wave_pnts = totalpnts
        self.wave_start[axis] = startposition
        #self.wave_speed = totaltravel/totaltime
        self.wave_accelpoints = pnts4speedupdown
        #print(f"totaltravel is {totaltravel}, and totaltime is {totaltime}, and speed is {self.wave_speed}")

        #self.pidev.WAV_LIN(1, 0, totalpnts, 'X', pnts4speedupdown, totaltravel, startposition, totalpnts)
        # WAVE (WaveTableID, X, type) # X means clear the table.
        cmd = f"WAV {wavetableID} X LIN {totalpnts} {totaltravel:.3e} {startposition} {totalpnts} 0 {pnts4speedupdown}"
        self.pidev.send_command(cmd)
        print(cmd)

        #self.pidev.WSL(WaveGenID, waveTableID) # assign wavelet 1 to the X axis.
        self.pidev.send_command(f"WSL {WaveGenID[axis]} {wavetableID}")
        #self.pidev.WGC(WaveGenID, number of cycles to run) # run only 1 time
        self.pidev.send_command(f"WGC {WaveGenID[axis]} 1")
        
    def clear_Wave_Table_assignment(self):
        for axis in WaveGenID:
            self.pidev.send_command(f"WSL {WaveGenID[axis]} 0")

    def set_traj(self, axis="X", totaltime=5, totaltravel=5, startposition=-2.5, direction = 1, pulse_period_time=0.01, pnts4speedupdown=10):
        # set_traj(axis, totaltime, distance, startposition, direc, pulse_period_time, pointtoadd)
        # You can run multiple axis at the same time, but still generating one trigger out.
        # set_traj(['X', 'Y', 'Z'], 5, [1, 2, 0.5], [-0.5, -1, -0.25], [1, 1, 1], 0.01, 50)
        #       in this case, the three axis will start at the same time at different positions and end the motion at the same time.
        #       the step speed of each axis is different from each other.
        # total number of the trigger pulses = 5/0.01+1
        self.TWC()
        if type(totaltravel) != type([1,2]): # if type of totaltravel is not array.
            totaltravel = [totaltravel]
            startposition = [startposition]
            direction = [direction]
            axes = [axis]
        else:
            axes = axis
        pulse_period = abs(pulse_period_time)/0.001
        pulse_number = totaltime/abs(pulse_period_time)+1
        for ind, axis in enumerate(axes):
            # currently only for the first axis that is the X axis...
            direc = direction[ind]
            wave_speed = totaltravel[ind]/totaltime
            #print(direc, " direction")
            self.set_wav_LIN(totaltime, totaltravel[ind], startposition[ind], pnts4speedupdown, direction=direc, axis = axis, wavetableID = WaveGenID[axis])
            dist = wave_speed*abs(pulse_period_time)*1000
            print(f'For {axis}, it triggers {pulse_number} times in every {dist:.3e} um or %0.3f seconds.'% (totaltime/pulse_number))
        self.set_pulses(1, WaveGenID[axes[0]], pnts4speedupdown, 1, pulse_period)
        self.pulse_number = pulse_number
        self.scantime = totaltime
        self.pidev.send_command("CTO 1 3 9")

        # second axis can be added later.

    def goto_start_pos(self, axes2run='X'):
        if not hasattr(self, 'wave_start'):
            for axis in axes2run:
                wv = self.get_wavelet(WaveGenID[axis])
                self.wave_start[axis] = wv[0]
        #pos = self.get_pos()
        #if (pos['X']-self.wave_start)*1000000 > 200: # if off more than 200nm
        argv = []
        for axis in axes2run:
            argv.append(axis)
            argv.append(self.wave_start[axis])
        self.set_speed(1) # set the speed 1mm/second.
        time.sleep(0.1)
        self.mv(*argv)
        status = False
        while not status:
            try:
                state = self.isattarget()
                status = state[axis]
            except:
                status = False
            time.sleep(0.1)
        return status
    
    def run_traj(self, axes2run='X'):
        self.axes2run = axes2run
        wavegenerator_output_cmd = ''
        for axis in axes2run:
            wavegenerator_output_cmd = '%s %i 1' %(wavegenerator_output_cmd, WaveGenID[axis])

        wavegenerator_output_cmd = "WGO%s" % wavegenerator_output_cmd
        self.pidev.send_command(wavegenerator_output_cmd)
        print(f"Run command '{wavegenerator_output_cmd}' is sent.")
    
    def stop_traj(self):
        if not hasattr(self, 'axes2run'):
            return
        wavegenerator_output_cmd = ''
        for axis in self.axes2run:
            wavegenerator_output_cmd = '%s %i 0' %(wavegenerator_output_cmd, WaveGenID[axis])
        self.pidev.send_command("WGO%s"%wavegenerator_output_cmd)

    ## added for waveform. 11/1/2023
    def qCTO(self):
        with self.lock:
            """CTO?"""
            d = self.pidev.send_read_command('CTO?')
            return d

    def CTO(self, *argv):
        """CTO
        CTO(DIOid, Mode, Type, ...)
            1,2,3,and 4 for DIOid: DIO channel number.
            3 for Mode: TriggerMode
            9 for Type: Generator Pulse Trigger
        CTO(1, 3, 9)
        CTO(1, 3, 9, 2, 3, 9)
        """
        with self.lock:
            cmd = "CTO"
            for arg in argv:
                cmd = cmd + " %d"%arg
            self.pidev.send_command(cmd)

    def get_wavelen(self, wavetableID=-1):
        '''returns the length of wavelets
        if the wavelet ID is specified, return the length of the wavelet.
        otherwise, it returns lengthes of all wavelets'''
        with self.lock:
            d = self.pidev.send_read_command('WAV?')
        a = d.split('\n')
        wav = OrderedDict()
        
        for arg in a:
            if len(arg)>0:
                b = arg.split(' ')
                c = b[1].split('=')
                val = OrderedDict()
                val[int(c[0])] = int(c[1])
                wav[int(b[0])] = val
        # this will return {WaveTableID, {WaveParameterID, value}}
        if wavetableID >=0: 
            return wav[wavetableID][1]
        else:
            return wav

    def get_wavelet(self, length=10, waveletID=1):
        '''read the wavelet table and return wavelet'''
        with self.lock:
            d = self.pidev.send_read_command(f'GWD? 1 {length} {waveletID}')
        v = d.split('\n')
        dt = []
        for l in v:
            if len(l)==0:
                continue
            if l[0] == '#':
                print(l)
            else:
                dt.append(float(l))
        return dt

    def qTWG(self):
        with self.lock:
            d = self.pidev.send_read_command('TWG?')
        return int(d)

    def qWMS(self):
        # maximum available wave table points
        with self.lock:
            d = self.pidev.send_read_command('WMS?')
        b = d.split('\n')
        a = b[0].split('=')
        return int(a[1])

    def TWC(self):
        with self.lock:
            self.pidev.send_command('TWC')

    def get_pos(self):
        with self.lock:
            return self.pidev.get_pos()
    
    def mv(self, *argv):
        cmd = 'MOV'
        for arg in argv:
            cmd = cmd + ' %s' % arg
        with self.lock:    
            self.pidev.send_command(cmd)

    def get_records(self, Ndata=0):
        # wavelet 1: target position X
        # wavelet 2: real position X
        # 3 and 4: for Y
        # ..
        # 11 and 12: for W
        if Ndata == 0:
            wave = self.get_wavelen()
            Ndata = wave[1][1] # read the wavelet 1.
        with self.lock:
            dt = self.pidev.send_read_command(f"DRR? 1 {Ndata} 1 2 3 4 5 6 7 8 9 10 11 12")
        v = dt.split('\n')
        Xt = []
        Xr = []
        Yt = []
        Yr = []
        Zt = []
        Zr = []
        Ut = []
        Ur = []
        Vt = []
        Vr = []
        Wt = []
        Wr = []

        data = {}
        for l in v:
            if len(l)==0:
                continue
            if l[0] == '#':
                if 'SAMPLE_TIME' in l:
                    v = l.split(' = ')
                    data['Sample Time'] = float(v[1])
            else:
                n = l.split(' ')
                Xt.append(float(n[0]))
                Xr.append(float(n[1]))
                Yt.append(float(n[2]))
                Yr.append(float(n[3]))
                Zt.append(float(n[4]))
                Zr.append(float(n[5]))
                Ut.append(float(n[6]))
                Ur.append(float(n[7]))
                Vt.append(float(n[8]))
                Vr.append(float(n[9]))
                Wt.append(float(n[10]))
                Wr.append(float(n[11]))
        data['X'] = (np.array(Xt), np.array(Xr))
        data['Y'] = (np.array(Yt), np.array(Yr))
        data['Z'] = (np.array(Zt), np.array(Zr))
        data['U'] = (np.array(Ut), np.array(Ur))
        data['V'] = (np.array(Vt), np.array(Vr))
        data['W'] = (np.array(Wt), np.array(Wr))
        return data

    def isattarget(self, axis=""):
        ret = False
        while not ret:
            try:
                with self.lock:
                    r = self.pidev.send_read_command('ONT?')
                ret = True
            except:
                ret = False
                time.sleep(0.1)
        if len(r)==0:
            return None
        v = decode_ONT(r)
        if len(axis):
            return v[axis]
        return v

    def reset_record_table(self):
        with self.lock:
            self.pidev.send_command('DRC 1 X 1')
            self.pidev.send_command('DRC 2 X 2')
            self.pidev.send_command('DRC 3 Y 1')
            self.pidev.send_command('DRC 4 Y 2')
            self.pidev.send_command('DRC 5 Z 1')
            self.pidev.send_command('DRC 6 Z 2')
            self.pidev.send_command('DRC 7 U 1')
            self.pidev.send_command('DRC 8 U 2')
            self.pidev.send_command('DRC 9 V 1')
            self.pidev.send_command('DRC 10 V 2')
            self.pidev.send_command('DRC 11 W 1')
            self.pidev.send_command('DRC 12 W 2')
            self.pidev.send_command('DRC 13 1 8')
            self.pidev.send_command('DRC 14 0 0')
            self.pidev.send_command('DRC 15 0 0')
            self.pidev.send_command('DRC 16 0 0')
    
    def get_speed(self):
        # returns speed in mm/s 
        ret = False
        while not ret:
            try:
                with self.lock:
                    r = self.pidev.send_read_command('VLS?')
                ret = True
            except:
                ret = False
                time.sleep(0.1)
        # decipher
        v = r.split('\n')
        for l in v:
            if len(l)>0:
                return float(l)
        return None
    
    def set_speed(self, val):
        # unit of the speed is mm/s 
        with self.lock:
            self.pidev.send_command('VLS %f'%val)
        