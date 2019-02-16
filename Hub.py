import socket
import pyaudio
import wave

from _thread import *
import threading

import json

#record
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 40

HOST = '192.168.137.1'    # The remote host
PORT = 50007              # The same port as used by the server

END = False

dataGlobal = None

########## Get ID from face Section ###########

########## Start Broadcasting ################
def threadSend():
    global END
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    server.settimeout(1)
    server.bind(("", 44444))
    toSend = json.dumps({"Hub": 2, "Client": 1}
    message = toSend
    # message = b"Hub 2, Looking For Client 1"
    while not END:
        server.sendto(message, ('<broadcast>', 37020))
        print("message sent!")
        time.sleep(1)
    sys.exit()

######### Wait to Receive UDP #################
def threadReceive():
    global END
    global globalData
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 37020))
    while True:
        data, addr = client.recvfrom(1024)
        globalData = data
        END = True
    sys.exit()

####### Main #######
t1 = threading.Thread(target=threadReceive)
t1.start()
t2 = threading.Thread(target=threadReceive)
t2.start()
wait = True
# threadSend("Send").Start
# threadReceive("Receive")

########### Wait for GlobalData to be filled to parse
while wait:
    if globalData:
        stuff = json.loads(globalData)
        ip = stuff['ip']
        port = stuff['port']
        hubId = stuff['hubId']
        clientId = stuff['clientId']
        wait = False

# globalData -> parse, IP and Port
if not(ip == HOST):
    print('ip did not match host')
    sys.exit()
if not(port == PORT):
    print('port did not match port')
    sys.exit()

########## Start Audio Streaming ###############
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("*recording")

frames = []

for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
 data  = stream.read(CHUNK)
 frames.append(data)
 s.sendall(data)

print("*done recording")

stream.stop_stream()
stream.close()
p.terminate()
s.close()

print("*closed")