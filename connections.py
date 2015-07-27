import numpy as np
import cv2

def get_connections(g, skeleton, img):
    hier, contours, hierarchy = cv2.findContours(skeleton.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE )

    blank_image = np.zeros((img.shape[0], img.shape[1],3), np.uint8)
    areas = [(cv2.contourArea(c), index) for index,c in enumerate(contours)]
    areas = sorted(areas, reverse=True)

    for i in areas:
        contour = contours[i[1]]
        blank_image = cv2.drawContours(blank_image, [contour], 0, (255, 255, 255), 1)

        [vx,vy,x,y] = cv2.fitLine(contour, cv2.DIST_L2,0,0.01,0.01)

        cols, row, depth = img.shape

        arcLength = cv2.arcLength(contour, True)/2
        img = cv2.line(img, (x+arcLength*vx*.5, y+arcLength*vy*.5), (x-arcLength*vx*.5, y-arcLength*vy*.5), (0,255,0), 2, cv2.LINE_AA)
