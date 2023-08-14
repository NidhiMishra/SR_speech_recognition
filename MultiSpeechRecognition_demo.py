# -*- coding: utf-8 -*-

import threading
import aiml
import time
# language#

# from langdetect import detect

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

# to ease client server creation in python
import ThriftTools
import I2PTime
import random

from Translator import Translator
from RecognizerWrapper import RecognizerWrapper
import os


class SpeechRecognition:
    def __init__(self):
        self.language_changed = False
        self.demo = ''
        self.build()

    def build(self):
        self.translator = Translator()
        self.getMultiRecognizer(freeFlag=True)
        self.getThriftClient()
        self.loadSignalText()
        self.loadGermanChatbot()
        self.loadDefaultLanguage()

    def getMultiRecognizer(self, freeFlag=False):
        self.EnglishRecognizer = RecognizerWrapper(freeFlag=freeFlag, language="en-US")
        self.GermanRecognizer = RecognizerWrapper(freeFlag=freeFlag, language="de-DE")
        self.FrenchRecognizer = RecognizerWrapper(freeFlag=freeFlag, language="fr-FR")
        self.ChineseRecognizer = RecognizerWrapper(freeFlag=freeFlag, language="zh-CN")

    def loadSignalText(self):
        self.takePhotoText = [
            "take a picture",
            "take a photo",
            "take my picture",
            "take my photo",
            "take me a picture",
            "take me a photo"]

        self.reportObjectText = [
            "what do you see",
            "what have you seen",
            "could you tell me what you have seen",
            "what objects have you seen",
            "what object have you seen",
            "what objects do you see",
            "what object do you see",
            "name the objects"
        ]

        speakEnglishText = [
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

        speakGermanText = ["speak german",
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

        speakFrenchText = ["speak french",
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

        germanMapDict = {"nadja": ["nadja", "natia", "nadia", "nadya"],
                         "thalmann": ["thalmann", "thalman", "dhalmann", "dhalman", "dahlmann", \
                                      "dahlman", "talman", "talmann", "dallmann", "dannemann"],
                         "lady": ["ada", "ida", "lady", "lily", "edda", "pedalo", "egal"],
                         "lovelace": ["lovelace", "lackless", "loveless", "willis", "novelas", "laavless"]
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

    def germanChatbotReply(self, transc):
        response = self.germanChat.respond(transc)
        return response

    def getThriftClient(self):
        import socket
        IP = socket.gethostbyname(socket.gethostname())
        print IP
        self.sr_client = ThriftTools.ThriftClient(IP, 1200, SR_Service, 'Speech Recognition')
        self.rl_client = ThriftTools.ThriftClient(IP, Inputs.constants.DEFAULT_SPEECHRECOGNITION_SERVICE_PORT,
                                                  SR_Service, 'Speech Recognition for Reactive Layer')
        self.gui_client = ThriftTools.ThriftClient(IP, Inputs.constants.DEFAULT_SPEECHGUI_PORT, GUI_Service,
                                                   'Speech GUI')
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
        self.defaultLanguage = "en-US"
        # self.defaultLanguage = "zh-CN"
        print "Default Language: ", self.defaultLanguage
        self.sr_client.client.LanguageRecognized('Microphone',
                                                 I2PTime.getTimeStamp(), self.defaultLanguage)

    # def storeDefaultLanguage(self,text):
    #     with open('defaultLanguage.txt', 'wb') as f:
    #         f.write(text)

    def getTakingPhotoFlag(self, sentence):
        for sent in self.takePhotoText:
            if sent in sentence:
                return True
        return False

    def getReportObjectFlag(self, sentence):
        for sent in self.reportObjectText:
            if sent in sentence:
                return True
        return False

    def startThreading(self):
        self.nonEnglishRecognizer = RecognizerWrapper(freeFlag=False, language=self.defaultLanguage)
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

    def setDefaultLanguage(self, language):
        self.defaultLanguage = language
        # self.storeDefaultLanguage(self.defaultLanguage)
        self.sr_client.client.LanguageRecognized('Microphone', I2PTime.getTimeStamp(), self.defaultLanguage)
        print "Default Language: ", self.defaultLanguage, "\n"

    def switchLanguageMode(self):
        E_Start = self.EnglishRecognizer.getLanugageMode([self.EnglishRecognizer.text,
                                                          self.GermanRecognizer.text])
        G_Start = self.GermanRecognizer.getLanugageMode([self.EnglishRecognizer.text,
                                                         self.GermanRecognizer.text])
        F_Start = self.FrenchRecognizer.getLanugageMode([self.EnglishRecognizer.text])
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
        print "English Transcription: ", self.EnglishRecognizer.text
        print "German Transcription: ", self.GermanRecognizer.text
        print "French Transcription: ", self.FrenchRecognizer.text
        print "Chinese Transcription: ", self.ChineseRecognizer.text

    def reset(self):
        self.EnglishRecognizer.text = ""
        self.GermanRecognizer.text = ""
        self.FrenchRecognizer.text = ""
        self.ChineseRecognizer.text = ""
        self.EnglishRecognizer.modeChanged = False
        self.GermanRecognizer.modeChanged = False
        self.FrenchRecognizer.modeChanged = False
        self.ChineseRecognizer.modeChanged = False

    def autoResetEnglishMode(self):
        while self.isNoSpeech() and self.defaultLanguage != "en-US" and self.EnglishRecognizer.thread.isAlive():
            mode = self.EnglishRecognizer.autoSelfChecking(timeLimit=180)
            if mode:
                self.setDefaultLanguage(mode)

    def processGermanText(self):
        defaultGermanWords = ['ja', 'ja ich spreche deutsch', 'Ja, ich kann deutsch sprechen',
                              'ja, mache ich']
        sentenceToSend = ""
        if self.GermanRecognizer.modeChanged:  # at the beginning, change language mode to German, speak something
            sentenceToSend = random.choice(defaultGermanWords)
        elif self.defaultLanguage == self.GermanRecognizer.language:
            self.GermanRecognizer.processText(self.gui_client)
            if self.GermanRecognizer.text != "NONE":
                sentenceToSend = self.germanChatbotReply(self.GermanRecognizer.text)
        if sentenceToSend != "":
            sentenceToSend = "GERMAN:::" + sentenceToSend
            self.rl_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceToSend, 0.0)

    def processFrenchText(self):
        defaultFrenchWords = ['can you speak french', 'can you speak french']
        sentenceToSend = ""
        if self.FrenchRecognizer.modeChanged:  # at the beginning, change language mode to German, speak something
            sentenceToSend = random.choice(defaultFrenchWords)
        elif self.defaultLanguage == self.FrenchRecognizer.language:
            self.FrenchRecognizer.processText(self.gui_client)
            if self.FrenchRecognizer.text != "NONE":
                sentenceToSend = self.FrenchTranslation(self.FrenchRecognizer.text)
        if sentenceToSend != '':
            self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceToSend, 0.0)

    def processChineseText(self):
        defaultChineseWords = ['can you speak chinese', 'can you speak chinese']
        sentenceToSend = ""
        if self.ChineseRecognizer.modeChanged:  # at the beginning, change language mode to German, speak something
            sentenceToSend = random.choice(defaultChineseWords)
        elif self.defaultLanguage == self.ChineseRecognizer.language:
            self.ChineseRecognizer.processText(self.gui_client)
            if self.ChineseRecognizer.text != "NONE":
                sentenceToSend = self.ChineseTranslation(self.ChineseRecognizer.text)
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
        defaultEnglishWords = ['can you speak English', 'can you speak english']
        sentenceToSend = ""
        if self.EnglishRecognizer.modeChanged:  # at the beginning, change language mode to German, speak something
            sentenceToSend = random.choice(defaultEnglishWords)
        elif self.defaultLanguage == self.EnglishRecognizer.language:
            self.EnglishRecognizer.processText(self.gui_client)
            # if self.EnglishRecognizer.text!="NONE":
            sentenceToSend = self.EnglishRecognizer.text
        if sentenceToSend != '':
            self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceToSend, 0.0)

    def FrenchTranslation(self, text, targetLanguage="en", freeFlag=True):
        try:
            translation = str(self.translator.translation(text, targetLanguage, freeFlag))
            print "French Translation: ", translation
            return translation

        except:
            print "No French translation"
            return ""

    def ChineseTranslation(self, text, targetLanguage="en", freeFlag=True):
        try:
            translation = str(self.translator.translation(text, targetLanguage, freeFlag))
            print "Chinese Translation: ", translation
            return translation

        except:
            print "No Chinese translation"
            return ""

    def processText(self):
        if self.language_changed == False:
            sentenceToSend = self.demo  # self.nonEnglishRecognizer.text.lower()
            sentenceToSend = sentenceToSend.replace("&#39;", "'")
            # print(sentenceToSend)
            if "speak french" in sentenceToSend:
                self.defaultLanguage = "fr-FR"
                sentenceToSend = "language changed to french"
            elif "speak german" in sentenceToSend and self.defaultLanguage != "de-DE":
                self.defaultLanguage = "de-DE"
                sentenceToSend = "language changed to german"


            elif "speak chinese" in sentenceToSend and self.defaultLanguage != "cmn-Hans-CN":
                self.defaultLanguage = "cmn-Hans-CN"
                sentenceToSend = "language changed to chinese"
            # ja-JP
            elif "speak japanese" in sentenceToSend and self.defaultLanguage != "ja-JP":
                self.defaultLanguage = "ja-JP"
                sentenceToSend = "language changed to japanese"
            elif "speak hindi" in sentenceToSend and self.defaultLanguage != "hi-IN":
                self.defaultLanguage = "hi-IN"
                sentenceToSend = "language changed to hindi"
            elif (
                    "english" in sentenceToSend or "switch to english" in sentenceToSend) and self.defaultLanguage != "en-US":
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
            sentenceToSend = sentenceToSend + "#" + self.defaultLanguage
            self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceToSend, 0.0)
        # GERMAN#
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
                    demo_num = raw_input('sentence: ');

                    ###for video done by nidhi###
                    # demo_num = raw_input('sentence: ');
                    # num = raw_input('num: ');
                    #
                    # if int(num) <= 250:
                    #     if int(num) == 1:
                    #         demo_num = "demo*"+demo_num + "#en-US"
                    #     elif int(num) == 2:
                    #         demo_num = "demo*"+demo_num + "#cmn-Hans-CN"
                    #     elif int(num) == 3:
                    #         demo_num = "demo*"+demo_num + "#hi-IN"
                    #     elif int(num) == 4:
                    #         demo_num = "demo*"+demo_num + "#ko-KR"
                    #     self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), demo_num, 0.0)

                    ###for video done by nidhi###


                    if int(demo_num) <= 250:
                        print "in loop if"
                        if int(demo_num) <= 200:
                            demo_num = demo_num + "#en-US"
                        else:
                            demo_num = demo_num + "#en-US" ## "#cmn-hans-cn"
                        self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), demo_num, 0.0)
                    ##############
                    # elif demo_num == '4' or demo_num == '5' or demo_num == '6':
                    #     print "in loop if"
                    #     demo_num = demo_num + "#hi-IN"
                    #     self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), demo_num, 0.0)
                    else:
                        print "in loop else"
                        # self.demo = self.demo + "#en-US"
                        print "Start Listening"
                        self.startThreading()
                        print ("text set")
                        print "&&&&&&&&&&&&&&&&&&&&&&&"
                        if self.nonEnglishRecognizer.done != True:
                            self.processText()
                            self.reset()
                        print "&&&&&&&&&&&&&&&&&&&&&&&\n"
                        self.sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), self.demo, 0.0)
                    time.sleep(0.2)
            except Exception as error:
                print(error)


if __name__ == "__main__":
    speech = SpeechRecognition()
    speech.main()
