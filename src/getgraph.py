import cv2
import mazereader
import argparse
import processimage
import config
import sys

parser = argparse.ArgumentParser(description='Get a maze graph from an image')
parser.add_argument('image', help='Image of maze to solve')
parser.add_argument('--handdrawn', '-d',
                    dest='handdrawn', action='store_true',
                    help='Preprocess the image for a messier maze')
parser.add_argument('--scale', '-s',
                    dest='scale', type=float, default=None,
                    help='Scale factor to scale the image by before solving')
parser.add_argument('--tiles', '-t',
                    dest='tiles', action='store_true',
                    help='Use tiled skeletonization')

args = parser.parse_args()
args.nogui = True
args.pixellines = False
config.args = args

origImg = cv2.imread(config.args.image)
if origImg is None:
    print("Unable to load image file")
    sys.exit(-1)

img = origImg.copy()
img, scale = processimage.processimage(origImg, config.args.scale,
                                       config.args.handdrawn)
img2, graph = mazereader.read_maze(img)

print('---GRAPH START---')
for node in graph.nodes:
    print('---')
    print('{},{}'.format(node.pos[0] / scale, node.pos[1] / scale))
    for con, dist in node.connections:
        print('{},{}'.format(con, dist))
