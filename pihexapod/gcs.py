# When you do not need to use EPICS,
# install PIPython (pip install pipython)
# https://github.com/PI-PhysikInstrumente/PIPython
# KLS?
# KSD CSname X 80 Y ... : define CSname coordinate system.
# KLN CS1 CS2: set CS2 to be a parent of CS1
# KEN CSname: enable CSname
import time
from .decode import decode_KET, decode_KLT
from collections import OrderedDict

IP = '164.54.122.87'
BASEPV = "12idHXP"

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

    def disconnect(self):
        if self.isEPICS == False:
            self.pidev.close()

    def set_UserDefaultCSname(self, CS):
        self.mycs = CS

    def get_axes(self):
        csval = self.get_mycsinfo('ZERO')
        del csval['Name']
        del csval['EndCoordinateSystem']
        self.axes = list(csval.keys())
        return self.axes
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
        _s = self.pidev.qKLT()
        _v = decode_KLT(_s)
#        for _m in _v:
#            print(_m)
        return _v

    def get_mycsinfo(self, cs=""):
        if len(cs)==0:
            cs = self.mycs
        _s = self.get_allcs()
        for _m in _s:
            if _m['Name'] == cs:
                return _m

    def print_return(self, ret):
        _m = ret.split('\n')
        for _a in _m:
            print(_a)

    def set_CS(self, CS):
        self.pidev.KEN(CS)

    def get_KET(self):
        strv = ''
        strv = self.pidev.qKET()
        return decode_KET(strv)

    def get_CS(self):
        """get the name of activated coordination system"""
        strv = self.get_KET()
        if isinstance(strv, type(None)):
            strv = 'ZERO'
        return strv

    def remove_CS(self, csname):
        """remove a coordination system other than ZERO"""
        if csname=='ZERO':
            raise ValueError("Zero cannot be removed.")
        ccs = self.get_KSDname()
        if ccs==csname:
            self.set_default_CS()
        self.pidev.KRM(csname)

    def set_default_CS(self):
        """activate ZERO"""
        self.set_CS(CS = "ZERO")

    def linkCS(self, cs, parent):
        """linking a child to a parent"""
        self.pidev.KLN(cs, parent)

    def add_CS(self, **kwargs):  # define new coordinate system.
        """adding a new coordination system, arguments: csname, parent, X, Y, Z, U, V, W"""
        parent = ""
        dic2pass = {}
        for key, value in kwargs.items():
            if key == 'csname':
                CS = value.upper()
            if key == 'parent':
                parent = value.upper()
            dic2pass[key] = value
        if len(parent)==0:
            parent = 'ZERO'
        
        self.set_CSpos(**kwargs)
        self.linkCS(CS, parent)
        self.set_CS(CS)

    def set_CSpos(self, **kwargs):
    # set XYZUVW of the currently activated coordination system(not ZERO)  
    # use 'parent' keyword for the parent of KSD.
    # set_CSpos(csname = 'NewCS1', X=1,Y=2,Z=1,U=2,V=1,W=0)  # for new one.
    # set_CSpos(X=1,Z=1) # this change the position of the current active KSD.

        _cs =""
        _qcs = False

        csval = {}
        for key, value in kwargs.items():
            if key in self.axes:
                csval[key] = value
            if key == "csname":
                _cs = value.upper()
        if len(_cs)==0:
            _cs = self.get_KSDname()
            if _cs is not None:
                self.set_default_CS()
                _qcs = True
            else:
                raise ValueError("Custom coordination is not activated. Run set_CS()")

        self.pidev.KSD(csname=_cs, axes=csval)

        if _qcs:
            time.sleep(0.1)
            self.set_CS(CS=_cs)

    def get_KSDname(self):
        _s = self.get_KET()
        return _s

