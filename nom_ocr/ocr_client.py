import requests
from dataclasses import dataclass
import os
from .dtype_client import UploadImageReq, UploadImageRes, OCRReq , OCRRes
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv
load_dotenv(".env")


class OCR:
    def __init__(self):
        self.client = requests.session()
        self.base_url = f"https://{os.environ['SN_DOMAIN']}/"
        # self.proxies = proxies or {}

    def upload_image(self, req: UploadImageReq , agent):
        url = self.base_url + "api/web/clc-sinonom/image-upload"

        if not os.path.exists(req.image):
            raise FileNotFoundError(f"File not found: {req.image}")

        # agent postman
        headers = {
            "User-Agent": agent,  
            "Authorization": "Bearer 123"
        }

        with open(req.image, "rb") as f:
            files = {"image_file": f}
            try:
                response = self.client.post(url, files=files, headers=headers, verify=False)
                if response.status_code != 200:
                    raise Exception(f"Failed to upload image: {response.text}")
                if response.json().get("is_success", False) == False:
                    errors = response.json().get("message", "BlockIP")["title"]
                    raise Exception(errors)
                
                return UploadImageRes.dict2obj(response.json())
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                raise e

    def download_image(self, file_name: str, save_path: str , agent):
        url = f"{self.base_url}api/web/clc-sinonom/image-download?file_name={file_name}"

        headers = {
            "User-Agent": agent,  
            "Authorization": "Bearer 123",
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            response = self.client.get(url, headers=headers, verify=False)
            
            if "image" not in response.headers.get("Content-Type", ""):
                print("Error: Response is not an image. Check the URL or headers.")
                return

            response.raise_for_status()

            with open(save_path, "wb") as f:
                f.write(response.content)

            return save_path

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            raise e

    def ocr(self, req: OCRReq, agent, output_file: str = "ocr_output.json"):
        url = f"{self.base_url}api/web/clc-sinonom/image-ocr"
        headers = {
            "User-Agent": agent,  # Random User-Agent
            "Authorization": "Bearer 123",
            "Content-Type": "application/json; charset=utf-8"
        }
        body = {
            "ocr_id": req.ocr_id,
            "file_name": req.file_name
        }

        try:
            response = self.client.post(url, headers=headers, json=body, verify=False)
            response.encoding = "utf-8"

            if response.status_code == 504:
                raise Exception("Gateway Timeout")
            
            response_json = response.json()

            if response.json().get("is_success", False) == False:
                errors = json.dumps(response.json().get("message", "BlockIP"), ensure_ascii=True)
                raise Exception(errors)
            

            # Encode the JSON with Unicode escape sequences
            encoded_json = json.dumps(response_json, ensure_ascii=False, indent=4)

            # Save the encoded JSON to a file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(encoded_json)

            # Return the response as an object
            return OCRRes.dict2obj(response_json)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            raise e