import numpy as np
import random
import cv2
import graph
import skeletonize
import connections
import config
import processimage


def get_largest_contour_centroid(img):
    img2, cnts_start, heirarchy = cv2.findContours(img,
                                                   cv2.RETR_TREE,
                                                   cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts_start) == 0:
        return None
    start_cnt = cnts_start[0]
    m = cv2.moments(start_cnt)
    if m['m00'] != 0:
        return (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
    return None


def find_start_end(thresh_r, thresh_g):
    start = get_largest_contour_centroid(thresh_r)
    end = get_largest_contour_centroid(thresh_g)
    return (start, end)


def create_graph_nodes(skeleton, eroded, img):
    corners = cv2.goodFeaturesToTrack(skeleton, 0, 0.025, 3)
    g = graph.Graph()
    for corner in corners:
        if eroded[corner[0][1], corner[0][0]] != 0:
            node = graph.Node((corner[0][0], corner[0][1]))
            g.add_node(node)
    print("Found {} nodes".format(len(g.nodes)))
    return g


def read_maze(img):
    img2 = img.copy()

    thresh_v = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh_v_eroded = cv2.erode(thresh_v, np.ones((3, 3), np.uint8))

    thresh_v_skeleton = skeletonize.skeletonize_zhang_shuen(thresh_v)
    if not config.args.nogui:
        cv2.imshow("skeleton",
                   cv2.resize(thresh_v_skeleton, (0, 0), fx=0.5, fy=0.5))
    cv2.imwrite("skeleton.png", thresh_v_skeleton)

    g = create_graph_nodes(thresh_v_skeleton, thresh_v_eroded, img2)
    connections.get_connections(g, thresh_v_skeleton, thresh_v_eroded)
    g.split_long_edges()

    group_colors = {}
    for node in g.nodes:
        if node.group not in group_colors:
            group_colors[node.group] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255))
        cv2.circle(img2, (node.pos[0], node.pos[1]), 3,
                   group_colors[node.group], -1, cv2.LINE_AA)
    cv2.imwrite("nodes.png", img2)
    for a, b in g.connections:
        cv2.line(img2, g.nodes[a].pos, g.nodes[b].pos,
                 (0, 255, 0), 1, cv2.LINE_AA)
    cv2.imwrite("connections.png", img2)

    return img2, g
