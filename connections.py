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
            yield (x, y)
            err -= dy
            if err < 0:
                y += y
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            yield (x, y)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy


def check_los(img, a, b):
    print(a, b)
    for x, y, in bresenham_line(a, b):
        print(x, y)
        if img[y, x] == 0:
            return False
    return True

num_clicks = 0
start_ = None
end_ = None


def get_connections(g, skeleton, eroded, img):
    skeleton = cv2.resize(skeleton, (0, 0), fx=0.5, fy=0.5)
    height, width = skeleton.shape
    tree = g.build_kd_tree()

    visited = cv2.merge((skeleton, skeleton * 0, skeleton * 0))
    for node in g.nodes:
        cv2.rectangle(visited,
                      (int(node.pos[0] / 2) - 1, int(node.pos[1] / 2) - 1),
                      (int(node.pos[0] / 2) + 1, int(node.pos[1] / 2) + 1),
                      (255, 255, 0), -1)
        #visited[node.pos[1] / 4, node.pos[0] / 4][1] = 255

    pixel_stack = [((g.nodes[0].pos[0] / 2, g.nodes[0].pos[1] / 2), 0)]
    i = 0
    while len(pixel_stack) > 0:
        i += 1
        pos, cur_node = pixel_stack.pop()
        visited[pos[1], pos[0]][0] = 0
        if i % 1000 == 0:
            cv2.imshow("visited", visited)
            cv2.waitKey(1)

        if visited[pos[1], pos[0]][1] != 0:
            node_dists, nodes = tree.query(np.array([[pos[0] * 2, pos[1] * 2]]))
            node = nodes[0]
            if node != cur_node:
                if cur_node not in [e[0] for e in g.nodes[node].connections]:
                    dx = g.nodes[node].pos[0] - g.nodes[cur_node].pos[0]
                    dy = g.nodes[node].pos[1] - g.nodes[cur_node].pos[1]
                    cv2.line(img, g.nodes[node].pos, g.nodes[cur_node].pos,
                             (0, 255, 0), 1, cv2.LINE_AA)
                    g.link_nodes(node, cur_node, np.sqrt(dx * dx + dy * dy))
                cur_node = node

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x = pos[0] + dx
                y = pos[1] + dy
                if x >= 0 and x < width and y >= 0 and y < height:
                    if visited[y, x][0] != 0:
                        pixel_stack.append(((x, y), cur_node))
