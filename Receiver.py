import socket
import pyaudio, sys, time
import wave

from _thread import *
import threading
from AudioStreaming import AudioStreamReciever
import json


AUDIO_PORT = 50007              # Arbitrary non-privileged port
MY_CLIENT_ID = "1"
END = False


def getMyIP():
    try:
        # !/usr/bin/python3
        import socket
        import os
        gw = os.popen("ip -4 route show default").read().split()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((gw[2], 0))
        ipaddr = s.getsockname()[0]
        return ipaddr
    except:
        return socket.gethostbyname(socket.gethostname())
def threadAcceptInvite():
    global END

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, socket.SO_REUSEADDR)
    client.bind(("", 42345))
    while not END:
        try:
            data, addr = client.recvfrom(1024)
            # We will need to confirm that the Hub id in the data we recieved matches the ours***add this
            print(data)
            try:
                stuff = json.loads(str(data.decode('utf8')))
                invite_from_hubId = stuff['hubId']

                invite_to_clientId = stuff['clientId']

                if invite_to_clientId == MY_CLIENT_ID:
                    #this message is for this reciever
                    #***broadcast our info now***
                    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, socket.SO_REUSEADDR)
                    # Set a timeout so the socket does not block
                    # indefinitely when trying to receive data.
                    server.settimeout(1)
                    # server.bind(("", 37020))
                    toSend = json.dumps({"hubId": invite_from_hubId, "port":AUDIO_PORT, "clientId": MY_CLIENT_ID, "clientIp": getMyIP()})
                    message = toSend.encode()
                    print("got an invite for me, responding with:" + str(toSend))
                    server.sendto(message, ('255.255.255.255', 42346))
                    server.close()
                    END = True

                else:
                    print("got a valid invitation, but it wasn't for me")

            except json.decoder.JSONDecodeError:
                print("Got a UDP packet, but it wasn't formatted right")
        except socket.timeout:
            pass

    client.close()
    sys.exit()



def audioStreamRecieveThread():
    reciever = AudioStreamReciever(AUDIO_PORT)
    reciever.startRecieving() #this will be an infinite loop


####### Main #######
t1 = threading.Thread(target=threadAcceptInvite)
t1.start()


t2 = threading.Thread(target=audioStreamRecieveThread)
t2.start()
