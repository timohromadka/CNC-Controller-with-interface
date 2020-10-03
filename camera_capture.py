import cv2 as cv
import numpy as np
import time

# CONSTANT SPEEDS OF THE CNC MACHINE, CHANGE ACCORDINGLY
xSpeed = 300 # cm/sec
ySpeed = 100 # cm/sec
padding = 0 # ms


def cameraCapture(folder, xAmt, yAmt, xLength, yLength, startX, startY, pauseDuration):

    xDuration = calcDuration(xLength, xSpeed)
    yDuration = calcDuration(yLength, ySpeed)
    photosTaken = 0

    pauses = []

    # calculate how long it takes to reach the start point
    startPointDuration = calcDuration(startX, xSpeed) + calcDuration(startY, ySpeed) + pauseDuration/2
    pauses.append(startPointDuration)

    #print(startPointDuration)
    for y in range(yAmt):
        for x in range (xAmt-1):
            pauses.append(xDuration + pauseDuration)
        pauses.append(yDuration + pauseDuration)

    pauses.pop()
    #print(pauses)


    cap = cv.VideoCapture(0)
    counter = 0 # counter for each capture
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    index = 0
    startTime = time.time()
    while index < len(pauses):
        # Capture frame
        ret, frame = cap.read()
        # ret = True if successful capture
        if not ret:
            print("Error. Can't receive camera input, exiting.")
            break
        # for capturing
        frame = cv.flip(frame, -1)

        # cv.putText(frameEdit, "press \'q\' to close", (10, 20), cv.FONT_HERSHEY_SIMPLEX, 1,(208, 224, 64),2,cv.LINE_AA)
        # cv.putText(frameEdit, "press \'w\' to capture", (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (208, 224, 64), 2, cv.LINE_AA)

        # show captured image in frame
        cv.imshow("Camera", frame)
        key = cv.waitKey(1)
        if key == ord('q'):
            break

        endTime = time.time()
        elapsedTime = (endTime - startTime)*1000
        #print(elapsedTime)
        #print(index)
        if elapsedTime >= pauses[index]:
            cv.imwrite(folder + '/image%d.png' % index, frame)
            cv.imshow('test', frame)
            #print("photo captured! Saved as image%d.png to " % counter + folder)
            index += 1
            startTime = time.time()
            #print("index %d %f" % (index, startTime))
    cap.release()
    cv.destroyAllWindows()

def calcDuration(length, speed):
    # 60000 (ms) * length (cm), divided by speed (cm/min)
    return ((60000 * length)/speed) + padding



#cameraCapture("C:/Users/timosh/PycharmProjects/ustav_brigada/images_for_stitching", 3, 3, 10, 10, 5, 5, 3000)