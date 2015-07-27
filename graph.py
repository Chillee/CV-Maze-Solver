import numpy as np
import scipy.spatial

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

    def link_nodes(self, a, b):
        self.nodes[a].connections.append(b)
        self.nodes[b].connections.append(a)
        self.connections.append((a,b))

    def build_kd_tree(self):
        return scipy.spatial.KDTree(np.array([list(node.pos) for node in self.nodes]))