from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang='en'
)

result = ocr.predict('image1.png')   # change 'photo.jpg' to your filename if different

for res in result:
    res.print()                 # dumps everything it read
    res.save_to_img('output')   # saves your photo with boxes drawn on what it found
    res.save_to_json('output')  # saves raw results as JSON