import cv2
cimport numpy as np
import numpy as np
from scipy import weave
from skeletonize_c import thinning_iteration
import config

cdef unsigned int TILE_SIZE = 256


def skeletonize_zhang_shuen(np.ndarray[np.uint8_t, ndim=2] src):
    cdef unsigned int xx, yy, width, height

    cdef np.ndarray[np.uint8_t, ndim=2] dst = src.copy() / 255
    cdef np.ndarray[np.uint8_t, ndim=2] diff, prev
    width = src.shape[0]
    height = src.shape[1]
    prev = np.zeros((width, height), np.uint8)
    if config.args.tiles:
        tiles = []
        for xx in range(0, width / TILE_SIZE + 1):
            for yy in range(0, height / TILE_SIZE + 1):
                tiles.append((xx, yy))
        print("Using {} tiles".format(len(tiles)))
        done = False
        i = 0
        while len(tiles) > 0:
            i += 1
            for xx, yy in tiles:
                x0 = xx * TILE_SIZE + 1
                x1 = min((xx + 1) * TILE_SIZE + 1, width - 1)
                y0 = yy * TILE_SIZE + 1
                y1 = min((yy + 1) * TILE_SIZE + 1, height - 1)
                dst[x0:x1, y0:y1] = thinning_iteration(prev, i % 2, x0, y0, x1, y1)[x0:y0, x1:y1]
                diff = np.absolute(dst[x0:x1, y0:y1] - prev[x0:x1, y0:y1])
                if np.sum(diff) == 0:
                    if np.all(dst[x0:x1, y0:y1]):
                        dst[x0:x1, y0:y1] = 0
                    tiles.remove((xx, yy))
            prev = dst.copy()
    else:
        while True:
            dst = thinning_iteration(dst, 0, 1, 1, width - 1, height - 1)
            dst = thinning_iteration(dst, 1, 1, 1, width - 1, height - 1)
            diff = np.absolute(dst - prev)
            if np.sum(diff) == 0:
                break
            prev = dst.copy()
    return dst * 255
