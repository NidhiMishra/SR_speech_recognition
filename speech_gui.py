from Tkinter import *
import os
import sys
import re
sys.path.append("../../i2p/i2pThrift/gen-py")
sys.path.append("../../i2p/i2pThrift/tools/py")

import Inputs.SpeechGuiService as GUI_Service
from Inputs.ttypes import *
import Inputs.constants

from I2P.ttypes import *
from thrift.transport import TSocket
import ThriftTools
import time

import socket

IP = socket.gethostbyname(socket.gethostname())
print IP

class Application(Frame):
    def start(self):
        #self.text=Text(width = 20, height=4, font=("Helvetica",40))
        self.text=Text(font=("Helvetica",40))
        #self.text.insert(1.0,self.content)
        self.text.pack()

    def editText(self, sentence):
        self.text.delete(1.0,"end")
        self.text.insert(1.0,sentence)
        self.callback=self.text.after(2000,self.clear)

    def clear(self):
        self.text.delete(1.0,"end")
        for name in self.text.tag_names():
            self.text.tag_delete(name)

    def update(self):
        try:
            if self.gui_handler.text!=None and not re.match(r"\W+",self.gui_handler.text):
                root.after_cancel(self.callback)
                self.editText(self.gui_handler.text)
                if self.gui_handler.text.endswith("SPEAK AGAIN"):
                    self.text.tag_add(self.gui_handler.text,1.0,"end")
                    self.text.tag_config(self.gui_handler.text,background="red",foreground="blue")
                self.gui_handler.text=None
            root.after(500, self.update) # every second...
        except:
            print sys.exc_info()
            pass



    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.start()
        self.editText("Begin")
        import socket
        IP = socket.gethostbyname(socket.gethostname())
        print IP

        self.gui_handler = GUIHandler()
        self.gui_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_SPEECHGUI_PORT,GUI_Service,self.gui_handler,'Speech GUI Service',IP)
        #self.gui_server = ThriftTools.ThriftServerThread(1500,GUI_Service,self.gui_handler,'Speech GUI Service',IP)
        self.gui_server.start()

class GUIHandler:
    def __init__(self):
        self.text=None
        #self.text="SPEAK AGAIN"

    def __del__(self):
        return

    def updateText(self, text):
        print "Received Text: %s" % text
        self.text=text


if __name__=="__main__":

    root = Tk()
    root.title("SPEECH INPUT TO NADINE")
    #root.attributes('-fullscreen', True)
    w, h = root.winfo_screenwidth()/4, root.winfo_screenheight()/5
    root.geometry("%dx%d+0+0" % (w, h))
    app = Application(master=root)
    #app.editText("begin")
    app.update()
    root.mainloop()
    #root.destroy()





            
