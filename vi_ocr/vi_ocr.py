from google.cloud import vision
import io
import re
import os
import logging
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
from align.vi_process import clean_text
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)

class VOCR:
    def __init__(self, json_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS'] , error_logs = None , success_logs = None):
        print(json_path)
        self.client = vision.ImageAnnotatorClient.from_service_account_json(json_path)
        self.error_logs = error_logs
        self.success_logs = success_logs

        self.logger = logging.getLogger('VOCR')
        self.logger.setLevel(logging.DEBUG)

        # self.console_handler = logging.StreamHandler()
        # self.console_handler.setLevel(logging.WARNING)

        self.error_handler = logging.FileHandler(self.error_logs)
        self.error_handler.setLevel(logging.ERROR)

        self.success_handler = logging.FileHandler(self.success_logs)
        self.success_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        # self.console_handler.setFormatter(formatter)
        self.error_handler.setFormatter(formatter)
        self.success_handler.setFormatter(formatter)

        # self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.error_handler)
        self.logger.addHandler(self.success_handler)


    def detect_dir(self,input_dir, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        for file_name in tqdm(os.listdir(input_dir), desc="OCR VI: ", unit="file"):
            if file_name.endswith(".jpg"):
                file_path = os.path.join(input_dir, file_name)
                output_path = os.path.join(output_dir, file_name.replace(".jpg", ".txt"))
                try:
                    self.detect_file(file_path, output_path)
                except Exception as e:
                    print(f"{file_path} - Error: {e}")

    def detect_file(self, image_path, output_path):
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        try:
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
        except Exception as e:
            self.logger.error(f"{image_path} - Error Detect: {e}")

        if texts:
            try:
                with open(output_path, "w" , encoding='utf-8') as text_file:
                    text = clean_text(texts[0].description)
                    text_file.write(text)
                # self.logger.info(f"{image_path} - Success")
            except Exception as e:
                self.logger.error(f"{image_path} - Error Write: {e}")
        
def vi_ocr(vi_dir, output_txt_dir, creadiential_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS'], logs_dir=os.environ['LOG_DIR']):
    vocr = VOCR(
        json_path=creadiential_path ,
        error_logs=os.path.join(logs_dir, "error.log"),
        success_logs=os.path.join(logs_dir, "success.log")
    )
    try:
        vocr.detect_dir(input_dir=vi_dir, output_dir=output_txt_dir)
    except Exception as e:
        vocr.logger.error(f"Error: {e}")

# if __name__ == "__main__":
#     vi_dir = r"image_del"
#     output_txt_dir = "output/"
#     creadiential_path = "vi_ocr/vision_key.json"
#     logs_dir = "vi_ocr\\logs"
#     vi_ocr(vi_dir, output_txt_dir, creadiential_path, logs_dir)
