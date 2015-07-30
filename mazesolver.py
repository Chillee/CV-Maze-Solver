#!/usr/bin/python2

import numpy as np
import cv2
import time
import mazereader
import argparse
import sys
import processimage

parser = argparse.ArgumentParser(description='Solve a maze from an image')
parser.add_argument('image', help='Image of maze to solve')
parser.add_argument('--manual', '-m',
                    dest='manual', action='store_true',
                    help='Manually select start and end points\
                     instead of automatically detecting them')
parser.add_argument("--handdrawn", '-d',
                    dest='handdrawn', action='store_true',
                    help='Preprocess the image for a hand-drawn maze')
parser.add_argument("--scale", '-s',
                    dest='scale', type=float, default=None,
                    help='Scale factor to scale the image by before solving')
parser.add_argument("--rows", '-r', dest="screenRows", help="Pixel width of resolution", default=1024)
parser.add_argument("--cols", '-c', dest="screenCols", help="Pixel height of resolution", default=768)

args = parser.parse_args()

origImg = cv2.imread(args.image)
if origImg is None:
    print("Unable to load image file")
    sys.exit(-1)
start_time = time.time()
img = origImg.copy()

img = processimage.processimage(origImg, args.scale, args.handdrawn)
ret = mazereader.read_maze(img, args.manual)
start = end = None
num_clicks = 0

if ret is not None:
    img2, graph, start, end = ret
    cv2.imshow("image", img2)
    end_time = time.time()
    print("Time: {}".format(end_time - start_time))
    dispScale = min(float(args.screenRows)/img2.shape[1], float(args.screenCols)/img2.shape[0])
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
        for node_id in path:
            node = graph.nodes[node_id]
            if last is not None:
                cv2.line(pathImg, (int(last.pos[0]*dispScale), int(last.pos[1]*dispScale)), (int(node.pos[0]*dispScale), int(node.pos[1]*dispScale)), (255, 0, 0), 2, cv2.LINE_AA)
            last = node

        cv2.imshow("image_solved", pathImg)
        start = None
        end = None
        if __name__ != "__main__":
            break
    cv2.destroyAllWindows()
