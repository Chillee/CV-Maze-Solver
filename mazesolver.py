import cv2
import mazereader

img = cv2.imread("maze1.png")
ret = mazereader.read_maze(img)
if ret != None:
    img2, graph, start, end = ret
    cv2.imshow("image", img2)
    #solve the maze
    path = graph.dijkstra(start, end)
    last = None
    for node_id in path:
        node = graph.nodes[node_id]
        if last is not None:
            cv2.line(img, last.pos, node.pos, (255, 0, 0), 2, cv2.LINE_AA)
        last = node
    cv2.imshow("image_solved", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()