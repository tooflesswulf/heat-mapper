import serial
from serial.tools.list_ports import comports
import time
import struct

class FoTempReader:
    def __init__(self, port='/dev/ttyUSB0', verbose=False,**kwargs):
        self.port = port
        self.verbose=verbose
        if len(comports())<1:
            print("No serial ports found. Please connect the Fiber Optic Probe and try again.")
        else:
            self.ser = serial.Serial( self.port, 57600, timeout=2 )
    
    def sendAndGetResponse(self,strToSend):
        self.ser.write(strToSend)
        self.lastResponse = self.ser.readline()
        self.lastStatus = self.ser.readline()
        if self.verbose:
            print ("response=%s",self.lastResponse)
            print("last status=%s", self.lastStatus)
        if self.lastStatus[1:3]=='FF':
            print("error occurred reading probe")
        return self.lastResponse, self.lastStatus
            
    def getCurrentTemp(self):
        resp, status = self.sendAndGetResponse("?01 01\r\n")
        
        temp = float(int(resp[5:])/10.)
        if self.verbose:
            print ("Current Temp = %f"%(temp))
        return temp
        
    def getNumChannels(self):
        resp,status = self.sendAndGetResponse("?0F\r\n")
        numChannels = int(resp[4:])
        if self.verbose:
            print("Num channels = %d"%(numChannels))
        return numChannels