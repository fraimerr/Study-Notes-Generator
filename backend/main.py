from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import imageio.v3 as iio
import pytesseract
import pypdf
import fitz
import google.generativeai as genai
import logging

# Set tesseract command
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

genai.configure(api_key="AIzaSyDeEBwtJr-V88B0tKI5onwtF1sQLuBAMbo")
model = genai.GenerativeModel(model_name="gemini-pro")

app = Flask(__name__)
CORS(app)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def read_image(file_path: str) -> str:
    try:
        logging.info(f"Reading image: {file_path}")
        img = iio.imread(file_path)
        text = pytesseract.image_to_string(img)
        logging.info(
            f"Extracted text from image: {text[:50]}..."
        )  # Log the first 50 characters
        return text
    except Exception as e:
        logging.error(f"Error reading image: {e}")
        return ""


def extract_images_from_pdf(pdf_path: str):
    images = []
    try:
        logging.info(f"Extracting images from PDF: {pdf_path}")
        pdf_document = fitz.open(pdf_path)
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_path = (
                    f"images/page_{page_num + 1}_image_{img_index + 1}.{image_ext}"
                )
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                images.append(image_path)
                logging.info(f"Extracted image: {image_path}")
    except Exception as e:
        logging.error(f"Error extracting images from PDF: {e}")
    return images


def read_pdf(file_path: str) -> str:
    text = ""
    try:
        logging.info(f"Reading PDF: {file_path}")
        with open(file_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)
            logging.info(f"Number of pages: {len(pdf_reader.pages)}")
            for page_number in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_number]
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                    logging.info(
                        f"Extracted text from page {page_number + 1}: {page_text[:50]}..."
                    )  # Log the first 50 characters

        if not text:
            logging.info("No text extracted with PyPDF2. Using OCR for scanned images.")
            images = extract_images_from_pdf(file_path)
            for image_path in images:
                text += read_image(image_path)
                os.remove(image_path)

    except Exception as e:
        logging.error(f"Error reading PDF: {e}")
    return text


@app.route("/")
def home():
    return "Welcome to Notes Summarizer!"


@app.route("/read", methods=["POST"])
def read():
    logging.info("Received /read request")
    if not "file" in request.files:
        logging.error("No file provided")
        return jsonify({"error": "No File Provided"}), 400

    file = request.files["file"]
    file_path = os.path.join("uploads", file.filename)
    logging.info(f"Saving file to: {file_path}")
    file.save(file_path)

    if file.filename.lower().endswith(".pdf"):
        text = read_pdf(file_path)
    elif file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
        text = read_image(file_path)
    else:
        return jsonify({"error": "Unsupported File Format"})

    os.remove(file_path)
    return jsonify({"text": text})


@app.route("/generate_notes", methods=["POST"])
def generate_notes():
    logging.info("Received /generate_notes request")
    if "file" not in request.files:
        logging.error("No file provided")
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    file_path = os.path.join("uploads", file.filename)
    logging.info(f"Saving file to: {file_path}")
    file.save(file_path)

    if file.filename.lower().endswith(".pdf"):
        text = read_pdf(file_path)
    elif file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
        text = read_image(file_path)
    else:
        logging.error(f"Unsupported file format: {file.filename}")
        return jsonify({"error": "Unsupported file format"}), 400

    os.remove(file_path)

    try:
        logging.info(f"Generating notes for: {text[:50]}...")
        res = model.generate_content(f"Convert to study notes for my exam: {text}")
        notes = res.text
        logging.info(f"Generated notes: {notes[:50]}...")
    except Exception as e:
        logging.error(f"Error generating study notes: {e}")
        return jsonify({"error": f"Error generating study notes: {e}"}), 500

    return jsonify({"notes": notes})


if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists("images"):
        os.makedirs("images")

    app.run("0.0.0.0", port=5000, debug=True)
