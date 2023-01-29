# When you do not need to use EPICS,
# install PIPython (pip install pipython)
# https://github.com/PI-PhysikInstrumente/PIPython
# KLS?
# KSD CSname X 80 Y ... : define CSname coordinate system.
# KLN CS1 CS2: set CS2 to be a parent of CS1
# KEN CSname: enable CSname
import time
from .decode import decode_KEN, decode_KET, decode_KLT

hexapodIP = '164.54.122.87'
basePV = "12idHXP"

class hexapod:
    def __init__(self, IPorBasePV, UserCS = "PTYCHO"):
        m = IPorBasePV.split('.')
        if len(m)==4:
            from pigcs import hexapod as hp
            self.pidev = hp()
            self.pidev.connect(IPorBasePV)
        else:
            from pigcs_epics import hexapod as hp
            self.pidev = hp()
            self.pidev.connect(IPorBasePV)

        self.mycs = UserCS

    def set_UserDefaultCSname(self, CS):
        self.mycs = CS

    def get_axes(self):
        csval = self.get_mycsinfo('ZERO')
        del csval['Name']
        del csval['EndCoordinateSystem']
        allaxes = list(csval.keys())
        self.axes = allaxes
        return allaxes
        # global allaxes
        # if ConnectionType==1:
        #     allaxes = pidev.axes
        # else:
        #     csval = get_mycsinfo('ZERO')
        #     del csval['Name']
        #     del csval['EndCoordinateSystem']
        #     allaxes = list(csval.keys())
        # return allaxes

    def get_allcs(self):
        s = self.pidev.qKLT()
        return decode_KLT(s)


    def get_mycsinfo(self, cs=""):
        if len(cs)==0:
            cs = self.mycs
        s = self.get_allcs()
        for m in s:
            if m['Name'] == cs:
                return m

    def print_return(self, ret):
        m = ret.split('\n')
        for a in m:
            print(a)


    def set_CS(self, CS):
        self.pidev.KEN(CS)

    def get_KET(self):
        strv = ''
        strv = self.pidev.qKET()
        return decode_KET(strv)

    def get_CS(self):
        strv = self.get_KET()
        if isinstance(strv, type(None)):
            strv = 'ZERO'
        return strv

    def remove_CS(self, csname):
        if csname=='ZERO':
            raise ValueError("Zero cannot be removed.")
        ccs = self.get_KSDname()
        if ccs==csname:
            self.set_default_CS()
        self.pidev.KRM(csname)

    def set_default_CS(self):
        self.set_CS(CS = "ZERO")

    def linkCS(self, cs, parent):
        self.pidev.KLN(cs, parent)

    def add_CS(self, **kwargs):  # define new coordinate system.
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

        CS =""
        qCS = False

        csval = {}
        for key, value in kwargs.items():
            if key in self.axes:
                csval[key] = value
            if key == "csname":
                CS = value.upper()
        if len(CS)==0:
            CS = self.get_KSDname() 
            if CS is not None:
                self.set_default_CS()
                qCS = True
            else:
                raise ValueError("Custom coordination is not activated. Run set_CS()")
        try:
            self.pidev.KSD(csname=CS, axes=csval)
        except self.pidev.gcserror.GCSError:
            print("Cannot change the current cs.")

        if qCS:
            time.sleep(0.1)
            self.set_CS(CS=CS)

    def get_KSDname(self):
        s = self.get_KET()
        return s
