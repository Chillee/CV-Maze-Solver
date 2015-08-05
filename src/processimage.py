#TODO: denoise
import cv2
import numpy as np


def threshold_value(img):
    b, g, r = cv2.split(img)
    h, s, v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))

    # use thresh_s to make sure that low-staturation areas are not included in
    # the thresholds for red and green
    thresh_s = cv2.threshold(s, 100, 255, cv2.THRESH_BINARY)[1]
    thresh_r = cv2.bitwise_and(
        cv2.threshold(r, 200, 255, cv2.THRESH_BINARY)[1], thresh_s)
    thresh_g = cv2.bitwise_and(
        cv2.threshold(g, 200, 255, cv2.THRESH_BINARY)[1], thresh_s)

    img =  cv2.bitwise_and(
        cv2.threshold(v, 150, 255, cv2.THRESH_BINARY)[1],
        cv2.bitwise_not(cv2.bitwise_or(thresh_r, thresh_g)))
    #PAPER_MIN = np.array([0, 0, 110])
    #img = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 190, 255)
    #cv2.imshow("test", img)
    return img


def threshold(img):
    adapt_thresh = cv2.adaptiveThreshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 255,
                                cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                11, 4)
    PAPER_MIN = np.array([0, 0, 110],np.uint8)
    PAPER_MAX = np.array([255, 255, 255],np.uint8)
    range_thresh = cv2.inRange(img, PAPER_MIN, PAPER_MAX)

    img = cv2.bitwise_and(range_thresh, adapt_thresh)
    #cv2.imshow("range", range_thresh)
    #cv2.imshow("adapt_thresh", adapt_thresh)

    # img = cv2.inRange(img, PAPER_MIN, PAPER_MAX)
    return img


def bounding_box(img):
    canny_img = cv2.Canny(img, 100, 200)

    hier, contours, hierarchy = cv2.findContours(canny_img.copy(),
                                                 cv2.RETR_CCOMP,
                                                 cv2.CHAIN_APPROX_SIMPLE)

    areas = [(cv2.contourArea(c), index) for index, c in enumerate(contours)]
    areas = sorted(areas)
    big_contour = contours[areas[-1][1]]
    x, y, w, h = cv2.boundingRect(big_contour)
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # img = cv2.drawContours(img, [big_contour], 0, (0, 0, 0), -1)

    return img


def find_column_length(img, horizontal, position):
    h, w = img.shape
    position = h / 2
    in_maze = False
    img = img / 255
    in_wall = False
    column_pos = []
    if horizontal:
        iterRange = enumerate(img[position, 0:w])
    else:
        iterRange = enumerate(img[0:h, position])
    for idx, i in iterRange:
        if i == 1 and not in_maze:
            continue
        if i == 0 and not in_maze:
            in_maze = True
            in_wall = True

        if i == 0 and not in_wall:
            in_maze=True
            in_wall = True
            column_pos[-1].append(idx)
        elif i == 1 and in_wall:
            in_wall = False
            column_pos.append([idx])
    if(len(column_pos) == 0):
        return [], []
    if(len(column_pos[-1]) == 1):
        column_pos.pop()
    whiteColumnLength = [x[1]-x[0] for x in column_pos]
    blackColumnLength = [column_pos[idx+1][0] - column_pos[idx][1] for idx, x in enumerate(column_pos[:-1])]
    whiteColumnLength = sorted(whiteColumnLength)
    blackColumnLength = sorted(blackColumnLength)
    return whiteColumnLength, blackColumnLength


def processimage(img, size_mult=None, handdrawn = False):
    if handdrawn:
        img = threshold(img)
    else:
        img = threshold_value(img)
    h, w = img.shape
    # img = bounding_box(img)
    #min_column_size = 15.0
    min_column_size = 10.0
    if handdrawn:
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
        img = cv2.medianBlur(img, 3)
        kernel = np.ones((5,5),np.uint8)
        img = cv2.erode(img, kernel)

        min_column_size = 15.0
        #cv2.imshow("heh", img)
    # img = bounding_box(img)

    if not size_mult:
        white_cols, black_cols = [], []
        for i in [h / 3, h / 2, 2 * h / 3]:
            x = find_column_length(img, True, i)
            white_cols.append(x[0])
            black_cols.append(x[1])

        for i in [w/3, w/2, 2*w/3]:
            x = find_column_length(img, False, i)
            white_cols.append(x[0])
            black_cols.append(x[1])

        white_cols = [i for sublist in white_cols for i in sublist]
        black_cols = [i for sublist in black_cols for i in sublist]

        if handdrawn:
            black_cols = [i for i in black_cols if i > 2]
            white_cols = [i for i in white_cols if i > 2]
        white_cols = sorted(white_cols)
        black_cols = sorted(black_cols)
        print(white_cols, black_cols)

        white_col_size = white_cols[len(white_cols) / 2]
        black_col_size = black_cols[len(black_cols) / 2]

        print(white_col_size, black_col_size)

        size_mult = min_column_size / white_col_size
    print(size_mult)
    img = cv2.resize(img, (0, 0), fx=size_mult, fy=size_mult)

    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    return img, size_mult

if __name__ == "__main__":
    img = cv2.imread("maze3.png")
    img = cv2.resize(img, (0, 0), fx=.4, fy=.4)
    # cv2.imshow("thresh", preprocess(img))
    # cv2.waitKey(0)
    cv2.destroyAllWindows()
