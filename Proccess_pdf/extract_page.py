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
        # Check if PDF file exists
        if not os.path.exists(self.pdf_file_path):
            raise FileNotFoundError(f"File not found: {self.pdf_file_path}")

        # Check if images already exist in output folder
        existing_files = sorted(os.listdir(self.output_folder))
        if existing_files:
            file_paths = [os.path.join(self.output_folder, file) for file in existing_files]
            result = ExtractPageResult(len(existing_files), file_paths)

            if logs:
                print(f"Total pages extracted: {len(existing_files)}")
                print(f"Pages saved at: {self.output_folder}")

            return result.return_dict() if return_dict else result

        # Convert PDF to images
        pages = fitz.open(self.pdf_file_path)
        image_name = os.path.splitext(os.path.basename(self.pdf_file_path))[0]  # Fix path extraction

        #Save each page as an image
        print(f"watting for {len(pages)} pages to be saved as images...")
        os.makedirs(self.nom_path,exist_ok=True)
        os.makedirs(self.quoc_ngu, exist_ok=True)
        page_names = []
        for page_num in tqdm(range(len(pages)), desc="proccessing extract: "):
            page = pages.load_page(page_num)
            zoom = dpi/72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            _image_name_ = f"{image_name}_{str(page_num+1).zfill(3)}.jpg"
            image_path = os.path.join(self.output_folder, _image_name_)
            pix.save(image_path)
            page_content = self.extract_page_content(image_path)
            if page_content:
                try:
                    if langdetect.detect(page_content) == "vi":
                        image_new = os.path.join(self.quoc_ngu, _image_name_)
                    else:
                        image_new = os.path.join(self.nom_path, _image_name_)
                    page_names.append(image_new)
                    shutil.move(image_path,image_new)
                except:
                    print(f"we can't proccessing this image: {image_path}")
            image_path = ""
            if logs and (page_num+1) % 50 == 0:
                print(f"Page {page_num + 1} saved at: {image_path}")
        if logs:
            print(f"Total pages extracted: {len(page_names)}")
            print(f"Pages saved at: {self.output_folder}")
        
        result = ExtractPageResult(len(pages), page_names)
        return result.return_dict() if return_dict else result
