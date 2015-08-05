#!/usr/bin/python2

import numpy as np
import cv2
import time
import mazereader
import argparse
import sys
import processimage
import config

parser = argparse.ArgumentParser(description='Solve a maze from an image')
parser.add_argument('image', help='Image of maze to solve')
parser.add_argument("--handdrawn", '-d',
                    dest='handdrawn', action='store_true',
                    help='Preprocess the image for a hand-drawn maze')
parser.add_argument("--scale", '-s',
                    dest='scale', type=float, default=None,
                    help='Scale factor to scale the image by before solving')
parser.add_argument("--rows", '-r', dest="screenRows",
                    help="Pixel width of resolution", default=1024)
parser.add_argument("--cols", '-c', dest="screenCols",
                    help="Pixel height of resolution", default=768)

parser.add_argument("--output", '-o',
                    dest='output', default="maze_solved.png",
                    help='File to write the final solved maze image to')
parser.add_argument("--nogui", '-n',
                    dest='nogui', action='store_true',
                    help='Do not display any images')
parser.add_argument("--pixellines", '-p',
                    dest='pixellines', action='store_true',
                    help='Draw the lines between nodes at pixel\
                    resolution from the skeleton (can help in\
                    situations where the lines go through walls)')
parser.add_argument("--tiles", '-t',
                    dest='tiles', action='store_true',
                    help='Use tiled skeletonization\
                    (sometimes faster on images with lots of white space')

args = parser.parse_args()

config.args = args

origImg = cv2.imread(config.args.image)
if origImg is None:
    print("Unable to load image file")
    sys.exit(-1)
start_time = time.time()
img = origImg.copy()

img, scale = processimage.processimage(origImg, config.args.scale,
                                       config.args.handdrawn)
cv2.imwrite("preprocessed.png", img)
ret = mazereader.read_maze(img)
start = end = None
num_clicks = 0

if ret is not None:
    img2, graph = ret
    if not config.args.nogui:
        cv2.imshow("image", img2)
    end_time = time.time()
    print("Time: {}".format(end_time - start_time))
    w, r, h = img2.shape
    r = max(float(config.args.screenRows), r)
    w = max(float(config.args.screenCols), w)
     
    dispScale = min(float(config.args.screenRows)/r, float(config.args.screenCols)/w)
    pathImg = cv2.resize(cv2.resize(origImg.copy(), (img2.shape[1], img2.shape[0])),(0,0), fx = dispScale, fy = dispScale)

    while True:
        if start is None or end is None:
            print("Select the start and end points")
            num_clicks = 0
            # img2_copy = cv2.resize(img2.copy(), (0, 0), fx=.75, fy=.75)

            def mouse_callback(event, x, y, flags, param):
                xx = x/dispScale
                yy = y/dispScale
                global start, end, num_clicks
                if event == cv2.EVENT_LBUTTONUP:
                    # cv2.circle(img2_copy, (x, y), 5, (255, 0, 255), -1,
                    #            cv2.LINE_AA)
                    # cv2.imshow("image", img2_copy)
                    if num_clicks == 0:
                        start = (xx, yy)
                    elif num_clicks == 1:
                        end = (xx, yy)
                        cv2.setMouseCallback("image",
                                             lambda e, x, y, f, p: None,
                                             None)
                    num_clicks += 1
            # let the user pick the start and end points

            if not config.args.nogui:
                cv2.imshow("image", img2)
                cv2.imshow("image_solved", pathImg)
                cv2.setMouseCallback("image_solved", mouse_callback,
                                     (num_clicks, start, end))
            pathImg = cv2.resize(cv2.resize(origImg.copy(), (img2.shape[1], img2.shape[0])),(0,0), fx = dispScale, fy = dispScale)

            while num_clicks != 2:
                if cv2.waitKey(10) == ord('q'):
                    cv2.destroyAllWindows()
                    sys.exit(0)

        node_pos, nodes = graph.build_kd_tree().query(
            np.array([[start[0], start[1]], [end[0], end[1]]]))
        start = nodes[0]
        end = nodes[1]

        # solve the maze
        path = graph.dijkstra(start, end)
        last = None

        img_copy = img.copy()
        print("Drawing lines")
        for a, b in zip(path, path[1:]):
            if config.args.pixellines:
                pixels = graph.connections[(a, b)][1]
                for pos0, pos1 in zip(pixels, pixels[1:]):
                    # pathImg[y, x] = np.array([255, 0, 0], dtype=np.uint8)
                    cv2.line(pathImg, (int(pos0[0]*dispScale), int(pos0[1]*dispScale)), (int(pos1[0]*dispScale), int(pos1[1]*dispScale)), (255, 0, 0), 1,
                             cv2.LINE_AA)
            else:
                last = graph.nodes[a]
                node = graph.nodes[b]
                cv2.line(pathImg, (int(last.pos[0]*dispScale), int(last.pos[1]*dispScale)), (int(node.pos[0]*dispScale), int(node.pos[1]*dispScale)), (255, 0, 0), 1, cv2.LINE_AA)
        print("Done")

       # if not config.args.nogui:
            #cv2.imshow("image_solved",
                       #cv2.resize(img_copy, (0, 0), fx=0.75, fy=0.75))
        cv2.imwrite(config.args.output, pathImg)
        start = None
        end = None
        if __name__ != "__main__":
            break
    cv2.destroyAllWindows()
