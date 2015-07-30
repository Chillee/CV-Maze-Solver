from cpython cimport array as c_array
from cython.view cimport array as cvarray
from array import array
import copy
import numpy as np
cimport numpy as np
cimport cython
import cv2

@cython.boundscheck(False)
@cython.infer_types(True)
def get_connections(g,
                    np.ndarray[np.uint8_t, ndim=2] skeleton,
                    np.ndarray[np.uint8_t, ndim=2] eroded):
    skeleton = cv2.resize(skeleton, (0, 0), fx=0.5, fy=0.5)
    cdef int height = skeleton.shape[0]
    cdef int width = skeleton.shape[1]

    cdef int x, y, dx, dy, xx, yy
    cdef np.ndarray[np.uint8_t, ndim=3] visited = np.zeros([height, width, 3], dtype=np.uint8)
    visited[:,:,0] = skeleton
    visited[:,:,1] = 0
    visited[:,:,2] = 0
    cdef np.ndarray[np.uint16_t, ndim=2] node_map = np.zeros([height, width], dtype=np.uint16)

    for idx, node in enumerate(g.nodes):
        x = int(node.pos[0] / 2)
        y = int(node.pos[1] / 2)
        visited[y-1:y+2, x-1:x+2, 1] = 255
        node_map[y-1:y+2, x-1:x+2] = idx

    pixel_stack_pos = [array('i', [int(g.nodes[0].pos[0] / 2), int(g.nodes[0].pos[1] / 2)])]
    pixel_stack_node = [0]
    pixel_stack_path = [[]]

    unprocessed_nodes = range(0, len(g.nodes))

    cdef int group = 0
    #cdef int[2] pos
    cdef int i = 0
    while len(pixel_stack_pos) > 0:
        pos = pixel_stack_pos.pop()
        cur_node = pixel_stack_node.pop()
        path = pixel_stack_path.pop()

        g.nodes[cur_node].group = group
        if cur_node in unprocessed_nodes:
            unprocessed_nodes.remove(cur_node)

        x = pos[0]
        y = pos[1]

        visited[y, x, 0] = 0

        i += 1
        # if i % 10 == 0:
        #     cv2.imshow("visited", visited)
        #     cv2.waitKey(1)

        path.append((pos[0] * 2, pos[1] * 2))
        if visited[y, x, 1] != 0:
            node = node_map[y, x]
            if node != cur_node:
                if cur_node not in [e[0] for e in g.nodes[node].connections]:
                    xx = g.nodes[node].pos[0] - g.nodes[cur_node].pos[0]
                    yy = g.nodes[node].pos[1] - g.nodes[cur_node].pos[1]
                    g.link_nodes(node, cur_node, np.sqrt(xx * xx + yy * yy), path)
                cur_node = node
                path = path[:-1]

        num_children = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                xx = x + dx
                yy = y + dy
                if xx >= 0 and xx < width and yy >= 0 and yy < height:
                    if visited[yy, xx, 0] != 0:
                        num_children += 1
                        pixel_stack_pos.append(array('i', [xx, yy]))
                        pixel_stack_node.append(cur_node)
                        if num_children == 0:
                            pixel_stack_path.append(path)
                        else:
                            pixel_stack_path.append(copy.copy(path))

        if len(pixel_stack_pos) == 0 and len(unprocessed_nodes) > 0:
            group += 1
            n = unprocessed_nodes.pop()
            pixel_stack_pos.append(array('i', [int(g.nodes[n].pos[0] / 2), int(g.nodes[n].pos[1] / 2)]))
            pixel_stack_node.append(n)
            pixel_stack_path.append([])
