import serial
from serial.tools.list_ports import comports
import time
import struct

def printHexStr( sToPrint ):
    hexStr = ''
    for i in range( len(sToPrint ) ):
        hexStr= hexStr + '%x'%(struct.unpack('B',sToPrint[i]))
    print(hexStr)
    return hexStr

class StirrerControl:
    def __init__(self, port='/dev/ttyUSB0',addr=1,**kwargs):
        self.port = port
        self.addr = addr
        if len(comports())<1:
            print("No serial port found. Check motor connection.")
        else:
            self.ser = serial.Serial( self.port, 9600, timeout=2 )
            self.setSlowMoveCurrent( 60 )
            self.setPosModeVelocity( 50, 250 )
            self.termLoopCmd()
            # self.ser.write('/%1dA%dR\r\n'%(self.addr, 0.0))
            self.moveAbsPos(0)
            time.sleep(.1)

    def __enter__(self):
        pass

    def write(self, st):
        self.ser.write(st.encode())

    # Dunno why this works, but it does.
    def isReady(self):
        return self.getCurrentPos()[0]==98

    def waitReady(self):
        while not self.isReady():
            pass

    def setSlowMoveCurrent(self, value):
        self.write('/%1dl%dR\r\n'%(self.addr,value))
        self.lastResponse=self.ser.readline()
        # printHexStr( self.lastResponse )


    def setPosModeVelocity(self, startSpeed, maxSpeed):
        # Set the max start speed of motor
        self.write('/%1dv%dR\r\n'%(self.addr,startSpeed))
        self.lastResponse=self.ser.readline()
        # printHexStr( self.lastResponse )
        # Set the max/slew speed of motor
        self.write('/%1dV%dR\r\n'%(self.addr,maxSpeed))
        self.lastResponse=self.ser.readline()
        # printHexStr( self.lastResponse )

    def termLoopCmd(self):
        self.write('/%1dT\r\n'%(self.addr))
        self.lastResponse= self.ser.readline()
        # printHexStr( self.lastResponse )

    def moveAbsPos(self,absPos):
        self.write('/%1dA%dR\r\n'%(self.addr,absPos))
        self.lastResponse= self.ser.readline()
        #printHexStr( self.lastResponse )

    def moveRelPos(self,relPos):
        if relPos<0:
            self.write('/%1dD%dR\r\n'%(self.addr,-relPos))
        elif relPos>0:
            self.write('/%1dP%dR\r\n'%(self.addr,relPos))
        self.lastResponse= self.ser.readline()
        # printHexStr( self.lastResponse )

    def gotoHomePos(self):
        self.write('/%1d1ZR\r\n'%(self.addr))
        self.lastResponse= self.ser.readline()
        # printHexStr( self.lastResponse )

    def getCurrentPos(self):
       self.write('/%1d1A?\r\n'%(self.addr))
       self.lastResponse= self.ser.readline()
       # printHexStr( self.lastResponse )
       sof,startChar,addrRec,status,resp,etx=struct.unpack('BBBBHB',self.lastResponse)
       return (status,resp)
    
    def controlLights( self, value ):
        self.write('/%1dJ%1dR\r\n'%(self.addr,value))
        self.lastResponse= self.ser.readline()
        # printHexStr( self.lastResponse )

    def close(self):
        self.waitReady()
        self.controlLights(0)
        self.moveAbsPos(0)
        self.ser.close()

    def __exit__(self, type, value, traceback ):
        self.close()


def main():
    s=StirrerControl(port='/dev/ttyUSB0',addr=1)
    s.controlLights(2)
    print(s)
    s.setSlowMoveCurrent( 60 )
    s.gotoHomePos()
    time.sleep(1)
    s.getCurrentPos()
    time.sleep(1)
    s.moveRelPos(400)
    time.sleep(1)
    print(s.getCurrentPos())
    s.moveRelPos(-400)
    time.sleep(1)
    print(s.getCurrentPos())
    s.gotoHomePos()
    time.sleep(1)
    print(s.getCurrentPos())
    s.moveAbsPos(1000)
    print(s.getCurrentPos())

    s.close()

if __name__ == '__main__':
    main()
