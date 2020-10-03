import math

def giveFeedback(language, targetMegapixels, paintingResolution, physicalCamResolution, camMegapixels, camRatio, xAmount, yAmount):
    # create size variables
    camWidth, camHeight = camRatio
    camPWidth, camPHeight = calculateCamPixelRatio(camMegapixels, camRatio)
    camCMWidth, camCMHeight = physicalCamResolution
    paintingCMWidth, paintingCMHeight = paintingResolution

    # create constants for efficiency measurement
    lowest_allowed_efficiency = 0.4

    # boolean to keep track of whether the gcode can be generated or not
    canProceed = False

    def doRatiosMatch():
        # checks if about equal to 5 decimal places
        if not math.isclose(camCMWidth / camCMHeight, camWidth / camHeight, abs_tol=10 ** -5):
            return False
        else:
            return True

    def calculateIfPossible():
        # check if the target megapixel count is even attainable by taking max case scenario
        if ((paintingCMWidth / camCMWidth) * camPWidth) * (
                (paintingCMHeight / camCMHeight) * camPHeight) <= targetMegapixels * 1000000:
            return False
        return True

    def calculateIsEfficient():

        def calculateOneAxisEfficiency(camP, amt, length):
            return (length/(amt*camP))

        xEfficiency = calculateOneAxisEfficiency(camCMWidth, xAmount, paintingCMWidth)
        yEfficiency = calculateOneAxisEfficiency(camCMHeight, yAmount, paintingCMHeight)
        # check if there is TOO much overlap (inefficient, loss of megapixels)
        if xEfficiency < lowest_allowed_efficiency and yEfficiency < lowest_allowed_efficiency:
            return False
        else:
            return True

    # read the correct language file
    fileName = ""
    if language == 1:  # english
        fileName = "en_alert.txt"
    elif language == 2:  # slovak
        fileName = "sk_alert.txt"
    elif language == 3:  # german
        fileName = "de_alert.txt"
    try:
        file = 'language_folder/%s' % fileName
    except FileNotFoundError:
        return ("Couldn't find language file: .../language_folder/##_alert.txt")
    with open(file) as f:
        lines = f.readlines()

        # -------------------------------------
        # THE MAIN FEEDBACK PROCESS
        # -------------------------------------

        # camera ratios do not match
        if not doRatiosMatch():
            return(lines[0], False)

        # works, but not optimal
        elif not calculateIsEfficient():
            return(lines[1], True)

        # unable to reach megapixel count
        elif not calculateIfPossible():
            return (lines[2], False)

        else: # success message
            return(lines[3], True)

def calculateMinimumOverlap(camCMWidth, camCMHeight, paintingCMWidth, paintingCMHeight, overlap):

    actualOverlap = overlap
    if overlap < 0 or overlap > 100:
        actualOverlap = 25

    def calculateOneAxisOverlap(camCMLength, paintingCMLength):
        finalAmt = 1  # start with only one x-distance required
        while (finalAmt - 1) * camCMLength * (1 - (actualOverlap / 100)) + camCMLength < paintingCMLength:
            finalAmt += 1
        return finalAmt

    xAmt = calculateOneAxisOverlap(camCMWidth, paintingCMWidth)
    yAmt = calculateOneAxisOverlap(camCMHeight, paintingCMHeight)

    return (xAmt, yAmt)

"""
Calculate the width and height (in pixels) the final processed image should have
@param targetMegapixels, target megapixel goal (e.g. 40 megapixels)
@param imageSize, the width and height of the physical image, in any unit
@return, width x height, width x height of the final image, in pixels
"""
def calculatePixelWidthHeight(targetMegapixels, imageSize):
    imageWidth, imageHeight = imageSize
    ratio = imageHeight / imageWidth

    finalWidth = math.sqrt(targetMegapixels * 1000000 / ratio)  # calculate width
    finalHeight = finalWidth * ratio
    return (finalWidth, finalHeight)

"""
Calculate increments between two points (either both X or both Y). Used to generate
incremented values when locating the center position for the camera to take a picture
@return increment, a number in cm to denote the length between camera points

"""
def calculateStep(pointA, pointB, amt):
    if amt == 0: # no movement required across this axis
        return 0
    high = max(pointA, pointB)
    low = min(pointA, pointB)
    return (high-low)/amt

"""
Calculate the pixelWidth and pixelHeight the camera takes pictures in
@param camMegapixels, cmaera megapixels
@param camRatio, (w, h) of camera's ratio (e.g. (16,9), (4,3), etc.)
Using formula x = sqrt(m/(w*h))
"""
def calculateCamPixelRatio(camMegapixels, camRatio):
    width, height = camRatio
    factor = math.sqrt(camMegapixels*1000000/(width*height))
    return (width*factor, height*factor)
