#print("EPICS IOC is not running.")
#print("Connecting with pipython.")
from pipython import GCSDevice, gcserror

class Hexapod:

    def __init__(self, dev='C-887') -> None:
        self.ConnectionType = -1
        self.pidev = GCSDevice(dev)

    def connect(self, IP):
        """connecting"""
        notconnected = False
        if len(IP)>0:
            self.IP = IP
            try:
                self.pidev.ConnectTCPIP(self.IP)
            except:
                notconnected = True
        else:
            try:
                self.pidev.InterfaceSetupDlg()
            except:
                notconnected = True
        if notconnected == False:
            self.ConnectionType = 1
        return self.ConnectionType

    def close(self):
        """disconnect"""
        self.pidev.CloseConnection()

    def KEN(self, CS):
        self.pidev.KEN(CS)

    def qKET(self):
        return self.pidev.qKET()

    def KRM(self, csname):
        self.pidev.KRM(csname)

    def KLN(self, cs, parent):
        self.pidev.KLN(cs, parent)

    def KSD(self, **kwargs):
        csval = {}
        for key, value in kwargs.items():
            if key in self.allaxes:
                csval[key] = value
            if key == "csname":
                CS = value.upper()
        self.pidev.KSD(csname=CS, axes=csval)

    def qKLT(self):
        s = self.pidev.qKLT()
        return s