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
        try:
            self.pidev.gcscommands.send(cmd)
        except gcserror.GCSError:
            raise gcserror.GCSError
        
    def send_read_command(self, cmd):
        try:
            return self.pidev.gcscommands.read(cmd)
        except gcserror.GCSError:
            raise gcserror.GCSError

    def close(self):
        """disconnect"""
        self.pidev.CloseConnection()

    def KEN(self, CS):
        """KEN"""
        self.send_command(f"KEN {CS}")

    def KRM(self, csname):
        self.send_command(f"KRM {csname}")

    def KLN(self, cs, parent):
        self.send_command(f"KLN {cs} {parent}")

    def KSD(self, **kwargs):
        # cannot apply to the currently active one
        # example:
        # KSD(csname='newcs0', Z=10)
        axstr = ""
        for key, value in kwargs.items():
            if key in self.axes:
                axstr = axstr+f" {key} "+ str(value)
            if key == "csname":
                CS = value.upper()
        self.send_command(f"KSD {CS} {axstr}")
    
    def FRF(self):
        self.send_command(f"FRF X")
    
    def SVO(self):
        self.send_command(f"SVO X 1")

    def qFRF(self):
        return self.pidev.qFRF()
    
    def qSVO(self):
        return self.pidev.qSVO()
    
    def qKET(self):
        """KET?"""
        return self.pidev.qKET()

    def qKLT(self):
        """KLT?"""
        s = self.pidev.qKLT()
        return s

    def get_pos(self):
        s = None
        max_retry = 5
        i = 0
        while (s is None):
            try:
                s = self.pidev.qPOS()
            except:
                s = None
            if i==max_retry:
                break
            i = i + 1
        if (s is None):
            raise TimeoutError
        return s