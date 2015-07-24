import cv2
import timeit

print timeit.timeit("counter += 1", "counter = 0", number=100000000)