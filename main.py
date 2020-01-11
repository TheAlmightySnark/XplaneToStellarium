from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

from kivy.base import runTouchApp
from kivy.app import App

from kivy.core.window import Window

#Stellarium related imports
from urllib.parse import urlencode
import requests

#X-plane related imports
import struct #structure byte arrays for X-plane
import socket #UDP connection
import threading #used for multithreading

#RREF requsts to X-plane. position in array will determine ID send back from X-plane.
xpDrefs = [
    (1, "sim/flightmodel/position/latitude", float), #ID, datarate, dataref, datatype
    (1, "sim/flightmodel/position/longitude", float), #ID, datarate, dataref, datatype
]

sock = None
xplaneIp = None
xplanePort = None

#IP labels
txtXpIP = None
txtXpPort = None
lblLat = None
lblLong = None

class XplaneToStellarium(App):

    def build(self):
        global txtXpIP, txtXpPort, lblLat, lblLong
        boxLayout = BoxLayout(orientation='vertical')

        txtXpIP = TextInput(text='127.0.0.1', multiline=False, size_hint_y=None, height='32dp')
        txtXpPort = TextInput(text='49000', multiline=False, size_hint_y=None, height='32dp')
        btnStart = Button(text="start")
        btnStart.bind(on_press=self.onStartClickEvent)

        lblLat = Label(text='Latitude', max_lines=1, size_hint_y=None, height='32dp')
        lblLong = Label(text='longtitude', max_lines=1, size_hint_y=None, height='32dp')

        boxLayout.add_widget(txtXpIP)
        boxLayout.add_widget(txtXpPort)
        boxLayout.add_widget(btnStart)
        boxLayout.add_widget(lblLat)
        boxLayout.add_widget(lblLong)


        Window.size = (300, 200)
        return boxLayout

    #eventhandlers
    def onStartClickEvent(self, instance):
        global sock, xplaneIp, xplanePort, txtXpIP, txtPort
        print("clicketyclick")

        if not sock:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            xplaneIp = txtXpIP.text
            xplanePort = int(txtXpPort.text)

            print("opening socket with %s and %s"%(xplaneIp, xplanePort))

            for idx, item in enumerate(xpDrefs):
                self.requestDref(idx, item[0], item[1])

    #build RREF according to X-plane 10/Instructions/Sending Data To X-plane.rtf
    def requestDref(self, id, rate, dref):
        padstring = '<5sii400s' #padding to 413 bytes according to the struct packing page(python)
        type = b"RREF\x00" #5 byte data type including null terminator

        self.sendUDP(struct.pack(padstring, type, rate, id, dref.encode()))


    def sendUDP(self, message):
        global sock, xplaneIp, xplanePort

        sock.sendto(message, (xplaneIp, xplanePort))

        threading.Thread(target=self.receiveUDP, args=()).start()

    def receiveUDP(self):
        global sock, lblLat, lblLong

        data, adress = sock.recvfrom(1024)

        decoded = self.decodeData(data)

        if decoded is None:
            print("No X-plane UDP data received")
            threading.Thread(target=self.receiveUDP, args=()).start()
            return

        for k, v in decoded.items():
            if k == 0:
                lblLat.text = str(float(v))
                continue
            if k == 1:
                lblLong.text = str(float(v))
                continue

        r = requests.post("http://localhost:8090/api/location/setlocationfields", params=urlencode({'latitude': lblLat.text, 'longitude':lblLong.text}).encode())
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
    XplaneToStellarium().run()
