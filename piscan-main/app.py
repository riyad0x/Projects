import os
from flask import Flask, request, jsonify
from my_pytesseract import extract_text_from_image
from process_image import DocScanner
from database import *


app = Flask(__name__)


@app.route('/process_image', methods=['POST', 'GET'])
def process_image():
    # Check if an image file was sent in the request, if not send back an error notify that no image is sent
    if 'image' not in request.files:
        return jsonify({'error': 'No image file sent'})

    image_file = request.files['image']

    image_path = 'uploads/image.png'
    image_file.save(image_path)

    # processing the document to enhance quality and make easy to extract text from it and also detect and warp the document
    doc_scanner = DocScanner()
    doc_scanner.scan(image_path)

    # save the base name of the image in order to use it for saving the processed image and then give it to the text extractor
    basename = os.path.basename(image_path)

    scanned_image_path = 'scans/' + basename

    # Extract text from the processed image using pytesseract
    extracted_text = extract_text_from_image(scanned_image_path)

    # Store the extracted text in the database and commit it.
    sql = "INSERT INTO imagedata (info) VALUES (%s)"
    val = (extracted_text,)
    mycursor.execute(sql, val)
    mydb.commit()

    # Return the extracted text as a response to send it back to the frontend of the application
    return jsonify({'text': extracted_text})


if __name__ == '__main__':
    app.run()
