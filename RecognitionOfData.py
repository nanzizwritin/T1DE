import cv2
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_doc_orientation_classify=False, use_doc_unwarping=False,
                use_textline_orientation=False, lang="en")

def to_grid(image_path, n_rows, n_cols, threshold=0.98):
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
            grid[r][c] = value if score >= 0.99 else "?"

    return grid    
    
def extract_record(left_path="left.png", right_path="right.png", rows=16):
    left  = to_grid(left_path,  rows, 9)
    right = to_grid(right_path, rows, 5)
    combined = [left[i] + right[i] for i in range(rows)]
    return combined

# ---------------- everything below this line uses the result ----------------
record = extract_record()       
def get_grid():
    global record
    return record

  # record is your 16-row 2D array

for row in record:             # just to see it; delete once you trust it
    print(row)
