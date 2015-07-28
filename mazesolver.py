#!/usr/bin/python2

import numpy as np
import cv2
import time
import mazereader
import argparse
import sys

parser = argparse.ArgumentParser(description='Solve a maze from an image')
parser.add_argument('image', help='Image of maze to solve')
parser.add_argument('--select', '-s',
                    dest='select', action='store_true',
                    help='Manually select start and end points\
                     instead of automatically detecting them')
args = parser.parse_args()

img = cv2.imread(args.image)
if img is None:
    print("Unable to load image file")
    sys.exit(-1)
start_time = time.time()
ret = mazereader.read_maze(img, args.select)
start = end = None
num_clicks = 0
if ret is not None:
    img2, graph, start, end = ret
    cv2.imshow("image", img2)

    while True:
        if start is None or end is None:
            print("Select the start and end points")
            num_clicks = 0
            img2_copy = cv2.resize(img2.copy(), (0, 0), fx=0.75, fy=0.75)

            def mouse_callback(event, x, y, flags, param):
                xx = x / 0.75
                yy = y / 0.75
                global start, end, num_clicks
                if event == cv2.EVENT_LBUTTONUP:
                    #cv2.circle(img2_copy, (x, y), 5, (255, 0, 255), -1,
                    #           cv2.LINE_AA)
                    #cv2.imshow("image", img2_copy)
                    if num_clicks == 0:
                        start = (xx, yy)
                    elif num_clicks == 1:
                        end = (xx, yy)
                        cv2.setMouseCallback("image",
                                             lambda e, x, y, f, p: None,
                                             None)
                    num_clicks += 1
            # let the user pick the start and end points
            cv2.imshow("image", img2_copy)
            cv2.setMouseCallback("image", mouse_callback,
                                 (num_clicks, start, end))
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
        for node_id in path:
            node = graph.nodes[node_id]
            if last is not None:
                cv2.line(img_copy, last.pos, node.pos, (255, 0, 0), 2,
                         cv2.LINE_AA)
            last = node
        end_time = time.time()
        print("Time: {}".format(end_time - start_time))
        cv2.imshow("image_solved",
                   cv2.resize(img_copy, (0, 0), fx=0.75, fy=0.75))
        start = None
        end = None
        if __name__ != "__main__":
            break
    cv2.destroyAllWindows()
