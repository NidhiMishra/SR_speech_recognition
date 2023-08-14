# -*- coding: utf-8 -*-
from __future__ import division
import argparse
import base64
import json

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials
#import free_speech_recognition as sr_free
import speech_recognition as sr_free
import sys


import re
import sys
import time
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import translate
import pyaudio
from six.moves import queue
from SpeechRecognizer import SpeechRecognizer
import threading
from datetime import datetime
import random
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class RecognizerWrapper:
    def __init__(self,freeFlag=False,language="en-US"):
        self.text="" # user speech input
        self.freeFlag=freeFlag
        self.language=language
        #self.getRecognizer()
        self.signalText=[]
        self.mapDict={}
        self.modeChanged=False
        self._start = datetime.now()
        self.stability_counter=[]
        self.transcript_length=[]
        self.max_length=0
        self.begin_time=0
        self.temp=''
        self.done=False
    def getLanguageName(self):
        if self.language=="en-US":
            return "English"
        elif self.language == "de-DE":
            return "German"
        elif self.language=="fr-FR":
            return "French"


    def getRecognizer(self):
        self.recognizer=SpeechRecognizer(freeFlag=self.freeFlag,targetLanguage=self.language)

    def getLanugageMode(self,textList):
        for text in textList:
            if self.getLanguageFlag(text.lower()):
                #print "Change to "+self.getLanguageName()+" Mode!!"
                self.modeChanged=True
                res = self.language
                return res

    def getLanguageFlag(self,sentence):
        for sent in self.signalText:
            if sent in sentence:
                return True
        return False



    def transferGermanText(self,transc):
        transc = transc.replace(u"ß" ,"ss" )
        transc = transc.replace(u"Ü" ,"ue" )
        transc = transc.replace(u"Ö" ,"oe" )
        transc = transc.replace(u"Ä" ,"ae" )
        transc = transc.replace(u"ü" ,"ue" )
        transc = transc.replace(u"ö" ,"oe" )
        transc = transc.replace(u"ä" ,"ae" )
        return transc

    def listen_print_loop(self,responses):
        """Iterates through server responses and prints them.

        The responses passed is a generator that will block until a response
        is provided by the server.

        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.

        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """

        num_chars_printed = 0
        end = False

        for response in responses:
            print("calling loop %f", time.time() - self.begin_time)
            if self.begin_time == 0:
                self.begin_time = time.time()
            #elif (time.time()>self.begin_time+30):
                #end=True
            if self.done==True:
                break
            if not response.results:
                continue

            # There could be multiple results in each response.
            result = response.results[0]
            #self.text=result
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript
            stable= result.stability
            if self.max_length==0 or len(transcript)> self.max_length:
                self.stability_counter.append(stable)
                self.transcript_length.append(len(transcript))
                self.temp=transcript
                self.max_length=len(transcript)
            #self.transcript_content.append(transcript)
            print(stable,end)
            print (self.max_length)
            #if len(self.transcript_length)>3: #or (self.transcript_length[-1]==self.transcript_length[-2] and self.transcript_length[-2]==self.transcript_length[-3] # or (end==True and self.language != "en-US")
            if (len(self.stability_counter)>1 and (float(sum(self.stability_counter)/len(self.stability_counter))>=0.89) and self.language != "en-US" ):

            #if stable >= 0.899 and self.language != "en-US" :
                #response=prev_response
                #result = response.results[0]
                    # self.text=result

                    # Display the transcription of the top alternative.
                #transcript = result.alternatives[0].transcript
                result.is_final=True
                self.stability_counter = []
                self.transcript_length=[]
                self.begin_time=time.time()
            elif len(self.stability_counter)>10:
                self.stability_counter=[]
                self.transcript_length = []
                self.begin_time = time.time()
            #self.text=transcript
            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                #sys.stdout.write(transcript + overwrite_chars + '\r')
                #print(transcript + overwrite_chars + '\r')
                #sys.stdout.flush()

                num_chars_printed = len(transcript)


            else:
                #print(transcript + overwrite_chars)
                if self.language != "en-US":
                    translate_client = translate.Client()

                    # The text to translate
                    text = transcript
                    # The target language
                    target = 'en'

                    # Translates some text into Russian
                    translation = translate_client.translate(
                        text,
                        target_language=target)

                    #print(u'Text: {}'.format(text))
                    #print(chr(text).encode("UTF-8"))
                    print(u'Translation: {}'.format(translation['translatedText']))
                    #sys.stdout.write(u'Translation: {}'.format(translation['translatedText']))
                    self.text = translation['translatedText']
                    #break
                else:
                    print(transcript + overwrite_chars)
                    self.text=transcript
                    #break
                break
                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting..')
                    break

                num_chars_printed = 0
            prev_response=response

    def recognize(self):
        #print "recognize"
        # with self.recognizer.Microphone() as source:
        #     #print "Mic"
        #     self.silentTime=datetime.now()
        #     audio = self.recognizer.listen(source)
        #     #print "get audio"
        #     try:
        #         text,_ = self.recognizer.recognition(audio)
        #         if self.language=="de-DE":
        #             text=self.transferGermanText(text)
        #         self.text=text
        #         #print self.language+": "+self.text
        #     except:
        #         self.text = "NONE"s
        language_code = self.language #'yue-Hant-HK'  # a BCP-47 language tag # hi-IN en-US cmn-Hans-CN ms-MY de-DE ko-KR yue-Hant-HK

        client = speech.SpeechClient()
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)
        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=True)

        with MicrophoneStream(RATE, CHUNK) as stream:
            print ("mic loop")
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)

            responses = client.streaming_recognize(streaming_config, requests)

            # if self.begin_time != 0 and time.time() > self.begin_time + 4:
            #     for response in responses:
            #         if not response.results:
            #             continue
            #
            #         # There could be multiple results in each response.
            #         result = response.results[0]
            #         # self.text=result
            #         if not result.alternatives:
            #             continue
            #         result.is_final=True
            #self.text=responses
            # Now, put the transcription responses to use.
            try:
                print "loop call"
                self.listen_print_loop(responses)
            except:
                print "switch back to english"
                print sys.exc_info()
                if self.language != "en-US":
                    self.text="switch to english"
                else:
                    self.text=""
            #audio_generator.close()


    def noSpeechInput(self):
        if self.text=="":
            return True
        else:
            return False

    def autoSelfChecking(self,timeLimit=180):
        self._end = datetime.now()
        p_time = (self._end - self._start).seconds
        if(p_time >= timeLimit):
            print "Auto Change Back to "+self.getLanguageName()
            self._start = datetime.now()
            return self.language

    def processText(self,gui_client):
        if self.text != "NONE": # already in german mode, get replied german words
            if self.language=="de-DE":
                self.text=self.sentenceCorrection(self.text.lower())
            output=self.getLanguageName().upper()+" Input: "+self.text
            gui_client.client.updateText(output)
            print output

        else: # if not recognized
            gui_client.client.updateText(self.getLanguageName().upper()+" - SPEAK AGAIN")
            print "Fail to Recognize "+self.getLanguageName()+" Input."
            print "Please speak again!"


    def getSignalText(self,SignalText):
        self.signalText=SignalText

    def getMapDict(self,MapDict):
        self.mapDict=MapDict

    # def getChatBot(self,chatbot):
    #     self.chatbot=chatbot
    #
    # def chatbotReply(self,transc):
    #     if self.chatbot:
    #         response=self.chatbot.respond(transc)
    #         return response


    def start(self):
        self.thread = threading.Thread(name=self.language, target=self.recognize)
        self.thread.start()
        if self.language != "en-US":
            while (self.begin_time == 0):
                time.sleep(0.1)

            while (time.time() < self.begin_time + 3):
                print ("listening...")
                time.sleep(1)
            print ("ending...")
            if self.text == "":
                if self.language != "en-US":
                    translate_client = translate.Client()

                    # The text to translate
                    text = self.temp
                    # The target language
                    target = 'en'

                    # Translates some text into Russian
                    translation = translate_client.translate(
                        text,
                        target_language=target)

                    # print(u'Text: {}'.format(text))
                    # print(chr(text).encode("UTF-8"))
                    print(u'Translation: {}'.format(translation['translatedText']))
                    # sys.stdout.write(u'Translation: {}'.format(translation['translatedText']))
                    self.text = translation['translatedText']
                    self.done = True
                    self.thread.start()

                    #raise ValueError('premature closing')
                    # break
                else:
                    self.text = self.temp
                    #raise ValueError('premature closing')
                    self.done=True
                    self.thread.start()

                print (self.text)
        else:
            self.thread.join()


    def join(self):
        self.thread.join()

    def wordCorrection(self,token):
        for key, wordList in self.mapDict.items():
            for word in wordList:
                if word==token:
                    # print "changed ",token," to ",key
                    return key
        return None

    def sentenceCorrection(self,sentence):
        tokens=sentence.split()
        res=[]
        for token in tokens:
            word=self.wordCorrection(token)
            if word!=None:
                res.append(word)
            else:
                res.append(token)
        ans=" ".join(res)
        # print "mapped sentence: ",ans
        return ans

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
# [END audio_stream]