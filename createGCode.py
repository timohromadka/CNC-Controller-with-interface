import math
import numpy as np
import cv2 as cv
import random as rand
import feedback as fb

def calcStartingPosition(camCMWidth, camCMHeight):
    return (camCMWidth/2, camCMHeight/2)

"""
Calculate the G-Code script for the slider
@param targetMegapixels, target megapixel goal (e.g. 40 megapixels)
@param paintingResolution, width x height of the painting, in cm
@param physicalCamResolution, camera's (w,h) photo in cm
@param camMegapixels, amt of megapixels camera has
@param camRatio, camera's photo ratio (e.g. (16,9), (4,3), etc.)
@param pauseDuration, duration (in milliseconds) the slider will pause for
@param overlap, the minimum % overlap the camera will be working with
@return the informative message to be displayed to the user

Prints the gCode CNC string. For a full list of commands see 'https://en.wikipedia.org/wiki/G-code'
"""
def calculateGCode(targetMegapixels, paintingResolution, physicalCamResolution, camMegapixels, camRatio, pauseDuration, overlap, filePath):


    # create size variables
    camWidth, camHeight = camRatio
    camPWidth, camPHeight = fb.calculateCamPixelRatio(camMegapixels, camRatio)
    camCMWidth, camCMHeight = physicalCamResolution
    paintingCMWidth, paintingCMHeight = paintingResolution
    finalPWidth, finalPHeight = fb.calculatePixelWidthHeight(targetMegapixels, paintingResolution)

    # image to re-create path and camera point
    img = np.zeros([paintingCMHeight, paintingCMWidth, 3], np.uint8)

    # useful with pixel calculation, not raw camera size
    """
    finalXAmt1 = 1 # start with only one picture required
    while (finalXAmt1 - 1)*camPWidth*(1-(overlap/100)) + camPWidth < finalPWidth:
        finalXAmt1 += 1

    finalYAmt1 = 1  # start with only one picture required
    while (finalYAmt1 - 1) * camPHeight * (1 - (overlap / 100)) + camPHeight < finalPHeight:
        finalYAmt1 += 1
    """
    finalXAmt, finalYAmt = fb.calculateMinimumOverlap(camCMWidth, camCMHeight, paintingCMWidth, paintingCMHeight, overlap)
    amtOfShots = finalXAmt * finalYAmt

    # create a text file into which g code will be inserted
    # textFile = open("gcode.txt", 'r+')
    # textFile = open('gcode.txt', 'w')
    textFile = open("%s/gcode.txt" % filePath, "w").close()
    textFile = open("%s/gcode.txt" % filePath, "a")

    if amtOfShots == 1:
        textFile.write(("G00 X" + str(camCMWidth/2) + " Y" + str(camCMHeight/2)) + "\n")
        textFile.write("G04 P" + str(pauseDuration) + "\n")
        textFile.write("M00")
        return(finalXAmt, finalYAmt, 0, 0, camCMWidth/2, camCMHeight/2)
    else:
        # calculate xStep
        xLeft, yDown = calcStartingPosition(camCMWidth, camCMHeight) # calculate left most x-coordinate
        xRight = paintingCMWidth - (camCMWidth/2) # calculate right most x-coordinate
        xStep = fb.calculateStep(xLeft, xRight, finalXAmt-1) # -1 very important!

        # calculate yStep
        yUp = paintingCMHeight - (camCMHeight/2) # calculate up most y-coordinate
        yStep = fb.calculateStep(yDown, yUp, finalYAmt-1) # -1 very important!

    # tracks the current coordinate, with units in cm
    curX = xLeft
    curY = yDown
    counter = 0
    isRight = True # whether path is currently going to the right or left

    images = []

    # set max speed (100%)
    textFile.write("G21\n")
    textFile.write("F100\n")

    # create a right angled path to the first point
    textFile.write("G00 X%f Y0 \n" % curX)

    # main while loop to build the G-Code path, in a snaking pattern for efficiency
    while counter < amtOfShots:
        color = (255, 0, 0)
        cv.circle(img, (round(curX), round(curY)), 1, color, 1)
        cv.rectangle(img, (round((curX) - camCMWidth/2), round((curY - camCMHeight/2))), (round((curX) + camCMWidth/2), round((curY + camCMHeight/2))), (rand.randrange(255), rand.randrange(255), rand.randrange(255)))

        # write g-code to file
        textFile.write("G00 X%f Y%f \n" % (curX, curY))
        textFile.write("G04 P%d \n" % pauseDuration)
        counter += 1

        if isRight:
            curX += xStep
        else:
            curX -= xStep

        if curX < 0 or curX > paintingCMWidth or xStep == 0:
            isRight = not isRight
            curY += yStep
            if curX < 0:
                curX += xStep
            elif curX > paintingCMWidth:
                curX -= xStep
            continue

    # return to origin and terminate gCode
    textFile.write("G00 X0 Y0 \n")
    textFile.write("M00")
    # display gCode pattern in new window, press 's' to save
    resizeFactor = 3
    largerImg = cv.resize(img, dsize=(paintingCMWidth*resizeFactor, paintingCMHeight*resizeFactor), interpolation=cv.INTER_CUBIC)
    cv.imshow("gCode path", largerImg)
    cv.imwrite("image.png", img)

    print("final x amt is %f, final y amt is %f, xstep is %f, ystep is %f, xleft is %f, yDown is %f" % (finalXAmt, finalYAmt, xStep, yStep, xLeft, yDown))
    return(finalXAmt, finalYAmt, xStep, yStep, xLeft, yDown)