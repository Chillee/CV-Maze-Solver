import numpy as np
import cv2
import graph
import skeletonize

def get_largest_contour_centroid(img):
    img2,cnts_start,heirarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    if len(cnts_start) == 0:
        return None
    start_cnt = cnts_start[0]
    M = cv2.moments(start_cnt)
    if M['m00'] != 0:
        return (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
    return None

def bresenham_line(a, b):
    x0, y0 = a
    x1, y1 = b
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            yield (x,y)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            yield (x,y)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy   

def check_LOS(img, a, b):
    for x, y, in bresenham_line(a,b):
        if img[y,x] == 0:
            return False
    return True

def read_maze(img):
    img2 = img.copy()

    #find the starting and ending locations
    b,g,r = cv2.split(img)
    h,s,v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))

    thresh_s = cv2.threshold(s, 100, 255, cv2.THRESH_BINARY)[1]
    thresh_r = cv2.bitwise_and(cv2.threshold(r, 200, 255, cv2.THRESH_BINARY)[1], thresh_s)
    thresh_g = cv2.bitwise_and(cv2.threshold(g, 200, 255, cv2.THRESH_BINARY)[1], thresh_s)

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

    thresh_v = cv2.bitwise_and(cv2.threshold(v, 254, 255, cv2.THRESH_BINARY)[1], cv2.bitwise_not(cv2.bitwise_or(thresh_r, thresh_g)))  
    
    thresh_v_eroded = cv2.erode(thresh_v, np.ones((3,3), np.uint8))
    thresh_v_skeleton = skeletonize.skeletonize_zhang_shuen(thresh_v)

    
    kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    #thresh_v_skeleton = cv2.dilate(thresh_v_skeleton, kernel, iterations=1)
    cv2.imshow("lines", thresh_v_skeleton)
    
    
    
    corners = cv2.goodFeaturesToTrack(thresh_v_skeleton, 0, 0.1, 10)
    g = graph.Graph()
    for corner in corners:
        if thresh_v_eroded[corner[0][1], corner[0][0]] != 0:
            node = graph.Node((corner[0][0], corner[0][1]))
            cv2.circle(thresh_v_skeleton, (node.pos[0], node.pos[1]), 3, (0, 0, 0), -1, cv2.LINE_AA)
            cv2.circle(img2, (node.pos[0], node.pos[1]), 3, (0, 0, 0), -1, cv2.LINE_AA)
            g.add_node(node)
    print("Found {} nodes".format(len(g.nodes)))
    
    """for node_id, node in g.nodes.iteritems():
        for node_id2, node2 in g.nodes.iteritems():
            if node_id != node_id2:
                if node_id not in node2.connections:
                    if check_LOS(thresh_v, node.pos, node2.pos):
                        g.link_nodes(node_id, node_id2)
                        cv2.line(img2, node.pos, node2.pos, (0, 255, 0), 3, cv2.LINE_AA)
                        cv2.imshow("image", img2)
                        if cv2.waitKey(10) & 0xff == ord('q'):
                            return None"""
    hier, contours, hierarchy = cv2.findContours(thresh_v_skeleton.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE )
    
    #for i in range(0, len(contours)):
    #    contours[i] = cv2.approxPolyDP(contours[i], 5, False)
    blank_image = np.zeros((img.shape[0], img.shape[1],3), np.uint8)
    #for contour in contours:
        #filledImage = cv2.drawContours(thresholdedImg, [contour], 0, (255,255,255), -1)    
    #cv2.imshow("cannyImg", thresholdedImg)
    areas = [(cv2.contourArea(c), index) for index,c in enumerate(contours)]
    areas = sorted(areas, reverse=True)
            
    #cnt=contours[areas[2][1]] 
    print sum([len(contour) for contour in contours])
    for i in areas:
        contour = contours[i[1]]
        blank_image = cv2.drawContours(blank_image, [contour], 0, (255, 255, 255), 1)
        
        [vx,vy,x,y] = cv2.fitLine(contour, cv2.DIST_L2,0,0.01,0.01)
        # vx, vy, x, y
        
        cols, row, depth = img2.shape
        
        arcLength = cv2.arcLength(contour, True)/2
        img2 = cv2.line(img2,(x+arcLength*vx*.5, y+arcLength*vy*.5),(x-arcLength*vx*.5, y-arcLength*vy*.5),(0,255,0),2)
        #cv2.imshow("contour", blank_image)
        #cv2.waitKey(10)
    #blank_image = cv2.drawContours(blank_image, [cnt], 0, (255, 255, 255), 1)    
    
    
    cv2.imshow("thresh_v", thresh_v_skeleton)
    cv2.imshow("contour", blank_image)
    cv2.imshow("img2", img2)

    return img2, graph

if __name__ == "__main__":
    img = cv2.imread("circular_maze1.png")
    ret = read_maze(img)
    if ret != None:
        img2, graph = ret
        cv2.imshow("image", img2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
