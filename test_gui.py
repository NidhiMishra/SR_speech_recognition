import sys
sys.path.append("../../i2p/i2pThrift/gen-py")
sys.path.append("../../i2p/i2pThrift/tools/py")

import Inputs.SpeechGuiService as GUI_Service
from Inputs.ttypes import *
import Inputs.constants

from thrift import Thrift
from I2P.ttypes import *
from thrift.transport import TSocket

#to ease client server creation in python
import ThriftTools
import I2PTime
import random

from Translator import Translator
from RecognizerWrapper import RecognizerWrapper
from Translator import Translator

class TestGUI:
    def __init__(self):
        import socket
        IP = socket.gethostbyname(socket.gethostname())
        print IP
        self.gui_client = ThriftTools.ThriftClient(IP,1500,GUI_Service,'Speech GUI')
        if not self.gui_client.connected:
            self.gui_client.connect()
        self.translateTool=Translator()

    def update(self,output):
        self.gui_client.client.updateText(output)


if __name__=="__main__":
    test=TestGUI()
    idx=0
    while True:
        text=raw_input("Input:")
        if idx%3==0:
            text=test.translateTool.free_translation(text)
        elif idx%3==1:
            text=test.translateTool.free_translation(text,targetLanguage="de")
        test.update(text)
        idx+=1