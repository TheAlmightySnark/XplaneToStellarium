#Stellarium related imports
from urllib.parse import urlencode
import requests

#X-plane related imports
import struct #structure byte arrays for X-plane
import socket #UDP connection
import threading #used for multithreading

import os

xpDrefs = [
    (1, "sim/flightmodel/position/latitude", float), #ID, datarate, dataref, datatype
    (1, "sim/flightmodel/position/longitude", float), #ID, datarate, dataref, datatype
]

class StellariumToXplane:
    _port = 49000
    _IP = '127.0.0.1'

    _sock = None

    def __init__(self):
        os.system('cls')
        print('Welcome to Stellarium To X-plane.')
        print('Default IP and port are 127.0.0.1 and 49000')
        print('leave IP and PORT empty if these are fine')

        print('IP:')
        if input(self):
            self._IP = input()

        print('PORT:')
        if input(self):
            self._port = int(input())

        print('starting with %s and %s'%(self._IP, self._port))

        #create the socket object
        if not self._sock:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #send all the datagrams to Xplane, this tells X-plane what data to start transmitting
        #over the UDP connection.
        for idx, item in enumerate(xpDrefs):
            self.requestDref(idx, item[0], item[1])

        #build RREF according to X-plane 10/Instructions/Sending Data To X-plane.rtf
    def requestDref(self, id, rate, dref):
        padstring = '<5sii400s' #padding to 413 bytes according to the struct packing page(python)
        type = b"RREF\x00" #5 byte data type including null terminator

        self.sendUDP(struct.pack(padstring, type, rate, id, dref.encode()))

    def sendUDP(self, message):
        self._sock.sendto(message, (self._IP, self._port))

        threading.Thread(target=self.receiveUDP, args=()).start()

    def receiveUDP(self):
        data, adress = self._sock.recvfrom(1024)
        lat = None
        lon = None
        decoded = self.decodeData(data)

        if decoded is None:
            print("No X-plane UDP data received")
            os.system('cls')
            threading.Thread(target=self.receiveUDP, args=()).start()
            return

        for k, v in decoded.items():
            if k == 0:
                lat = str(float(v))
                continue
            if k == 1:
                lon = str(float(v))
                continue

        r = requests.post("http://localhost:8090/api/location/setlocationfields", params=urlencode({'latitude':lat, 'longitude':lon, 'name':'X-plane'}).encode())

        os.system('cls')
        print('Latitude: %s longitude: %s'%(lat, lon))
        print('Stellarium reply:')
        print(r.status_code, r.reason)
        print(r.url)
        print(r.text)

        threading.Thread(target=self.receiveUDP, args=()).start()

    def decodeData(self, source):
        #check if it's X-plane data or not
        if source[0:4] != b'RREF': return None
        decoded = {} #return data as ID/Value pair in decoded
        numValues = int( len(source[5:]) / 8 ) #how many values per 8 bytes
        idx = -1
        value = None

        for i in range(0, numValues):
            idx, value = (struct.unpack("<if", source[5+8*i:5+8*(i+1)]))
            decoded[idx] = value
        return decoded

if __name__ == '__main__':
    StellariumToXplane()
