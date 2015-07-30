import copy
import numpy as np
import scipy.spatial
from Queue import PriorityQueue


class Node(object):
    def __init__(self, pos, group=0):
        self.group = group
        self.pos = pos
        self.connections = []

    def dist(self, other):
        dx = self.pos[0] - other.pos[0]
        dy = self.pos[1] - other.pos[1]
        return np.sqrt(dx * dx + dy * dy)


class Graph(object):
    def __init__(self):
        self.nodes = []
        self.connections = {}

    def add_node(self, node):
        self.nodes.append(node)
        return len(self.nodes) - 1

    def link_nodes(self, a, b, d=1, pixels=[]):
        self.nodes[a].connections.append((b, d))
        self.nodes[b].connections.append((a, d))
        self.connections[(a, b)] = (d, pixels)
        self.connections[(b, a)] = (d, pixels)

    def split_long_edges(self):
        for a, b in copy.copy(self.connections):
            dist, pixels = self.connections[(a, b)]
            if dist > 25:
                # split into multiple nodes
                num_nodes = int(dist / 25 + 1)
                last_node = b
                for i in range(0, num_nodes):
                    # lerp the positions
                    alpha = float(i) / num_nodes
                    inv_alpha = 1 - alpha
                    x = int(alpha * self.nodes[a].pos[0] +
                            inv_alpha * self.nodes[b].pos[0])
                    y = int(alpha * self.nodes[a].pos[1] +
                            inv_alpha * self.nodes[b].pos[1])
                    new_node = self.add_node(Node((x, y), self.nodes[a].group))
                    self.link_nodes(new_node, last_node,
                                    self.nodes[last_node].dist(
                                        self.nodes[new_node]),
                                    pixels[(len(pixels) * i) / num_nodes:
                                           (len(pixels) * (i + 1)) / num_nodes]
                                    )
                    last_node = new_node
                self.link_nodes(last_node, b,
                                self.nodes[last_node].dist(self.nodes[b]),
                                pixels[(len(pixels) * (num_nodes - 1)) /
                                       num_nodes:])

    def build_kd_tree(self):
        return scipy.spatial.KDTree(
            np.array([node.pos for node in self.nodes]))

    def dijkstra(self, start, end):
        dists = [float("inf") for i in self.nodes]
        dists[start] = 0
        prev = [-1 for i in self.nodes]

        cur_nodes = PriorityQueue()
        cur_nodes.put((0, start))

        while not cur_nodes.empty():
            curDist, index = cur_nodes.get()

            for connection in self.nodes[index].connections:
                new_dist = dists[index] + connection[1]
                if new_dist < dists[connection[0]]:
                    dists[connection[0]] = new_dist
                    prev[connection[0]] = index
                    cur_nodes.put((new_dist, connection[0]))

        cur_node = end
        path = []
        while cur_node != -1:
            path.append(cur_node)
            cur_node = prev[cur_node]
        return path[::-1]
