import cv2
import numpy as np

IMAGE = "image.png"
CELL_W, CELL_H = 100, 50

def order_points(pts):
    pts = np.array(pts, dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).flatten()
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]
    return np.float32([tl, tr, br, bl])

def straighten(image_path, save_as, label, n_cols, n_rows):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"can't read {image_path}")
    scale = 900 / max(img.shape[0], img.shape[1])
    small = cv2.resize(img, None, fx=scale, fy=scale)
    points = []

    def click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((int(x / scale), int(y / scale)))
            cv2.circle(small, (x, y), 6, (0, 0, 255), -1)
            cv2.imshow(label, small)

    cv2.imshow(label, small)
    cv2.setMouseCallback(label, click)
    print(f"{label}: click 4 corners of the DATA area — TOP corners just BELOW the header row. Any order. Then press any key.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    width  = n_cols * CELL_W
    height = n_rows * CELL_H
    src = order_points(points)
    dst = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    cv2.imwrite(save_as, cv2.warpPerspective(img, matrix, (width, height)))
    print(f"Saved {save_as} ({width}x{height})")

straighten(IMAGE, "left.png",  "LEFT table",  n_cols=8, n_rows=16)
straighten(IMAGE, "right.png", "RIGHT table", n_cols=5, n_rows=16)