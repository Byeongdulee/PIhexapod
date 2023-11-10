#print("EPICS IOC is not running.")
#print("Connecting with pipython.")
from pipython import GCSDevice, gcserror

## Exception handling....
class WAV_Exception(Exception):
    pass

class Hexapod:

    def __init__(self, IP, dev='C-887') -> None:
        self.connectiontype = -1
        self.pidev = GCSDevice(dev)
        self.axes = ['X', 'Y', 'Z', 'U', 'V', 'W']
        self.ip = IP

    def connect(self, IP=""):
        """connecting"""
        notconnected = False
        if len(IP)>0:
            self.ip = IP

        if len(self.ip.split('.'))==4:
            try:
                self.pidev.ConnectTCPIP(self.ip)
            except gcserror.GCSError:
                print('Connection failed. Check your IP or another software running for the IP.')
                notconnected = True
        else:
            try:
                self.pidev.InterfaceSetupDlg()
                print(self.pidev.qIDN())
            except gcserror.GCSError:
                print('Connection failed. Check if another software running for the IP')
                notconnected = True
        if notconnected is False:
            self.connectiontype = 1
        return self.connectiontype

    def send_command(self, cmd):
        self.pidev.gcscommands.send(cmd)

    def send_read_command(self, cmd):
        return self.pidev.gcscommands.read(cmd)

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
        try:
            self.pidev.KSD(csname=CS, axes=csval)
        except gcserror.GCSError:
            print("Cannot change the current cs.\n")

    def qKET(self):
        """KET?"""
        return self.pidev.qKET()

    def qKLT(self):
        """KLT?"""
        s = self.pidev.qKLT()
        return s

    def get_pos(self):
        s = self.pidev.qPOS()
        return s
    
    def mv(self, axes='X', pos=0):
        self.pidev.MOV(axes, pos)