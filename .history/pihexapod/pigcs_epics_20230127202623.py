import epics as ep
from epics import caput, caget
import time
mycs = "PTYCHO"

class hexapod:
    def __init__(self, base) -> None:
        self.basePV = base+":asyn_1"
        self._terminator = "\\n"
        self.waittime = 2
        self.allaxes = ['X', 'Y', 'Z', 'U', 'V', 'W']

    def connect(self):
        self.HXPout = ep.PV(self.basePV+".AOUT")
        time.sleep(self.waittime)
        self.ConnectionType = -1
        if self.HXPout.connected:
            self.HXPin = ep.PV(self.basePV+".AINP")
            self.HXPoutb = ep.PV(self.basePV+".BOUT")
            self.HXPoutb_len = ep.PV(self.basePV+".NOWT")
            self.HXPlenSent = ep.PV(self.basePV+".NAWT")
            self.HXPinb = ep.PV(self.basePV+".BINP")

            caput(self.basePV+".OFMT", "ASCII")
            caput(self.basePV+".IFMT", "Binary")
            caput(self.basePV+".IEOS", "")
            caput(self.basePV+".OEOS", "")
            imax = caget(self.basePV+".IMAX")
            if imax<(2**12-1):
                print("Warning!! IMAX should be more than 2**12")
            self.ConnectionType = 0
        return self.ConnectionType

    def send_command(self, com):
        self.HXPout.put(com+self._terminator)
    def get(self):
        return self.get_binary()
    def get_binary(self):
        val = self.HXPinb.get()
        v = ""
        for b in val:
            v = v+chr(b)
        return v
    def KEN(self, CS):
        self.send_command(f"KEN {CS}")

    def qKET(self):
        self.send_command(f"KET?")
        strv = ""
        st = time.time()
        while len(strv)==0:
            time.sleep(0.1)
            strv = self.get()
            if (time.time()-st)>self.waittime:
                break
        if len(strv)==0:
            ValueError("Connecion is failed.")
    def KRM(self, csname):
        self.send_command(f"KRM {csname}")
    def KLN(self, cs, parent):
        self.send_command(f"KLN {cs} {parent}")
    def KSD(self, **kwargs):
        axstr = ""
        for key, value in kwargs.items():
            if key in self.allaxes:
                axstr = axstr+f" {key} "+ str(value)
            if key == "csname":
                CS = value.upper()
        self.send_command(f"KSD {CS} {axstr}")
    
    def qKLT(self):
        self.send_command("KLT?")
        s = ""
        st = time.time()
        while len(s)==0:
            time.sleep(0.25)
            s = self.get()
            if (time.time()-st)>self.waittime:
                break
        if len(s)==0:
            ValueError("Connecion is failed.")
        return s