import epics as ep
from epics import caput, caget
import time
mycs = "PTYCHO"

class Hexapod:
    """A code to control through epics"""
    def __init__(self, base) -> None:
        self.basepv = base+":asyn_1"
        self._terminator = "\\n"
        self.waittime = 2
        self.axes = ['X', 'Y', 'Z', 'U', 'V', 'W']

    def connect(self):
        """connect"""
        self.hxpout = ep.PV(self.basepv+".AOUT")
        time.sleep(self.waittime)
        self.connectiontype = -1
        if self.hxpout.connected:
            #self.hxpin = ep.PV(self.basepv+".AINP")
            #self.hxpoutb = ep.PV(self.basepv+".BOUT")
            self.hxpoutb_len = ep.PV(self.basepv+".NOWT")
            self.hxplenSent = ep.PV(self.basepv+".NAWT")
            self.hxpinb = ep.PV(self.basepv+".BINP")

            caput(self.basepv+".OFMT", "ASCII")
            caput(self.basepv+".IFMT", "Binary")
            caput(self.basepv+".IEOS", "")
            caput(self.basepv+".OEOS", "")
            imax = caget(self.basepv+".IMAX")
            if imax<(2**12-1):
                print("Warning!! IMAX should be more than 2**12")
            self.connectiontype = 0
        return self.connectiontype

    def send_command(self, com):
        """send data through AOUT"""
        self.hxpout.put(com+self._terminator)

    def get(self):
        """read data"""
        return self.get_binary()

    def get_binary(self):
        """read data from BINP"""
        val = self.hxpinb.get()
        v = ""
        for b in val:
            v = v+chr(b)
        return v

    def KEN(self, CS):
        """KEN"""
        self.send_command(f"KEN {CS}")

    def KRM(self, csname):
        self.send_command(f"KRM {csname}")

    def KLN(self, cs, parent):
        self.send_command(f"KLN {cs} {parent}")

    def KSD(self, **kwargs):
        axstr = ""
        for key, value in kwargs.items():
            if key in self.axes:
                axstr = axstr+f" {key} "+ str(value)
            if key == "csname":
                CS = value.upper()
        self.send_command(f"KSD {CS} {axstr}")

    def qKET(self):
        self.send_command("KET?")
        strv = ""
        st = time.time()
        while len(strv)==0:
            time.sleep(0.1)
            strv = self.get()
            if 'PI_BASE' not in strv:
                strv = ""
            if (time.time()-st)>self.waittime:
                break
        if len(strv)==0:
            ValueError("Connecion is failed.")
        return strv

    def qKLT(self):
        self.send_command("KLT?")
        s = ""
        st = time.time()
        while len(s)==0:
            time.sleep(0.1)
            s = self.get()
            if 'Name=' not in s:
                s = ""
            if (time.time()-st)>self.waittime:
                break
        if len(s)==0:
            ValueError("Connecion is failed.")
        return s