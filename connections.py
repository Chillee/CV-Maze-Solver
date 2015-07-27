import numpy as np
import cv2

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

def get_connections(g, skeleton, eroded, img):
    hier, contours, hierarchy = cv2.findContours(skeleton.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE )

    blank_image = np.zeros((img.shape[0], img.shape[1],3), np.uint8)
    areas = [(cv2.contourArea(c), index) for index,c in enumerate(contours)]
    areas = sorted(areas, reverse=True)

    tree = g.build_kd_tree()

    for i in areas:
        contour = contours[i[1]]
        blank_image = cv2.drawContours(blank_image, [contour], 0, (255, 255, 255), 1)

        [vx,vy,x,y] = cv2.fitLine(contour, cv2.DIST_L2,0,0.01,0.01)

        cols, row, depth = img.shape

        arcLength = cv2.arcLength(contour, True)/2
        x0, y0 = float(x+arcLength*vx*.5), float(y+arcLength*vy*.5)
        x1, y1 = float(x-arcLength*vx*.5), float(y-arcLength*vy*.5)

        nodes = []
        node_pos, nodes = tree.query(np.array([[x0,y0], [x1,y1]]))
        node_a = nodes[0]
        node_b = nodes[1]
        if check_LOS(eroded, g.nodes[node_a].pos, g.nodes[node_b].pos):
            dx = g.nodes[node_a].pos[0] - g.nodes[node_b].pos[0]
            dy = g.nodes[node_a].pos[1] - g.nodes[node_b].pos[1]
            g.link_nodes(node_a, node_b, np.sqrt(dx * dx + dy * dy))
            cv2.line(img, g.nodes[node_a].pos, g.nodes[node_b].pos, (0,255,0), 2, cv2.LINE_AA)
    print g.dijkstra(1, 5)
    print "hmm"
