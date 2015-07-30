import cv2
import numpy as np

def threshold(img):
    img = cv2.adaptiveThreshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 4)
    #PAPER_MIN = np.array([0, 0, 100],np.uint8)
    #PAPER_MAX = np.array([255, 255, 255],np.uint8)
    #img = cv2.inRange(img, PAPER_MIN, PAPER_MAX)
    return img

def boundingBox(img):
    cannyImg = cv2.Canny(img, 100, 200)

    hier, contours, hierarchy = cv2.findContours(cannyImg.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    areas = [(cv2.contourArea(c), index) for index,c in enumerate(contours)]
    areas = sorted(areas)
    bigContour = contours[areas[-1][1]]
    x,y,w,h = cv2.boundingRect(bigContour)
    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    #img = cv2.drawContours(img, [bigContour], 0, (0, 0, 0), -1)

    return img

def findColumnLengths(img, horizontal, position):
    h, w = img.shape
    position = h/2
    inMaze = False
    img = img/255
    numColumns=0
    inWall = False
    columnPos = []
    if horizontal:
        iterRange = enumerate(img[position, 0:w])
    else:
        iterRange = enumerate()
    for idx, i in iterRange:
        if i == 1 and not inMaze:
            continue
        if i == 0 and not inMaze:
            inMaze = True
            inWall = True

        if i == 0 and not inWall:
            inMaze=True
            inWall = True
            columnPos[-1].append(idx)
        elif i == 1 and inWall:
            inWall = False
            columnPos.append([idx])
    if(len(columnPos[-1]) == 1):
        columnPos.pop()
    whiteColumnLength = [x[1]-x[0] for x in columnPos]
    blackColumnLength = [columnPos[idx+1][0] - columnPos[idx][1] for idx, x in enumerate(columnPos[:-1])]
    whiteColumnLength = sorted(whiteColumnLength)
    blackColumnLength = sorted(blackColumnLength)
    return whiteColumnLength, blackColumnLength


def processimage(img, sizeMult=None, handdrawn = False):
    img = threshold(img)
    h, w = img.shape
    #img = boundingBox(img)
    MIN_COLUMN_SIZE = 15.0
    if handdrawn:
        img = cv2.erode(img, (7, 7))
        img = cv2.medianBlur(img, 3)
        MIN_COLUMN_SIZE = 30.0
        
    #img = boundingBox(img)

    if not sizeMult:
        whiteCols, blackCols = [], []
        for i in [h/3, h/2, 2*h/3]:
            x = findColumnLengths(img, True, i)
            whiteCols.append(x[0])
            blackCols.append(x[1])

        whiteCols = [i for sublist in whiteCols for i in sublist]
        blackCols = [i for sublist in blackCols for i in sublist]

        if handdrawn:
            blackCols= [i for i in blackCols if i > 2]
            whiteCols = [i for i in whiteCols if i > 2]
        whiteCols = sorted(whiteCols)
        blackCols = sorted(blackCols)
        print whiteCols, blackCols

        whiteColSize = whiteCols[len(whiteCols)/2]
        blackColSize = blackCols[len(blackCols)/2]

        print whiteColSize, blackColSize

        sizeMult = MIN_COLUMN_SIZE/whiteColSize
    print sizeMult
    img = cv2.resize(img, (0, 0), fx=sizeMult, fy=sizeMult)

    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


    return img

if __name__ == "__main__":
    img = cv2.imread("maze3.png")
    img = cv2.resize(img, (0, 0), fx=.4, fy=.4)
    #cv2.imshow("thresh", preprocess(img))
    cv2.waitKey(0)
    cv2.destroyAllWindows()