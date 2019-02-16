import time
import RPi.GPIO as GPIO
import MFRC522




import os, threading, time, subprocess
from HubPairer import HubPairer
MY_HUB_ID = '1'

class RFIDDetector():
    def __init(self):
        # Create an object of the class MFRC522
        self.MIFAREReader = MFRC522.MFRC522()
        self.current_card_uid = None
        self.current_audio_sender = None

    def startReading(self):
        # This loop checks for chips. If one is near it will get the UID
        try:



            while True:



                while self.current_card_uid == None:


                    # Scan for cards
                    (status, TagType) = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)

                    # Get the UID of the card
                    (status, uid) = self.MIFAREReader.MFRC522_Anticoll()

                    # If we have the UID, continue
                    if status == self.MIFAREReader.MI_OK:
                        # Print UID


                         #It's a new card so start streaming
                        #**STRART TRANSMITTING***
                        self.current_audio_sender = HubPairer(MY_HUB_ID)
                        self.current_audio_sender.pairAndStreamAudio(str(uid))
                        print("UID: " + str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3]))

                        time.sleep(0.1)
                        self.missing_card_count = 0

                while not self.current_card_uid == None:
                    time.sleep(0.1)

                    # Scan for cards
                    (status, TagType) = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)

                    # Get the UID of the card
                    (status, uid) = self.MIFAREReader.MFRC522_Anticoll()

                    # If we have the UID, continue
                    if not status == self.MIFAREReader.MI_OK:
                        # Print UID

                        self.missing_card_count += 1
                        if self.missing_card_count > 5:
                            self.current_card_uid = None

                            ##**STOP TRANSMITTING**##
                            self.current_audio_sender.listOfOngoingStreams[0]["audioSenderObject"].stopSending()
                            self.current_audio_sender = None
                            self.missing_card_count = 0
                            self.current_card_uid = None

        except KeyboardInterrupt:
            GPIO.cleanup()