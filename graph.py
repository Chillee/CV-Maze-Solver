import numpy as np
import scipy.spatial
from Queue import PriorityQueue

class Node(object):
    def __init__(self, pos):
        self.pos = pos
        self.connections = []

class Graph(object):
    def __init__(self):
        self.nodes = []
        self.connections = []

    def add_node(self, node):
        self.nodes.append(node)
        return len(self.nodes) - 1

    def link_nodes(self, a, b, d):
        self.nodes[a].connections.append((b, d))
        self.nodes[b].connections.append((a, d))
        self.connections.append((a,b, d))

    def build_kd_tree(self):
        return scipy.spatial.KDTree(np.array([list(node.pos) for node in self.nodes]))

    def dijkstra(self, start, end):
        dists = [float("inf") for i in self.nodes]
        dists[start] = 0
        prev = [-1 for i in self.nodes]

        curNodes = Queue.PriorityQueue()
        curNodes.put((0, start))

        while curNodes is not None:
            index, curNode = curNodes.get()
            for connection in self.nodes[index].connections:
                newDist = dist[index] + connection[1]
                if newDist < dist[connection[0]]:
                    dist[connection[0]] = newDist
                    prev[connection[0]] = index
        return dist[end]
    