## New addition....
    def set_pulses(self, channel, wavetableID, pulse_start=1, pulse_width=1, pulse_period=100, pulse_number=2):
        wav = self.qWAV()
        try:
            Npnts = wav[wavetableID][1]
        except:
            print("wavetableID is empty.\n")
            Npnts = 0
        pulseN = 1
        if Npnts>0:
            try:
                while pulse_start < Npnts:
                    self.pidev.send_command(f"TWS {channel} {pulse_start} 2 {channel} {pulse_start+pulse_width} 3")
                    pulse_start = pulse_start + pulse_period
                    pulseN = pulseN + 1
                print(f"{pulseN-1} number of pulses will be generated.")
            except gcserror.GCSError:
                print("Cannot clear triggers.\n")
        else:
            print(f"The wavetable {wavetableID} might be empty.")
    
    def set_wav_x(self, totaltime=5, totaltravel=5, startposition=-2.5, pnts4speedupdown=10):
        sec4pnt = 0.001 # 1m second for each pont.
        meanspeed_per_points = totaltravel/totaltime*sec4pnt
        distance4speedupdown = meanspeed_per_points*pnts4speedupdown
        totaltravel = totaltravel + distance4speedupdown*2
        startposition = startposition - distance4speedupdown
        totalpnts = totaltime/sec4pnt
        totalpnts = totalpnts + pnts4speedupdown*2
        if totalpnts>self.qWMS():
            raise WAV_Exception("Too long wave.")

        print(f"totalpnts = {totalpnts}, startposition={startposition}, totaltravel={totaltravel}")
        self.wave_pnts = totalpnts
        self.wave_start = startposition
        self.wave_speed = totaltravel/totaltime
        self.wave_accelpoints = pnts4speedupdown

        #self.pidev.WAV_LIN(1, 0, totalpnts, 'X', pnts4speedupdown, totaltravel, startposition, totalpnts)
        cmd = f"WAV 1 X LIN {totalpnts} {totaltravel} {startposition} {totalpnts} 0 {pnts4speedupdown}"
        self.pidev.send_command(cmd)
        print(cmd)
        #self.pidev.WSL(1, 1) # assign wavelet 1 to the X axis.
        self.pidev.send_command("WSL 1 1")
        #self.pidev.WGC(1, 1) # run only 1 time
        self.pidev.send_command("WGC 1 1")
        

    def set_traj(self, totaltime=5, totaltravel=5, startposition=-2.5, pnts4speedupdown=10, pulse_period_time=0.01):
        self.TWC()
        pulse_period = pulse_period_time/0.001
        # currently only for the first axis that is the X axis...
        self.set_wav_x(totaltime, totaltravel, startposition, pnts4speedupdown)
        pulse_number = totaltime/pulse_period_time+1
        self.set_pulses(1, 1, pnts4speedupdown, 1, pulse_period, pulse_number)
        self.pulse_number = pulse_number
        print(f'Total {pulse_number} data will be collected, each in every {self.wave_speed*pulse_period_time*1000} um.')
        self.pidev.send_command("CTO 1 3 9")

        # second axis can be added later.

    def run_traj(self):
        self.pidev.send_command("WGO 1 1")
    
    def stop_traj(self):
        self.pidev.send_command("WGO 1 0")

    ## added for waveform. 11/1/2023
    def qCTO(self):
        """CTO?"""
        d = self.pidev.send_read_command('CTO?')
        return s

    def CTO(self, *argv):
        """CTO
        CTO(DIOid, Mode, Type, ...)
            1,2,3,and 4 for DIOid: DIO channel number.
            3 for Mode: TriggerMode
            9 for Type: Generator Pulse Trigger
        CTO(1, 3, 9)
        CTO(1, 3, 9, 2, 3, 9)
        """
        cmd = "CTO"
        for arg in argv:
            cmd = cmd + " %d"%arg
        self.pidev.send_command(cmd)

    def qWAV(self):
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
        return wav

    def qTWG(self):
        d = self.pidev.send_read_command('TWG?')
        return int(d)

    def qWMS(self):
        # maximum available wave table points
        d = self.pidev.send_read_command('WMS?')
        b = d.split('\n')
        a = b[0].split('=')
        return int(a[1])

    def TWC(self):
        self.pidev.send_command('TWC')

    def get_pos(self):
        return self.pidev.get_pos()
    
    def mv(self, *argv):
        cmd = 'MOV'
        for arg in argv:
            cmd = cmd + ' %s' % arg
        self.pidev.send_command(cmd)