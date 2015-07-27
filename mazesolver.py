import cv2
import mazereader

img = cv2.imread("circular_maze1.png")
ret = mazereader.read_maze(img)
if ret != None:
    img2, graph = ret
    cv2.imshow("image", img2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()