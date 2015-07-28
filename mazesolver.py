#!/usr/bin/python2

import cv2
import time
import mazereader
import argparse
import sys

parser = argparse.ArgumentParser(description='Solve a maze from an image')
parser.add_argument('image', help='Image of maze to solve')
parser.add_argument('--select', '-s',
    dest='select', action='store_true',
    help='Manually select start and end points instead of automatically detecting them')
args = parser.parse_args()

img = cv2.imread(args.image)
if img == None:
    print("Unable to load image file")
    sys.exit(-1)
start_time = time.time()
ret = mazereader.read_maze(img, args.select)
if ret != None:
    img2, graph, start, end = ret
    cv2.imshow("image", img2)
    #solve the maze
    path = graph.dijkstra(start, end)
    last = None
    for node_id in path:
        node = graph.nodes[node_id]
        if last is not None:
            cv2.line(img, last.pos, node.pos, (255, 0, 0), 2, cv2.LINE_AA)
        last = node
    end_time = time.time()
    print("Time: {}".format(end_time - start_time))
    cv2.imshow("image_solved", img)
    if __name__ == "__main__":
        while True:
            if cv2.waitKey(10) == ord('q'):
                break
    cv2.destroyAllWindows()