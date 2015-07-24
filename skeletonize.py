import cv2
import numpy as np
from scipy import weave

#thin all lines to 1 pixel wide
def skeletonize(img):
    size = np.size(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    ret = np.zeros(img.shape, np.uint8)
    while True:
        eroded = cv2.erode(img, kernel)
        temp = cv2.dilate(eroded, kernel)
        temp = cv2.subtract(img, temp)
        ret = cv2.bitwise_or(ret, temp)
        img = eroded.copy()

        zeros = size - cv2.countNonZero(img)
        if zeros == size:
            break

    return ret


def skeletonize_guo_hall(img):
    h,w,d = img.shape
    def trans(dx, dy):
        mat = np.array([[1, 0, dx],
                        [0, 1, dy]], np.uint8)
        return cv2.warpAffine(img, mat, (w, h))
    p1 = img
    p2 = trans(0, -1)
    p2 = trans(1, -1)
    p3 = trans(1, 0)
    p4 = trans(1, 1)
    p5 = trans(0, 1)
    p6 = trans(0, 1)
    p7 = trans(-1, -1)
    p8 = trans(-1, 0)
    p9 = trans(-1, 1)

def _thinningIteration(im, iter):
    I, M = im, np.zeros(im.shape, np.uint8)
    expr = """
    for (int i = 1; i < NI[0]-1; i++) {
    for (int j = 1; j < NI[1]-1; j++) {
    int p2 = I2(i-1, j);
    int p3 = I2(i-1, j+1);
    int p4 = I2(i, j+1);
    int p5 = I2(i+1, j+1);
    int p6 = I2(i+1, j);
    int p7 = I2(i+1, j-1);
    int p8 = I2(i, j-1);
    int p9 = I2(i-1, j-1);
    int A = (p2 == 0 && p3 == 1) + (p3 == 0 && p4 == 1) +
    (p4 == 0 && p5 == 1) + (p5 == 0 && p6 == 1) +
    (p6 == 0 && p7 == 1) + (p7 == 0 && p8 == 1) +
    (p8 == 0 && p9 == 1) + (p9 == 0 && p2 == 1);
    int B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9;
    int m1 = iter == 0 ? (p2 * p4 * p6) : (p2 * p4 * p8);
    int m2 = iter == 0 ? (p4 * p6 * p8) : (p2 * p6 * p8);
    if (A == 1 && B >= 2 && B <= 6 && m1 == 0 && m2 == 0) {
    M2(i,j) = 1;
    }
    } 
    }
    """
    weave.inline(expr, ["I", "iter", "M"])
    return (I & ~M)

def skeletonize_zhang_shuen(src):
    dst = src.copy() / 255
    prev = np.zeros(src.shape[:2], np.uint8)
    diff = None
    while True:
        dst = _thinningIteration(dst, 0)
        dst = _thinningIteration(dst, 1)
        diff = np.absolute(dst - prev)
        prev = dst.copy()
        if np.sum(diff) == 0:
            break
    return dst * 255

if __name__ == "__main__":
    src = cv2.imread("circular_maze1.png")
    if src == None:
        sys.exit()
    bw = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    _, bw2 = cv2.threshold(bw, 10, 255, cv2.THRESH_BINARY)
    bw2 = thinning(bw2)
    cv2.imshow("src", bw)
    cv2.imshow("thinning", bw2)
    cv2.waitKey()