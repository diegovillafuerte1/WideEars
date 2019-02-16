import os, threading, time, subprocess
from HubPairer import HubPairer
import face_recognition
#new variables
known_persons=[]
known_image=[]
known_face_encodings=[]

faces_file_list = []

MY_HUB_ID = "2"

def refresh_known_faces():
    global faces_files_list
    faces_files_list = os.listdir("known_faces")
    #Loops to add images in known_faces folder. Do it once to start and then again whenever the list of files changes
    for file in faces_files_list:
        try:
            #Extracting person name from the image filename eg: david.jpg
            known_persons.append(file.replace(".jpg", ""))
            file=os.path.join("friends/", file)
            known_image = face_recognition.load_image_file(file)
            known_face_encodings.append(face_recognition.face_encodings(known_image)[0])
        except Exception as e:
            pass


def scan_for_new_faces_thread():
    global faces_file_list
    while True:
        if faces_files_list != os.listdir("known_faces"):
            refresh_known_faces()
        time.sleep(1)

refresh_known_faces()
threading.Thread(target=(scan_for_new_faces_thread()))


def take_photo():
    result = subprocess.run(["fswebcam","unknown_faces.jpg"],shell=True).returncode #or false maybe?
    if result == 0:
        #photo successfully taken
        return True
    else:
        print("Error capturing photo")
        return False

def recognize_faces_in_photo():
    unknown_faces_image = face_recognition.load_image_file("unknown_faces.jpg")
    unknown_faces_encodings = face_recognition.face_encodings(unknown_faces_image)


    matching_reciever_ids = []
    for unknown_face_encoding in unknown_faces_encodings:
        results = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)
        for result_index in range(0,len(results)):
            if results[result_index] == True:
                matching_reciever_ids.append(known_persons[result_index])


    return matching_reciever_ids



def photo_recognize_pair(HubPairerInst):#use the above functions to do the whole recognition and pairing stuff
    if take_photo():
        matching_receiver_ids = recognize_faces_in_photo()
        for receiver_id in matching_receiver_ids:
            HubPairerInst.pairAndStreamAudio(receiver_id)


HubPairer(MY_HUB_ID)

photo_recognize_pair(HubPairer)