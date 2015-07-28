import numpy as np
import scipy.spatial
from Queue import PriorityQueue

class Node(object):
    def __init__(self, pos):
        self.pos = pos
        self.connections = []

class Graph(object):
    def __init__(self):
        self.tree = None
        self.tree_changed = True
        self.nodes = []
        self.connections = []

    def add_node(self, node):
        self.tree_changed = True
        self.nodes.append(node)
        return len(self.nodes) - 1

    def link_nodes(self, a, b, d=1):
        self.nodes[a].connections.append((b, d))
        self.nodes[b].connections.append((a, d))
        self.connections.append((a,b, d))

    def build_kd_tree(self):
        if self.tree_changed or self.tree is None:
            self.tree_chnaged = False
            self.tree = scipy.spatial.KDTree(np.array([list(node.pos) for node in self.nodes]))
        return self.tree

    def dijkstra(self, start, end):
        dists = [float("inf") for i in self.nodes]
        dists[start] = 0
        prev = [-1 for i in self.nodes]

        curNodes = PriorityQueue()
        curNodes.put((0, start))

        while not curNodes.empty():
            curDist, index = curNodes.get()

            for connection in self.nodes[index].connections:
                newDist = dists[index] + connection[1]
                if newDist < dists[connection[0]]:
                    dists[connection[0]] = newDist
                    prev[connection[0]] = index
                    curNodes.put((newDist, connection[0]))

        curNode = end
        path =[]
        while curNode != -1:
            path.append(curNode)
            curNode = prev[curNode]
        return path[::-1]

