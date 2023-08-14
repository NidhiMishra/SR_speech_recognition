# -*- coding: utf-8 -*-

import threading
import aiml
import time
#language#

#from langdetect import detect

import sys
sys.path.append("../../i2p/i2pThrift/gen-py")
sys.path.append("../../i2p/i2pThrift/tools/py")

import Inputs.SpeechGuiService as GUI_Service
import Inputs.SpeechRecognitionService as SR_Service
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
import os
import config

#For Volume Control#
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#For Volume Control#

class SpeechRecognition:
    def __init__(self):
        self.language_changed=False
        self.build()

    def build(self):
        self.translator=Translator()
        self.getMultiRecognizer(freeFlag=True)
        self.getThriftClient()
        self.loadSignalText()
        self.loadGermanChatbot()
        self.loadDefaultLanguage()

    def getMultiRecognizer(self,freeFlag=False):
        self.EnglishRecognizer=RecognizerWrapper(freeFlag=freeFlag,language="en-US")
        self.GermanRecognizer=RecognizerWrapper(freeFlag=freeFlag,language="de-DE")
        self.FrenchRecognizer=RecognizerWrapper(freeFlag=freeFlag,language="fr-FR")
        self.ChineseRecognizer = RecognizerWrapper(freeFlag=freeFlag, language="zh-CN")

    def loadSignalText(self):
        self.takePhotoText=[
            "take a picture",
           "take a photo",
           "take my picture",
           "take my photo",
           "take me a picture",
           "take me a photo"]

        self.reportObjectText=[
            "what do you see",
           "what have you seen",
           "could you tell me what you have seen",
           "what objects have you seen",
           "what object have you seen",
           #"what objects do you see",
           #"what object do you see",
           #"name the objects"
           ]

        speakEnglishText=[
            "speak english",
		   "can you speak english",
		   "you speak english",
           "talk english",
		   "speak in english",
		   "talk in english",
           "communicate in english",
           "sprich englisch",
		   "kennst du englisch sprechen",
		   "kannst du englisch",
           "sprechen sie englisch",
		   "sprichst du englisch",
		   "kannst du englisch",
		   "kannst du englisch mit mir reden"]

        speakGermanText=["speak german",
           "talk german",
		   "speak in german",
		   "talk in german",
           "communicate in german",
		   "kennst du deutsch sprechen",
		   "kennst du deutsch",
		   "kannst du deutsch",
           "deutsch sprechen",
           "sprechen deutsch",
		   "deutsch werden",
		   "sprichst du deutsch"]

        speakFrenchText=["speak french",
			"can you speak french",
			"do you speak french",
            "talk french",
		    "speak in french",
		    "talk in french",
            "communicate in french"]

        speakChineseText = ["speak chinese",
                           "can you speak chinese",
                           "do you speak chinese",
                           "talk chinese",
                           "speak in chinese",
                           "talk in chinese",
                           "communicate in chinese"]

        germanMapDict={"nadja":["nadja","natia","nadia","nadya"],
         "thalmann":["thalmann","thalman","dhalmann","dhalman","dahlmann",\
                     "dahlman","talman","talmann","dallmann","dannemann"],
         "lady":["ada","ida","lady","lily","edda","pedalo","egal"],
         "lovelace":["lovelace","lackless","loveless","willis","novelas","laavless"]
        }
        self.EnglishRecognizer.getSignalText(speakEnglishText)
        self.GermanRecognizer.getSignalText(speakGermanText)
        self.FrenchRecognizer.getSignalText(speakFrenchText)
        self.ChineseRecognizer.getSignalText(speakChineseText)
        self.GermanRecognizer.getMapDict(germanMapDict)



    def loadGermanChatbot(self):
        try:
            self.germanChat = aiml.Kernel()
            self.germanChat.learn("std-startup_German_test.xml")
            self.germanChat.respond("load aiml b")
        except:
            print "German Chatbot Error"

    def germanChatbotReply(self,transc):
        response=self.germanChat.respond(transc)
        return response


    def getThriftClient(self):
        import socket
        IP = socket.gethostbyname(socket.gethostname())
        print IP
        self.sr_client = ThriftTools.ThriftClient(IP, 1200,SR_Service, 'Speech Recognition')
        self.rl_client = ThriftTools.ThriftClient(IP, Inputs.constants.DEFAULT_SPEECHRECOGNITION_SERVICE_PORT,SR_Service, 'Speech Recognition for Reactive Layer')
        self.gui_client = ThriftTools.ThriftClient(IP,Inputs.constants.DEFAULT_SPEECHGUI_PORT,GUI_Service,'Speech GUI')
        self.getThriftConnection()

    def getThriftConnection(self):
        if not self.sr_client.connected:
            self.sr_client.connect()
        if not self.rl_client.connected:
            self.rl_client.connect()
        if not self.gui_client.connected:
            self.gui_client.connect()

    def loadDefaultLanguage(self):
        # try:
        #     with file("defaultLanguage.txt","rb") as f:
        #         self.defaultLanguage = f.read()
        #         print "Default Language: ",self.defaultLanguage
        #         self.sr_client.client.LanguageRecognized('Microphone',
        #                 I2PTime.getTimeStamp(), self.defaultLanguage)
        # except:
        self.defaultLanguage="en-US"
        #self.defaultLanguage = "de-DE"
        print "Default Language: ",self.defaultLanguage
        self.sr_client.client.LanguageRecognized('Microphone',
                    I2PTime.getTimeStamp(), self.defaultLanguage)

    # def storeDefaultLanguage(self,text):
    #     with open('defaultLanguage.txt', 'wb') as f:
    #         f.write(text)


    def getTakingPhotoFlag(self,sentence):
        for sent in self.takePhotoText:
            if sent in sentence:
                return True
        return False

    def getReportObjectFlag(self,sentence):
        for sent in self.reportObjectText:
            if sent in sentence:
                return True
        return False



    def startThreading(self):
        self.nonEnglishRecognizer=RecognizerWrapper(freeFlag=False, language=self.defaultLanguage)
        self.nonEnglishRecognizer.start()

        # self.EnglishRecognizer.start()
        # self.GermanRecognizer.start()
        # self.FrenchRecognizer.start()
        # self.ChineseRecognizer.start()

    def joinThreading(self):
        self.nonEnglishRecognizer.join()
        # self.EnglishRecognizer.join()
        # self.GermanRecognizer.join()
        # self.FrenchRecognizer.join()
        # self.ChineseRecognizer.join()

    def isNoSpeech(self):
        if self.EnglishRecognizer.noSpeechInput() and \
                self.GermanRecognizer.noSpeechInput() and \
                self.FrenchRecognizer.noSpeechInput() and \
                self.ChineseRecognizer.noSpeechInput():
            return True
        return False

    def setDefaultLanguage(self,language):
        self.defaultLanguage = language
        #self.storeDefaultLanguage(self.defaultLanguage)
        self.sr_client.client.LanguageRecognized('Microphone', I2PTime.getTimeStamp(), self.defaultLanguage)
        print "Default Language: ",self.defaultLanguage,"\n"

    def switchLanguageMode(self):
        E_Start=self.EnglishRecognizer.getLanugageMode([self.EnglishRecognizer.text,
                                               self.GermanRecognizer.text])
        G_Start=self.GermanRecognizer.getLanugageMode([self.EnglishRecognizer.text,
                                                      self.GermanRecognizer.text])
        F_Start=self.FrenchRecognizer.getLanugageMode([self.EnglishRecognizer.text])
        C_Start = self.ChineseRecognizer.getLanugageMode([self.EnglishRecognizer.text])

        if E_Start:
            print "Switch to English Mode"
            self.setDefaultLanguage(E_Start)
        elif G_Start:
            print "Switch to German Mode"
            self.setDefaultLanguage(G_Start)
        elif F_Start:
            print "Switch to French Mode"
            self.setDefaultLanguage(F_Start)
        elif C_Start:
            print "Switch to Chinese Mode"
            self.setDefaultLanguage(C_Start)

    def printRecognizedText(self):
        print "English Transcription: ",self.EnglishRecognizer.text
        print "German Transcription: ",self.GermanRecognizer.text
        print "French Transcription: ",self.FrenchRecognizer.text
        print "Chinese Transcription: ", self.ChineseRecognizer.text

    def reset(self):
        self.EnglishRecognizer.text=""
        self.GermanRecognizer.text=""
        self.FrenchRecognizer.text=""
        self.ChineseRecognizer.text = ""
        self.EnglishRecognizer.modeChanged=False
        self.GermanRecognizer.modeChanged=False
        self.FrenchRecognizer.modeChanged=False
        self.ChineseRecognizer.modeChanged=False

    def autoResetEnglishMode(self):
        while self.isNoSpeech() and self.defaultLanguage!="en-US" and self.EnglishRecognizer.thread.isAlive():
            mode=self.EnglishRecognizer.autoSelfChecking(timeLimit=180)
            if mode:
                self.setDefaultLanguage(mode)

    def processGermanText(self):
        defaultGermanWords=['ja','ja ich spreche deutsch', 'Ja, ich kann deutsch sprechen',
                            'ja, mache ich']
        sentenceToSend=""
        if self.GermanRecognizer.modeChanged: # at the beginning, change language mode to German, speak something
            sentenceToSend = random.choice(defaultGermanWords)
        elif self.defaultLanguage==self.GermanRecognizer.language:
            self.GermanRecognizer.processText(self.gui_client)
            if self.GermanRecognizer.text!="NONE":
                sentenceToSend=self.germanChatbotReply(self.GermanRecognizer.text)
        if sentenceToSend != "":
            sentenceToSend = "GERMAN:::"+ sentenceToSend
            self.rl_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceToSend, 0.0)


    def processFrenchText(self):
        defaultFrenchWords=['can you speak french','can you speak french']
        sentenceToSend=""
        if self.FrenchRecognizer.modeChanged: # at the beginning, change language mode to German, speak something
            sentenceToSend = random.choice(defaultFrenchWords)
        elif self.defaultLanguage==self.FrenchRecognizer.language:
            self.FrenchRecognizer.processText(self.gui_client)
            if self.FrenchRecognizer.text!="NONE":
                sentenceToSend=self.FrenchTranslation(self.FrenchRecognizer.text)
        if sentenceToSend != '':
            self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceToSend, 0.0)

    def processChineseText(self):
        defaultChineseWords=['can you speak chinese','can you speak chinese']
        sentenceToSend=""
        if self.ChineseRecognizer.modeChanged: # at the beginning, change language mode to German, speak something
            sentenceToSend = random.choice(defaultChineseWords)
        elif self.defaultLanguage==self.ChineseRecognizer.language:
            self.ChineseRecognizer.processText(self.gui_client)
            if self.ChineseRecognizer.text!="NONE":
                sentenceToSend=self.ChineseTranslation(self.ChineseRecognizer.text)
        if sentenceToSend != '':
            self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceToSend, 0.0)

    def processEnglishText(self):
        if self.getTakingPhotoFlag(self.EnglishRecognizer.text):
            self.rl_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), "TAKEPIC", 0.0)
            print "send TakePic to reactive layer!!"
            return
        if self.getReportObjectFlag(self.EnglishRecognizer.text):
            self.rl_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), "REPORTOBJ", 0.0)
            print "send ReportObject to reactive layer!!"
            return
        defaultEnglishWords=['can you speak English','can you speak english' ]
        sentenceToSend=""
        if self.EnglishRecognizer.modeChanged: # at the beginning, change language mode to German, speak something
            sentenceToSend = random.choice(defaultEnglishWords)
        elif self.defaultLanguage==self.EnglishRecognizer.language:
            self.EnglishRecognizer.processText(self.gui_client)
            #if self.EnglishRecognizer.text!="NONE":
            sentenceToSend = self.EnglishRecognizer.text
        if sentenceToSend != '':
            self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceToSend, 0.0)

    def FrenchTranslation(self,text,targetLanguage="en",freeFlag=True):
        try:
            translation=str(self.translator.translation(text,targetLanguage,freeFlag))
            print "French Translation: ", translation
            return translation

        except:
            print "No French translation"
            return ""

    def ChineseTranslation(self,text,targetLanguage="en",freeFlag=True):
        try:
            translation=str(self.translator.translation(text,targetLanguage,freeFlag))
            print "Chinese Translation: ", translation
            return translation

        except:
            print "No Chinese translation"
            return ""

    def processText(self):
        if self.language_changed==False:
            sentenceToSend = self.nonEnglishRecognizer.text.lower()
            sentenceToSend=sentenceToSend.replace("&#39;","'")
            #print(sentenceToSend)
            if "speak french" in sentenceToSend:
                self.defaultLanguage = "fr-FR"
                sentenceToSend = "language changed to french"
            elif "speak german" in sentenceToSend and self.defaultLanguage != "de-DE" :
                self.defaultLanguage = "de-DE"
                sentenceToSend = "language changed to german"


            elif "speak chinese" in sentenceToSend and self.defaultLanguage != "cmn-Hans-CN":
                self.defaultLanguage = "cmn-Hans-CN"
                sentenceToSend = "language changed to chinese"
            elif "speak mandarin" in sentenceToSend and self.defaultLanguage != "cmn-Hans-CN":
                self.defaultLanguage = "cmn-Hans-CN"
                sentenceToSend = "language changed to chinese"
            #ja-JP
            elif "speak japanese" in sentenceToSend and self.defaultLanguage != "ja-JP":
                self.defaultLanguage = "ja-JP"
                sentenceToSend = "language changed to japanese"
            elif "speak hindi" in sentenceToSend and self.defaultLanguage != "hi-IN":
                self.defaultLanguage = "hi-IN"
                sentenceToSend = "language changed to hindi"
            ### korean added by nidhi###
            elif "speak korean" in sentenceToSend and self.defaultLanguage != "ko-KR":
                self.defaultLanguage = "ko-KR"
                sentenceToSend = "language changed to korean"
            elif ("english" in sentenceToSend or "switch to english" in sentenceToSend) and self.defaultLanguage != "en-US" :
                self.defaultLanguage = "en-US"
                sentenceToSend = "language changed to english"
        else:
            sentenceToSend = "language changed from the touch screen"
        if sentenceToSend != "":
            self.gui_client.client.updateText(sentenceToSend)
            if self.getTakingPhotoFlag(sentenceToSend):
                self.rl_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), "TAKEPIC", 0.0)
                print "send TakePic to reactive layer!!"
                return
            if self.getReportObjectFlag(sentenceToSend):
                self.rl_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), "REPORTOBJ", 0.0)
                print "send ReportObject to reactive layer!!"
                return
            sentenceToSend=sentenceToSend+"#"+self.defaultLanguage

            #if self.defaultLanguage == "fr-FR"
            self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceToSend, 0.0)
        #GERMAN#
        # if self.defaultLanguage==self.GermanRecognizer.language:
        #     self.processGermanText()
        # #FRENCH#
        # elif self.defaultLanguage==self.FrenchRecognizer.language:
        #     self.processFrenchText()
        # #ENGLISH#
        # elif self.defaultLanguage==self.EnglishRecognizer.language:
        #     self.processEnglishText()
        # #CHINESE#
        # elif self.defaultLanguage==self.ChineseRecognizer.language:
        #     self.processChineseText()

    def main(self):
        while True:
            try:
                self.getThriftConnection()
                while True:
                    user_available = os.path.join(config.development_folder, "user_available.txt")
                    language_txt = os.path.join(config.development_folder, "language.txt")

                    #if os.path.isfile("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\user_available.txt"):
                    if os.path.isfile(user_available):
                        self.language_changed = False
                        print "Start Listening"
                        self.startThreading()

                        # if os.path.isfile("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\language.txt"):
                        if os.path.isfile(language_txt):
                            #with open('G:\IMI-PROJECTS\i2p_Nadine_Robot\development\language.txt') as f:
                            with open(language_txt) as f:

                                content = f.readlines()
                                f.close()
                                #os.remove("G:\IMI-PROJECTS\i2p_Nadine_Robot\development\language.txt")
                                os.remove(language_txt)
                                if content[0] == "English":
                                    self.defaultLanguage = "en-US"
                                elif content[0] == "German":
                                    self.defaultLanguage = "de-DE"
                                elif content[0] == "French":
                                    self.defaultLanguage = "fr-FR"
                                elif content[0] == "Chinese":
                                    self.defaultLanguage = "cmn-Hans-CN"
                                elif content[0] == "Hindi":
                                    self.defaultLanguage = "hi-IN"
                                elif content[0] == "Korean":
                                    self.defaultLanguage = "ko-KR"
                                #language_set=True
                            self.language_changed=True
                            print ("ignore text")
                        print ("text set")
                        #self.printRecognizedText()
                        print "&&&&&&&&&&&&&&&&&&&&&&&"
                        #self.switchLanguageMode()
                        if self.nonEnglishRecognizer.done != True:
                            self.processText()
                            self.reset()
                        print "&&&&&&&&&&&&&&&&&&&&&&&\n"

            except Exception as error:
                #print sys.exc_info()
                print('caught this error: ' + repr(error))
                #if os.path.isfile("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\language.txt"):
                if os.path.isfile(language_txt):
                    # with open('G:\IMI-PROJECTS\i2p_Nadine_Robot\development\language.txt') as f:
                    with open(language_txt) as f:

                        content = f.readlines()
                        f.close()
                        #os.remove("G:\IMI-PROJECTS\i2p_Nadine_Robot\development\language.txt")
                        os.remove(language_txt)
                        if content[0] == "English":
                            self.defaultLanguage = "en-US"
                        elif content[0] == "German":
                            self.defaultLanguage = "de-DE"
                        elif content[0] == "French":
                            self.defaultLanguage = "fr-FR"
                        elif content[0] == "Chinese":
                            self.defaultLanguage = "cmn-Hans-CN"
                        elif content[0] == "Hindi":
                            self.defaultLanguage = "hi-IN"
                        elif content[0] == "Korean" or content[0] == "korean":
                            self.defaultLanguage = "ko-KR"
                            # language_set=True
                    self.language_changed = True
                    print ("ignore text")
                #else:
                if self.nonEnglishRecognizer.done==True:
                    print ("text set")
                    # self.printRecognizedText()
                    print "&&&&&&&&&&&&&&&&&&&&&&&"
                    # self.switchLanguageMode()
                    self.processText()
                    self.reset()
                    print "&&&&&&&&&&&&&&&&&&&&&&&\n"
                #print("Could not recognize from I2P")
                continue


if __name__=="__main__":
    speech=SpeechRecognition()
    speech.main()
