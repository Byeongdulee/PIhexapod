# When you do not need to use EPICS,
# install PIPython (pip install pipython)
# https://github.com/PI-PhysikInstrumente/PIPython
# KLS?
# KSD CSname X 80 Y ... : define CSname coordinate system.
# KLN CS1 CS2: set CS2 to be a parent of CS1
# KEN CSname: enable CSname
import time
from .decode import decode_KET, decode_KLT

IP = '164.54.122.87'
BASEPV = "12idHXP"

class Hexapod:
    """A class to use pipython"""
    def __init__(self, IPorBasePV, UserCS = "PTYCHO"):
        _m = IPorBasePV.split('.')
        if len(_m)==4:
            from .pigcs import Hexapod as hp
            self.pidev = hp(IPorBasePV)
            self.pidev.connect()
        else:
            from .pigcs_epics import Hexapod as hp
            self.pidev = hp(IPorBasePV)
            self.pidev.connect()

        self.mycs = UserCS
        self.axes = ['X', 'Y', 'Z', 'U', 'V', 'W']

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
