import cv2

def threshold(img):
    img = cv2.adaptiveThreshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 4)
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

def findAvgColumn(img):
    h, w = img.shape
    inMaze = False
    img = img/255
    numColumns=0
    inWall = False
    columnPos = []
    for idx, i in enumerate(img[h/2, 0:w]):
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
    columnLength = [x[1]-x[0] for x in columnPos]
    columnLength = sorted(columnLength)
    print columnLength[len(columnLength)/2]


def processimage(img, sizeMult):
    img = cv2.resize(img, (0, 0), fx=sizeMult, fy=sizeMult)
    img = threshold(img)
    findAvgColumn(img)

    #cv2.imshow("img", img)
    #img = boundingBox(img)
    #img = cv2.erode(img, (5, 5))
    #img = cv2.medianBlur(img, 3)"""
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img

if __name__ == "__main__":
    img = cv2.imread("maze3.png")
    img = cv2.resize(img, (0, 0), fx=.4, fy=.4)
    #cv2.imshow("thresh", preprocess(img))
    cv2.waitKey(0)
    cv2.destroyAllWindows()