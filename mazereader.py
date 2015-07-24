import numpy as np
import cv2
import graph

def get_largest_contour_centroid(img):
    img2,cnts_start,heirarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    if len(cnts_start) == 0:
        return None
    start_cnt = cnts_start[0]
    M = cv2.moments(start_cnt)
    if M['m00'] != 0:
        return (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
    return None

#thin all lines to 1 pixel wide
def skeletonize(img):
    size = np.size(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    ret = np.zeros(img.shape, np.uint8)
    while True:
        eroded = cv2.erode(img, kernel)
        temp = cv2.dilate(eroded, kernel)
        temp = cv2.subtract(img, temp)
        ret = cv2.bitwise_or(ret, temp)
        img = eroded.copy()

        zeros = size - cv2.countNonZero(img)
        if zeros == size:
            break

    return ret

def read_maze(img):
    img2 = img.copy()

    #find the starting and ending locations
    b,g,r = cv2.split(img)
    h,s,v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))

    thresh_s = cv2.threshold(s, 100, 255, cv2.THRESH_BINARY)[1]
    thresh_r = cv2.bitwise_and(cv2.threshold(r, 250, 255, cv2.THRESH_BINARY)[1], thresh_s)
    thresh_g = cv2.bitwise_and(cv2.threshold(g, 250, 255, cv2.THRESH_BINARY)[1], thresh_s)

    start = get_largest_contour_centroid(thresh_r)
    if start == None:
        print("Unable to find start location")
        return None
    cv2.circle(img2, start, 25, (0, 0, 0), 1, cv2.LINE_AA)

    end = get_largest_contour_centroid(thresh_g)
    if end == None:
        print("Unable to find end location")
        return None
    cv2.circle(img2, end, 25, (0, 0, 0), 1, cv2.LINE_AA)

    thresh_v = cv2.bitwise_and(cv2.threshold(v, 250, 255, cv2.THRESH_BINARY)[1], cv2.bitwise_not(cv2.bitwise_or(thresh_r, thresh_g)))
    thresh_v_eroded = cv2.erode(thresh_v, np.ones((3,3), np.uint8))
    thresh_v = skeletonize(thresh_v)
    cv2.imshow("skeleton", thresh_v)
    corners = cv2.goodFeaturesToTrack(thresh_v, 0, 0.1, 10)
    nodes = [graph.Node(start), graph.Node(end)]
    for corner in corners:
        if thresh_v_eroded[corner[0][1]][corner[0][0]] != 0:
            nodes.append(graph.Node((corner[0][1], corner[0][0])))
    g = graph.Graph()
    for node in nodes:
        cv2.circle(img2, (node.pos[0], node.pos[1]), 3, (255, 0, 0), -1, cv2.LINE_AA)
        g.add_node(node)
    print("Found {} nodes".format(len(nodes)))

    return img2, graph

if __name__ == "__main__":
    img = cv2.imread("circular_maze1.png")
    ret = read_maze(img)
    if ret != None:
        img2, graph = ret
        cv2.imshow("image", img2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
