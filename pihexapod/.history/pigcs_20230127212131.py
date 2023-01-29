#print("EPICS IOC is not running.")
#print("Connecting with pipython.")
from pipython import GCSDevice, gcserror

class Hexapod:

    def __init__(self, dev='C-887') -> None:
        self.connectiontype = -1
        self.pidev = GCSDevice(dev)
        self.axes = ['X', 'Y', 'Z', 'U', 'V', 'W']

    def connect(self, IP):
        """connecting"""
        notconnected = False
        if len(IP)>0:
            self.ip = IP
            try:
                self.pidev.ConnectTCPIP(self.ip)
            except:
                notconnected = True
        else:
            try:
                self.pidev.InterfaceSetupDlg()
            except:
                notconnected = True
        if notconnected is False:
            self.connectiontype = 1
        return self.connectiontype

    def close(self):
        """disconnect"""
        self.pidev.CloseConnection()

    def KEN(self, CS):
        """KEN"""
        self.pidev.KEN(CS)

    def KRM(self, csname):
        """KRM"""
        self.pidev.KRM(csname)

    def KLN(self, cs, parent):
        """KLN"""
        self.pidev.KLN(cs, parent)

    def KSD(self, **kwargs):
        """KSD"""
        csval = {}
        for key, value in kwargs.items():
            if key in self.axes:
                csval[key] = value
            if key == "csname":
                CS = value.upper()
        self.pidev.KSD(csname=CS, axes=csval)

    def qKET(self):
        """KET?"""
        return self.pidev.qKET()

    def qKLT(self):
        """KLT?"""
        s = self.pidev.qKLT()
        return s