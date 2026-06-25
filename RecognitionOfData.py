import cv2
import numpy as np
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_doc_orientation_classify=False, use_doc_unwarping=False,
                use_textline_orientation=False, lang="en")


def order_points(pts):
    pts = np.array(pts, dtype="float32")
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([
        pts[np.argmin(s)],   # top-left
        pts[np.argmin(d)],   # top-right
        pts[np.argmax(s)],   # bottom-right
        pts[np.argmax(d)],   # bottom-left
    ], dtype="float32")


def warp_from_corners(image_path, corners, save_as, n_cols, n_rows, CELL_W=100, CELL_H=50):
    img = cv2.imread(image_path)
    pts = order_points(corners)
    width, height = n_cols * CELL_W, n_rows * CELL_H
    dst = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype="float32")
    M = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(img, M, (width, height))
    cv2.imwrite(save_as, warped)
    return save_as


def to_grid(image_path, n_rows, n_cols, threshold=0.99):
    img = cv2.imread(image_path)
    H, W = img.shape[:2]
    row_h = H / n_rows
    col_w = W / n_cols

    result = ocr.predict(image_path)[0]
    texts  = result["rec_texts"]
    boxes  = result["rec_polys"]
    scores = result["rec_scores"]

    grid = [["" for _ in range(n_cols)] for _ in range(n_rows)]
    for value, box, score in zip(texts, boxes, scores):
        xs = [p[0] for p in box]; ys = [p[1] for p in box]
        r = int((sum(ys) / len(ys)) / row_h)
        c = int((sum(xs) / len(xs)) / col_w)
        if 0 <= r < n_rows and 0 <= c < n_cols:
            grid[r][c] = value if score >= threshold else "?"
    return grid


def extract_from_corners(image_path, all_corners, rows=16, insulin_cols=5):
    left_corners  = all_corners[:4]
    right_corners = all_corners[4:]
    warp_from_corners(image_path, left_corners,  "left.png",  n_cols=9, n_rows=rows)
    warp_from_corners(image_path, right_corners, "right.png", n_cols=insulin_cols, n_rows=rows)
    left  = to_grid("left.png",  rows, 9)
    right = to_grid("right.png", rows, insulin_cols)
    combined = []
    for i in range(rows):
        insulin = right[i] + [""] * (5 - insulin_cols)
        combined.append(left[i] + insulin)
    return combined