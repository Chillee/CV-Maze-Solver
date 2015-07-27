import numpy as np
import cv2
import graph
import skeletonize
import connections

def get_largest_contour_centroid(img):
    img2,cnts_start,heirarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts_start) == 0:
        return None
    start_cnt = cnts_start[0]
    M = cv2.moments(start_cnt)
    if M['m00'] != 0:
        return (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
    return None
    dy = abs(y1 - y0)
    x, y = x0, y0

def find_start_end(thresh_r, thresh_g):
    start = get_largest_contour_centroid(thresh_r)
    end = get_largest_contour_centroid(thresh_g)
    return (start, end)

def create_graph_nodes(skeleton, eroded, img):
    corners = cv2.goodFeaturesToTrack(skeleton, 0, 0.1, 10)
    g = graph.Graph()
    for corner in corners:
        if eroded[corner[0][1], corner[0][0]] != 0:
            node = graph.Node((corner[0][0], corner[0][1]))
            cv2.circle(skeleton, (node.pos[0], node.pos[1]), 3, (0, 0, 0), -1, cv2.LINE_AA)
            cv2.circle(img, (node.pos[0], node.pos[1]), 3, (0, 0, 0), -1, cv2.LINE_AA)
            g.add_node(node)
    print("Found {} nodes".format(len(g.nodes)))
    return g

def read_maze(img):
    img2 = img.copy()

    b,g,r = cv2.split(img)
    h,s,v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))

    #use thresh_s to make sure that low-staturation areas are not included in the thresholds
    #for red and green
    thresh_s = cv2.threshold(s, 100, 255, cv2.THRESH_BINARY)[1]
    thresh_r = cv2.bitwise_and(cv2.threshold(r, 200, 255, cv2.THRESH_BINARY)[1], thresh_s)
    thresh_g = cv2.bitwise_and(cv2.threshold(g, 200, 255, cv2.THRESH_BINARY)[1], thresh_s)

    start, end = find_start_end(thresh_r, thresh_g)
    if start == None:
        print("Unable to find start location")
        return None
    cv2.circle(img2, start, 25, (0, 0, 0), 1, cv2.LINE_AA)
    if end == None:
        print("Unable to find end location")
        return None
    cv2.circle(img2, end, 25, (0, 0, 0), 1, cv2.LINE_AA)

    thresh_v = cv2.bitwise_and(cv2.threshold(v, 254, 255, cv2.THRESH_BINARY)[1], cv2.bitwise_not(cv2.bitwise_or(thresh_r, thresh_g)))
    thresh_v_eroded = cv2.erode(thresh_v, np.ones((3,3), np.uint8))
    thresh_v_skeleton = skeletonize.skeletonize_zhang_shuen(thresh_v)
    cv2.imshow("lines", thresh_v_skeleton)

    g = create_graph_nodes(thresh_v_skeleton, thresh_v_eroded, img2)
    connections.get_connections(g, thresh_v_skeleton, thresh_v_eroded, img2)
    
    return img2, graph
