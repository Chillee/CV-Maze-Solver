import argparse
import tempfile
import json
import struct
import config
import thread
import time
import sys
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.python import log
import processimage
import mazereader
import cv2

TOK_CLIENT_START_PROCESSING = 0

queue = []
completed_jobs = {}
job_id = 0


class Args(object):
    def __init__(self, handdrawn):
        self.handdrawn = handdrawn
        self.scale = None
        self.tiles = False
        self.nogui = True
        self.pixellines = False


def process_mazes():
    while True:
        time.sleep(2)
        if len(queue) != 0:
            jid, handdrawn, scale, fname = queue.pop()
            print("Processing job {}".format(jid))
            config.args = Args(handdrawn)
            orig_img = cv2.imread(fname)
            if orig_img is None:
                print("Unable to load image file {}".format(fname))
                return
            img, scale = processimage.processimage(orig_img, scale, handdrawn)
            img2, graph = mazereader.read_maze(img)
            completed_jobs[jid] = (graph, scale)


class MazeWorker(Protocol):
    def connectionMade(self):
        self.jid = -1
        self.handdrawn = False
        self.length = None
        self.extension = None
        self.scale = None
        self.data = ""
        print("Got connection")

    def read_data(self, data):
        self.data = self.data + data
        if len(self.data) == self.length:
            tf = tempfile.NamedTemporaryFile(suffix='.' + self.extension)
            fname = tf.name
            tf.close()
            tf = open(fname, 'wb')
            tf.write(self.data)
            tf.close()
            queue.append((self.jid, self.handdrawn, self.scale, fname))
            while self.jid not in completed_jobs:
                time.sleep(1)
            print("Completed job {}".format(self.jid))
            graph, scale = completed_jobs[self.jid]
            del completed_jobs[self.jid]

            def serialize_node(node):
                return {
                    'pos': [float(node.pos[0]) / scale, float(node.pos[1]) / scale],
                    'connections': [{'other': other, 'dist': float(dist)}
                                    for other, dist in node.connections]
                }
            graph_json = json.dumps(
                [serialize_node(node) for node in graph.nodes])
            self.transport.write(graph_json)
            self.transport.loseConnection()

    def dataReceived(self, data):
        global job_id

        if self.length is not None:
            self.read_data(data)
            return

        token = data[0]
        data = data[1:]

        if ord(token) == TOK_CLIENT_START_PROCESSING:
            self.jid = job_id
            print("Got job: {} ({})".format(self.jid, self.length))
            job_id += 1
            handdrawn, extension, scale, length = struct.unpack('>?3sfI', data[:12])
            self.extension = extension
            self.length = length
            self.handdrawn = handdrawn
            self.scale = None if abs(scale - 0.0) < 0.001 else scale
            self.read_data(data[12:])
        else:
            print("Unknown token {}".format(ord(token)))


class MazeWorkerFactory(Factory):
    protocol = MazeWorker

    def __init__(self):
        pass

parser = argparse.ArgumentParser(description='Run the maze solving worker server')
parser.add_argument('--port', '-p', dest='port', type=int, default=8007,
                    help="Port to run the server on")
args = parser.parse_args()

thread.start_new_thread(process_mazes, ())

log.startLogging(sys.stdout)
endpoint = TCP4ServerEndpoint(reactor, args.port)
endpoint.listen(MazeWorkerFactory())
reactor.run()
