from .logger import Logger
import os
import json
from .ocr_client import OCR, UploadImageReq, OCRReq
import time
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv(".env")
import os

def  nom_ocr(nom_dir, output_json_dir, output_image_dir, start=0):
    nom_logger = Logger('NOMOCR', stdout='DEBUG', file='DEBUG', file_name="nom_ocr/logs/main.log")
    count = 1
    for file in tqdm(os.listdir(nom_dir) , desc="Processing ocr images: "):
        if count < start:
            continue
        time.sleep(1)
        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'
        ocr_client = OCR()
        os.makedirs(output_image_dir,exist_ok=True)
        os.makedirs(output_json_dir, exist_ok=True)
        image_path = os.path.join(nom_dir, file)
        output_json_path = os.path.join(output_json_dir, file.replace(".jpg", ".json"))
        output_image_path = os.path.join(output_image_dir, file.replace(".jpg", ".jpeg"))

        req = UploadImageReq(image=image_path)
        try:
            result = ocr_client.upload_image(req, agent=agent)
        except Exception as e:
            nom_logger.error(f"Error: {image_path} - Upload: {e}")
            break

        req = OCRReq(ocr_id=1, file_name=result.data.file_name)
        try:
            result = ocr_client.ocr(req, output_file=output_json_path, agent=agent)
        except Exception as e:
            nom_logger.error(f"Error: {image_path} - OCR: {e}")
            break

        with open(output_json_path, "r", encoding='utf-8') as f:
            data = json.load(f)
            file_name = data["data"]["result_file_name"]
        
        try:
            ocr_client.download_image(file_name, output_image_path, agent=agent)
        except Exception as e:
            nom_logger.error(f"Error: {image_path} - Download: {e}")
            break

        # nom_logger.info(f"Count: {idx}- OCR: {image_path} - {output_json_path} - {output_image_path}")
        count += 1
        
# if __name__ == "__main__":
#     nom_dir = "data/nom/image_proccess"
#     output_json_dir = "output/json_1"
#     output_image_dir = "output/images_1"
#     index = 237
#     nom_ocr(nom_dir, output_json_dir, output_image_dir, index)