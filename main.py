import cv2
import pickle
import cvzone
import goto
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("hsn.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Video feed
cap = cv2.VideoCapture('carPark.mp4')

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48


class ParkCam(object):
    def __init__(self, placeID, status, latitude, longitude):
        self.placeID = placeID
        self.status = status
        self.latitude = latitude
        self.longitude = longitude

#for placeID,pos in enumerate(posList):
#    cam1 = ParkCam(placeID, "Busy", "12.1245", "49.4561")
#    camUpdateList = {
#        u'placeID': cam1.placeID,
#        u'status': cam1.status,
#        u'latitude': cam1.latitude,
#        u'longitude': cam1.longitude,
#    }
#    db.collection(u'cam1').document(u'{}'.format(placeID)).update(camUpdateList)


def checkParkingSpace(imgPro):
    spaceCounter = 0


    for placeID, pos in enumerate(posList):
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        # cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)
        cvzone.putTextRect(img, str(placeID), (x + width - 30, y + height - 30), scale=1, thickness=2, offset=0,
                           colorR=(0, 0, 255))
        if count < 850:
            cam1 = ParkCam(placeID, "Empty", "12.1245", "49.4561")
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
            camUpdateList = {
                u'placeID': cam1.placeID,
                u'status': cam1.status,
                u'latitude': cam1.latitude,
                u'longitude': cam1.longitude,
            }
            db.collection(u'cam1').document(u'{}'.format(placeID)).set(camUpdateList)

        else:
            color = (0, 0, 255)
            thickness = 2
            cam1 = ParkCam(placeID, "Busy", "12.1245", "49.4561")
            camUpdateList = {
                u'placeID': cam1.placeID,
                u'status': cam1.status,
                u'latitude': cam1.latitude,
                u'longitude': cam1.longitude,
            }
            db.collection(u'cam1').document(u'{}'.format(placeID)).set(camUpdateList)



        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                       thickness=5, offset=20, colorR=(0, 200, 0))


while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)

    cv2.imshow("Image", img)
    # cv2.imshow("ImageBlur", imgBlur)
    # cv2.imshow("ImageThres", imgMedian)
    cv2.waitKey(10)
