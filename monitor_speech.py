#!/usr/bin/python
import subprocess, sys
import time
import threading

class monitor_speech:
    def __init__(self):
        ## command to run - tcp only ##
        self.cmd = "python -u MultiSpeechRecognition.py"
        self.speech_keywords = ['loop call', '&&&&&&&&&&&&&&&&&&&&&&&', '&&&&&&&&&&&&&&&&&&&&&&&', 'Default Language:  en-US']
        self.speech_good = True
        self.speech_output =""
        self.restart_flag = True
        self.time_out = 80

    def start_speech(self):
        ## run it ##
        self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE)
        self.speech_output = ""

    def monitor_speech_no_keywords(self):
        print("Watchdog: monitoring speech without keywords\n")
        str_ing = ""
        self.last_line = ""
        self.speech_output = ""

        ## But do not wait till netstat finish, start displaying output immediately ##
        while True:
            out = self.process.stdout.read(1)
            if out == '' and self.process.poll() != None:
                break
            if out != '':
                if out == "\n":
                    # print(str_ing)
                    s = str_ing.strip()
                    if s != '':
                    # if str_ing != '':
                        self.last_line = str_ing
                        self.last_line = self.last_line.strip("\n")
                    str_ing = ""

                str_ing = str_ing + out
                self.speech_output = self.speech_output + out

                sys.stdout.write(out)
                sys.stdout.flush()

    def monitor_speech(self):
        print("Watchdog: monitoring speech\n")
        str_ing = ""

        ## But do not wait till netstat finish, start displaying output immediately ##
        while True:
            out = self.process.stdout.read(1)
            if self.speech_good == False:
                start_time = time.time()
                if time.time() > start_time + self.time_out:
                    timeout = True
                    print("Watchdog: time out")
                    break
            if out == '' and self.process.poll() != None:
                break
            if out != '':
                if out == "\n":
                    # print(str_ing)
                    if str_ing in self.speech_keywords:
                        self.speech_good = True
                    else:
                        self.speech_good = False
                    str_ing = ""
                str_ing = str_ing + out

                sys.stdout.write(out)
                sys.stdout.flush()

    def start_monitor(self):
        self.start_speech()
        monitor_thread = threading.Thread(target=self.monitor_speech_no_keywords)
        monitor_thread.start()

        self.begin_time = time.time()
        output_len = len(self.speech_output)
        print("Watchdog: Checking")
        print(self.begin_time)
        print(output_len)
        while True:
            if time.time() > self.begin_time + self.time_out:
                print("Watchdog: Checking 1")
                if output_len == len(self.speech_output):
                    print("Watchdog: last_line: ", self.last_line)
                    # print("Restart")
                    # self.restart_flag = True
                    # break
                    if self.last_line in self.speech_keywords:
                        print("Watchdog: No Restart")
                    else:
                        print(output_len)
                        print("Watchdog: Restart")
                        self.process.terminate()
                        self.restart_flag = True
                        break

                else:
                    print("Watchdog: Checking 3")
                    self.begin_time = time.time()
                    output_len = len(self.speech_output)
        #self.monitor_speech_no_keywords()

    def main_monitor(self):
        while self.restart_flag:
            print("Watchdog: Going to start monitor")
            self.start_monitor()
            print("Watchdog: back to main monitor")

m = monitor_speech()
m.main_monitor()


