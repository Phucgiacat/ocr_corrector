from pdf2image import convert_from_path
from dataclasses import dataclass
import os
import fitz
from tqdm import tqdm
from google.cloud import vision
import io
import ast
import pdfplumber
import langdetect
import shutil
from pypdf import PdfReader
import pytesseract
from PIL import Image

creadiential_path = "D:/learning/lab NLP/Tool_news/AutoLabel_script/vi_ocr/vision_key.json"

@dataclass
class ExtractPageResult:
    total_pages: int
    pages: list

    def return_dict(self):
        return {
            "total_pages": self.total_pages,
            "pages": self.pages[:5],  # Return only first 5 pages for preview
        }

class ExtractPages:
    def __init__(self, pdf_file_path, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        self.pdf_file_path = pdf_file_path
        self.output_folder = output_folder
        self.nom_path = f"{output_folder}/image/Han Nom"
        self.quoc_ngu = f"{output_folder}/image/Quoc Ngu"
        print(f"PDF file path: {self.pdf_file_path}")
        print(f"Output folder: Nom -> {self.nom_path}, QN -> {self.quoc_ngu}")

    # Function to call GPT-4o API with the base64 image and a question
    def extract_page_content(self, image_path):
        """Sử dụng Google Cloud Vision để OCR văn bản từ hình ảnh"""
        
        # Khởi tạo Client
        client = vision.ImageAnnotatorClient.from_service_account_json(creadiential_path)

        # Đọc file ảnh
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        # Gửi yêu cầu OCR
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            return texts[0].description
        else:
            return ''

    def extract(self, logs=False, return_dict=False, dpi=500):
        if not os.path.exists(self.pdf_file_path):
            raise FileNotFoundError(f"File not found: {self.pdf_file_path}")

        existing_files = sorted(os.listdir(self.output_folder))
        if existing_files:
            file_paths = [os.path.join(self.output_folder, f) for f in existing_files]
            result = ExtractPageResult(len(existing_files), file_paths)
            if logs:
                print(f"Total pages extracted: {len(existing_files)}")
                print(f"Pages saved at: {self.output_folder}")
            return result.return_dict() if return_dict else result

        # Mở bằng cả 2 thư viện
        reader = PdfReader(self.pdf_file_path)
        doc = fitz.open(self.pdf_file_path)

        num_pages = len(reader.pages)
        image_name = os.path.splitext(os.path.basename(self.pdf_file_path))[0]

        print(f"Waiting for {num_pages} pages to be processed...")
        os.makedirs(self.nom_path, exist_ok=True)
        os.makedirs(self.quoc_ngu, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

        page_names = []

        for page_num in tqdm(range(num_pages), desc="Processing extract: "):
            _page_id = f"{image_name}_{str(page_num + 1).zfill(3)}"
            try:
                # Trích text bằng pypdf
                raw_text = reader.pages[page_num].extract_text()
                if raw_text and raw_text.strip():
                    detected_lang = langdetect.detect(raw_text)
                    save_folder = self.quoc_ngu if detected_lang == "vi" else self.nom_path
                    text_file_path = os.path.join(save_folder, f"{_page_id}.txt")
                    with open(text_file_path, "w", encoding="utf-8") as f:
                        f.write(raw_text)
                    page_names.append(text_file_path)
                else:
                    # Không có text → render ảnh bằng fitz để OCR
                    page = doc.load_page(page_num)
                    zoom = dpi / 72
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    image_path = os.path.join(self.output_folder, f"{_page_id}.jpg")
                    pix.save(image_path)

                    # OCR
                    page_content = self.extract_page_content(image_path)
                    if page_content:
                        detected_lang = langdetect.detect(page_content)
                        save_folder = self.quoc_ngu if detected_lang == "vi" else self.nom_path
                    else:
                        save_folder = self.nom_path

                    image_new = os.path.join(save_folder, f"{_page_id}.jpg")
                    shutil.move(image_path, image_new)
                    page_names.append(image_new)

            except Exception as e:
                print(f"⚠️ Could not process page {page_num + 1}: {e}")

            if logs and (page_num + 1) % 50 == 0:
                print(f"Page {page_num + 1} processed.")

        if logs:
            print(f"Total pages extracted: {len(page_names)}")

        result = ExtractPageResult(num_pages, page_names)
        return result.return_dict() if return_dict else result