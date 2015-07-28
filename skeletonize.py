import numpy as np
from scipy import weave


def thinning_iteration(im, iter):
    I, M = im, np.zeros(im.shape, np.uint8)
    # expr = """
    # for (int i = 1; i < NI[0]-1; i++)
    # {
    #     for (int j = 1; j < NI[1]-1; j++)
    #     {
    #         int p2 = I2(i-1, j);
    #         int p3 = I2(i-1, j+1);
    #         int p4 = I2(i, j+1);
    #         int p5 = I2(i+1, j+1);
    #         int p6 = I2(i+1, j);
    #         int p7 = I2(i+1, j-1);
    #         int p8 = I2(i, j-1);
    #         int p9 = I2(i-1, j-1);
    #
    #             int C  = (!p2 & (p3 | p4)) + (!p4 & (p5 | p6)) +
    #                      (!p6 & (p7 | p8)) + (!p8 & (p9 | p2));
    #             int N1 = (p9 | p2) + (p3 | p4) + (p5 | p6) + (p7 | p8);
    #             int N2 = (p2 | p3) + (p4 | p5) + (p6 | p7) + (p8 | p9);
    #             int N  = N1 < N2 ? N1 : N2;
    #             int m  = iter == 0 ? ((p6 | p7 | !p9) & p8) :
    #                                  ((p2 | p3 | !p5) & p4);
    #
    #             if (C == 1 && (N >= 2 && N <= 3) && m == 0)
    #                 M2(i,j) = 1;
    #     }
    # }
    # """
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
    weave.inline(expr, ["I", "iter", "M"], extra_compile_args=["-O3"])
    return (I & ~M)


def skeletonize_zhang_shuen(src):
    dst = src.copy() / 255
    prev = np.zeros(src.shape[:2], np.uint8)
    diff = None
    while True:
        dst = thinning_iteration(dst, 0)
        dst = thinning_iteration(dst, 1)
        diff = np.absolute(dst - prev)
        prev = dst.copy()
        if np.sum(diff) == 0:
            break
    return dst * 255
