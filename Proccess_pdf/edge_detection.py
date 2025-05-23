import cv2
import matplotlib.pyplot as plt
import os
import numpy as np
from ultralytics import YOLO
from tqdm import tqdm
import contextlib
import io

class EdgeDetection:
    def __init__(self, input_dir, output_dir,path_module):
        os.makedirs(output_dir, exist_ok=True)
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.module = YOLO(path_module,verbose=False)

    def process(self, crop = True, info = "Cropping images: "):
        index = 0
        for file in tqdm(os.listdir(self.input_dir), desc=info):
            _, ext = os.path.splitext(file)
            if ext.lower() not in ['.jpg', '.jpeg', '.png']:
                continue
            image_path = os.path.join(self.input_dir, file)
            output_path = os.path.join(self.output_dir, file)

            cropped_image = self.crop_largest_text_box(image_path, crop=crop)
            # for count, cropped_image in enumerate(cropped_images): 
            #     # Save each cropped image with a unique name
            #     index += 1
            #     output_path = os.path.join(self.output_dir, f"{name}{index}.jpg")
            #     cv2.imwrite(output_path, cropped_image)
            cv2.imwrite(output_path, cropped_image)

        print(f"Processed images saved at: {self.output_dir}")

    def crop_largest_text_box(self, image_path, _save_=False, crop = True) -> list:
        image = cv2.imread(image_path)
        max_area = 0
        if crop == False:
            return image
        
        largest_box = None

        results = self.module(image_path, save=_save_,verbose=False)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                area = (x2 - x1) * (y2 - y1)  # Tính diện tích box
                if area > max_area:
                    max_area = area
                    largest_box = (x1, y1, x2, y2)

        if largest_box:
            x1, y1, x2, y2 = largest_box
            cropped_image = image[y1:y2, x1:x2]
            return cropped_image
        else:
            return  image# Không có box nào được phát hiện

# if __name__ == "__main__":
#     input_dir = r"D:\learning\lab NLP\Tool_news\AutoLabel_script\data"
#     output_dir = r"D:\learning\lab NLP\Tool_news\AutoLabel_script\test"
#     edge_detection = EdgeDetection(input_dir, output_dir,path_module=r"D:\learning\lab NLP\Tool_news\AutoLabel_script\model\vi\best.pt")
#     edge_detection.process()
