import socket
import pyaudio, sys, time
import wave
from AudioStreaming import AudioStreamSender
from _thread import *
import threading

import json

class HubPairer():
    def __init__(self, MY_HUB_ID):
        self.MY_HUB_ID = MY_HUB_ID


        self.END = False
        self.listOfOngoingStreams = [] #format: list of dicts that hold clientId and the relevant audioStreamSender object
        self.globalData = None



    def pairAndStreamAudio(self, clientId):
        ########## Start Broadcasting ################
        def threadSend():

            server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, socket.SO_REUSEADDR)
            # Set a timeout so the socket does not block
            # indefinitely when trying to receive data.
            server.settimeout(1)
            #server.bind(("", 37020))
            toSend = json.dumps({"hubId": self.MY_HUB_ID, "clientId": clientId})
            message = toSend.encode()

            # message = b"Hub 2, Looking For Client 1"
            print(toSend)
            while not self.END:
                print(1)
                server.sendto(message, ('<broadcast>', 42345))
                print("message sent!")
                time.sleep(1)
            server.close()
            sys.exit()

        ######### Wait to Receive UDP #################
        def threadReceive():

            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,socket.SO_REUSEADDR)
            client.bind(("", 42346))
            while not self.END:
                try:
                    data, addr = client.recvfrom(1024)
                    # We will need to confirm that the Hub id in the data we recieved matches the ours***add this
                    print(data)


                    stuff = json.loads(data)
                    hubId = stuff['hubId']
                    print(hubId)
                    if hubId == self.MY_HUB_ID:
                        self.globalData = data
                        self.END = True
                except socket.timeout:
                    pass
                except json.JSONDecodeError:
                    print("got a packet but it was in wrong format")

            client.close()
            sys.exit()

        ####### Main #######
        t1 = threading.Thread(target=threadSend)
        t1.start()
        t2 = threading.Thread(target=threadReceive)
        t2.start()

        wait = True


        def startSendingAudioStream(clientIp, audioPort, clientId):
            audioSender = AudioStreamSender(clientIp, audioPort)
            audioSendThread = threading.Thread(target=audioSender.startSending, args=(clientIp, audioPort))
            audioSendThread.start()

            return {"clientId":clientId, "audioSenderObject":audioSender}



        ########### Wait for GlobalData to be filled to parse
        while wait:
            if self.globalData:
                stuff = json.loads(self.globalData)
                clientIp = stuff['clientIp']
                audioPort = stuff['port']
                clientId = stuff['clientId']
                hubId = stuff['hubId']
                wait = False

        self.listOfOngoingStreams.append(startSendingAudioStream(clientIp, audioPort, clientId))



