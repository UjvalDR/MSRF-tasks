import cv2 as cv                       # importing opencv module
import mediapipe as mp                 # importing mediapipe module
import numpy as np                     # importing numpy module
import math
from ctypes import cast, POINTER       # the below 3 modules are used to control the speakers
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

####################################################################
# to initialize the objects of mediapipe and volume modules
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

#####################################################################

def findHandLandPos(image, handNumber=0, draw=False):
    realimg = image
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)  # Because mediapipe accepts only  RGB
    results =hands.process(image)
    landMarkList = []

    if results.multi_hand_landmarks:                    # returns None if hand isn't detected
        hand = results.multi_hand_landmarks[handNumber] #results.multi_hand_landmarks returns landMarks for all the hands

        for id, landMark in enumerate(hand.landmark):
            imgH, imgW, imgC = realimg.shape          # height, width, channel of the image
            xPos, yPos = int(landMark.x * imgW), int(landMark.y * imgH)
            landMarkList.append([id, xPos, yPos])

        if draw:
            mpDraw.draw_landmarks(realimg, hand, mpHands.HAND_CONNECTIONS)

    return landMarkList



def main():
    
    webcamvid = cv.VideoCapture(0)
    volBar = 400
    volPer = 0

    while True:
        ret, image = webcamvid.read()
        handLandmarks = findHandLandPos(image=image, draw=True)

        if(len(handLandmarks) != 0):

            x1, y1 = handLandmarks[4][1], handLandmarks[4][2]
            x2, y2 = handLandmarks[8][1], handLandmarks[8][2]
            cx, cy = (x1+x2) // 2 , (y1+y2) // 2
            length = math.hypot(x2-x1, y2-y1)

            # to imterpolate volume value,bar and percentage
            volumeValue = np.interp(length, [50, 250], [-65.25, 0.0]) #coverting length to proportionate to volume range
            volBar = np.interp(length,[50,300],[400,150])
            volPer = np.interp(length,[50,300],[0,100])
            volume.SetMasterVolumeLevel(volumeValue, None)     #setting the volume 

            #to plot a circle at thumb and forefinger
            cv.circle(image, (x1, y1), 15, (255, 0, 255), -1)
            cv.circle(image, (x2, y2), 15, (255, 0, 255), -1)
            cv.line(image, (x1, y1), (x2, y2), (255, 0, 255), 3) # a line to join thumb and forefinger
            cv.circle(image,(cx,cy),15,(255,0,255),-1)            # a circle at middle of the line

            if length < 50:
                cv.circle(image,(cx,cy),15,(0,255,0),-1)    # if volume is 0 then the circle in the middle turns to green
            elif length > 300:
                cv.circle(image,(cx,cy),15,(0,0,255),-1)    # if the volume raises to 95 it shows a red circle

            # To set volume bar 
            cv.rectangle(image,(50,150),(85,400),(0,0,0),3)
            cv.rectangle(image,(50,int(volBar)),(85,400),(0,255,0),-1)
            cv.putText(image,f'{int(volPer)} %',(40,450),cv.FONT_HERSHEY_COMPLEX_SMALL,1,(0,0,255),2)

            print(int(volPer)) # to print volume in the console

        cv.imshow("Volume", image)   

        if cv.waitKey(1)==27:       #if user presses esc key the program ends
            break

    cv.destroyAllWindows()

if __name__ == "__main__":
    main()