import requests
from dataclasses import dataclass
import os
from .dtype_client import UploadImageReq, UploadImageRes, OCRReq , OCRRes
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)

def get_firebase_token():
    return "eyJhbGciOiJSUzI1NiIsImtpZCI6IjQ3YWU0OWM0YzlkM2ViODVhNTI1NDA3MmMzMGQyZThlNzY2MWVmZTEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vY2xjLWhhbS1ub24iLCJhdWQiOiJjbGMtaGFtLW5vbiIsImF1dGhfdGltZSI6MTc1MjA0MDU4NCwidXNlcl9pZCI6InRrS3JOcmVFVVBjNDJLMVBoZVloeDU4THR2cjEiLCJzdWIiOiJ0a0tyTnJlRVVQYzQySzFQaGVZaHg1OEx0dnIxIiwiaWF0IjoxNzUyMDQwNTg0LCJleHAiOjE3NTIwNDQxODQsImVtYWlsIjoiZGV0YWlAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbImRldGFpQGdtYWlsLmNvbSJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.L1w9bt5qh8Hm6BMC091bw6GiswtaMYlE3XgE_euN4c-HNHaq5Pfk6HwU8ggTVuxJCmQg1tRdaQm3NGovjPHucDzB2VWwKCgW05lUz7622-bY-FzOt0TB11Abhe2ldzBDy5LIgVcafZ7AsIwUrOQbVPScqSyhcgaFEvaQ4W24kCOfis2qiLwiXuiHvVLvJEgZQvzDcGCoxZe37bu05D1QOV0-qG_JKJhaXdSbVjBtOCakZCTJ0W9ax_XBzgqywsfHOB-4qqm4YKVuxLLl0UQCa9627rvNfdumE-YZcuNLCySWO_KRD8E3TuM38h6cMNuoqgX-eQDvO2qbKJTNZl08bg; path=/refresh_token=AMf-vBzXpDU7RyzZ_RJquw4989qQTYdbAMLMJ2c74nqs-ARe2x2b2DSV6RH1Ev_yOHrEQtDlb2Ul7109ATq9IVKgOW2VMphCYFFRN7gk6ylkYh88Hy5W3j4_-gggWqSb38JMsCe2s-Hbk1kBb2S_8siFSS6T7Yt2bUSWQEzVhjWQ0wYeTR76Wi2eqUl3KtayIoq_a-c9jNSd"

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
            "Authorization": f"Bearer {get_firebase_token()}",
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
            "Authorization": f"Bearer {get_firebase_token()}",
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
            "Authorization": f"Bearer {get_firebase_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        body = {
            "file_name": req.file_name,
            "ocr_id":  os.environ["TYPE_OCR"],
            "lang_type": os.environ["TYPE_LANG"],
            "reading_direction": os.environ["TYPE_READING_DIRECTION"],
            "font_type": os.environ["TYPE_FONT"]
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