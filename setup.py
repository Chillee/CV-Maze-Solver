import numpy
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

extensions = [
    Extension("connections", ["connections.pyx"],
              include_dirs=[numpy.get_include()],
              extra_compile_args=["-O3"],
              extra_link_args=["-O3"]),
    Extension("skeletonize", ["skeletonize.pyx"],
              include_dirs=[numpy.get_include()],
              extra_compile_args=["-O3"],
              extra_link_args=["-O3"])
]

setup(
    ext_modules=cythonize(extensions, annotate=True)
)
