import pyaudio, socket, sys, wave

#record
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WIDTH = 2 #for recv only
WAVE_OUTPUT_FILENAME = "server_output.wav" #for recv only
frames = [] #for recv only


class AudioStreamSender:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.stopSending = False

    def startSending(self):
        ########## Start Audio Streaming ###############
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("*recording")

        frames = []

        while not self.stopSending:
            data = stream.read(CHUNK)
            frames.append(data)
            s.sendall(data)

        print("*done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()
        s.close()

        print("*closed")

    def stopSending(self):
        self.stopSending = True
        sys.exit()

class AudioStreamReciever:
    def __init__(self, port):
        self.port = port

    def startRecieving(self):
        while True:
            try:
                p = pyaudio.PyAudio()
                stream = p.open(format=p.get_format_from_width(WIDTH),
                                channels=CHANNELS,
                                rate=RATE,
                                output=True,
                                frames_per_buffer=CHUNK)


                HOST = ''                 # Symbolic name meaning all available interfaces

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((HOST, self.port))
                s.listen(1)
                conn, addr = s.accept()
                print('Connected by', addr)
                data = conn.recv(1024)

                i=1
                while data != '':
                    stream.write(data)
                    data = conn.recv(1024)
                    i=i+1
                    print(i)
                    frames.append(data)

                wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

                stream.stop_stream()
                stream.close()
                p.terminate()
                conn.close()
            except Exception as e:
                print(e)