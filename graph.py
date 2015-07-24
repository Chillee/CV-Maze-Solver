class Node(object):
    def __init__(self, pos):
        self.pos = pos
        self.connections = []

class Graph(object):
    def __init__(self):
        self.nodes = {}
        self.connections = []
        self.next_node_id = 0

    def add_node(self, node):
        self.nodes[self.next_node_id] = node
        self.next_node_id += 1
        return self.next_node_id - 1

    def link_nodes(self, a, b):
        self.nodes[a].connections.append(b)
        self.nodes[b].connections.append(a)
        self.connections.append((a,b))
