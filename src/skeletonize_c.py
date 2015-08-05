import numpy as np
from scipy import weave

no_openmp = False


def thinning_iteration(im, iter, x0, y0, x1, y1):
    global no_openmp

    I, M = im, np.zeros(im.shape, np.uint8)
    expr = """
    #define I_idx(i, j) I[(i) * NI[1] + (j)]
    #pragma omp parallel for schedule(static)
    for (int i = x0; i < x1; i++) {
        for (int j = y0; j < y1; j++) {
            int p2 = I_idx(i-1, j);
            int p3 = I_idx(i-1, j+1);
            int p4 = I_idx(i, j+1);
            int p5 = I_idx(i+1, j+1);
            int p6 = I_idx(i+1, j);
            int p7 = I_idx(i+1, j-1);
            int p8 = I_idx(i, j-1);
            int p9 = I_idx(i-1, j-1);
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
    if no_openmp:
        weave.inline(expr, ["I", "iter", "M", "x0", "y0", "x1", "y1"],
                     extra_compile_args=["-O3"])
    else:
        try:
            weave.inline(expr, ["I", "iter", "M", "x0", "y0", "x1", "y1"],
                         extra_compile_args=["-O3", "-fopenmp"],
                         extra_link_args=["-fopenmp", "-lgomp"])
        except weave.build_tools.CompileError:
            no_openmp = True
            weave.inline(expr, ["I", "iter", "M", "x0", "y0", "x1", "y1"],
                         extra_compile_args=["-O3"])
    return (I & ~M)
