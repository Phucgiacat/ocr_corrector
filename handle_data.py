import os
import cv2
from tqdm import tqdm
import shutil
from dotenv import load_dotenv
from Proccess_pdf.extract_page import ExtractPages
import argparse
from Proccess_pdf.edge_detection import EdgeDetection
import json
import re
from tqdm import tqdm
load_dotenv('.env')


def crop_image_func(image_path: str, num_crop: int) -> dict:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    height, width, _ = image.shape

    if num_crop <= 1:
        os.remove(image_path)
        return {1: image}

    crop_image = {}
    step = width // num_crop
    start = 0

    for i in range(1, num_crop + 1):
        end = width if i == num_crop else start + step
        crop_image[i] = image[:, start:end]
        start += step

    os.remove(image_path)
    return crop_image

def crop_folder(dir_input, info="processing: ", num_crop=1):
    os.makedirs(dir_input, exist_ok=True)
    images = [f for f in os.listdir(dir_input) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    index = 0
    for image in tqdm(images, desc=info):
        image_path = os.path.join(dir_input, image)
        crop_image = crop_image_func(image_path, num_crop)
        filename, ext = os.path.splitext(image)
        for key in sorted(crop_image.keys()):
            index += 1
            output_file = os.path.join(dir_input, f"{filename}_{str(index).zfill(3)}{ext}")
            cv2.imwrite(output_file, crop_image[key])

def replace_number_in_filename(filename: str, number: int, type = " ") -> str:
    """
    Nếu cropped=True: thay thế số cũ (định dạng _xxx.) bằng số mới.
    Nếu cropped=False: thêm _xxx vào ngay trước phần đuôi file.
    """
    padding = f"{number:03d}"

    pattern = r'_(\d+)\.'
    new_filename = re.sub(pattern, f'_{type}_{padding}.', filename)

    return new_filename

def process_file(file_path):
    if os.path.exists(os.environ['OUTPUT_FOLDER']):
        shutil.rmtree(os.environ['OUTPUT_FOLDER'])
    save_info = "before_handle_data.json"
    file_name = os.path.basename(file_path)
    file_name = os.path.splitext(file_name)[0]
    info = {"file_name": file_name}
    
    if os.path.exists(save_info):
        os.remove(save_info)

    os.makedirs(os.environ['OUTPUT_FOLDER'], exist_ok=True)
    extractor = ExtractPages(file_path, os.environ['OUTPUT_FOLDER'])
    extractor.extract(logs=False, return_dict= False)

    vi_dir = f"{os.environ['OUTPUT_FOLDER']}/image/Quoc Ngu"
    nom_dir = f"{os.environ['OUTPUT_FOLDER']}/image/Han Nom"
    info['vi_dir'] = vi_dir
    info['nom_dir'] = nom_dir

    try:
        num_nom = int(os.environ['NUM_CROP_HN'])
        num_qn  = int(os.environ['NUM_CROP_QN'])
        print(f"Số ảnh crop nom: {num_nom}")
        print(f"Số ảnh crop qn: {num_qn}")
        crop_folder(vi_dir, info="processing Quoc Ngu: ", num_crop=num_nom)
        crop_folder(nom_dir, info= "proccessing Nom: ", num_crop=num_qn)
    except Exception as error:
        raise error
    
    with open(save_info, "w", encoding="utf-8") as file:
        json.dump(info, file, ensure_ascii=False, indent=4)
    print("Success !!!")

def str2bool(v: str):
    if v.isdigit():
        return int(v)
    return v.lower() in ('true', '1', 'yes', 'y')

def read_file_info() -> json:
    with open(os.environ['NAME_FILE_INFO'], "r", encoding="utf-8") as file:
        info = json.load(file)
    return info

def write_file_info(info: json):
    with open(os.environ['NAME_FILE_INFO'], "w", encoding="utf-8") as file:
        json.dump(info, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        'Sentence alignment using sentence embeddings',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('--input', type=str, required=False,
                        help='path_to_input_document')
    
    parser.add_argument('--file_id', type=str, required=False,
                        help='file_id')
    
    parser.add_argument("--check_num_pages", type=str, required=False,
                        help="check num pages")

    parser.add_argument("--crop", type=str2bool, nargs=2, metavar=('quocngu', 'hannom'),
                        help="Truyền 2 giá trị crop (true/false)")
    
    parser.add_argument("--align_number_reverse", type=str2bool, required=False
                        , help="Đánh số để align")

    args = parser.parse_args()

    input_file = args.input if args.input else None
    file_id = args.file_id if args.file_id else None
    crop = args.crop if args.crop else None
    align_number_reverse = args.align_number_reverse
    check_num = args.check_num_pages if args.check_num_pages else None
    if file_id and input_file:
        new_path = os.path.join(os.path.dirname(input_file), file_id + os.path.splitext(input_file)[1])
        os.rename(input_file, new_path)
        input_file = new_path
    
    if input_file:
        process_file(input_file)
        print('Results are saved to', os.path.splitext(os.path.basename(input_file))[0])

    if check_num:
        info = read_file_info()
        num_pages_vi = len(os.listdir(info['vi_dir']))
        num_pages_nom = len(os.listdir(info['nom_dir']))
        print(f"Số trang quốc ngữ: {num_pages_vi}")
        print(f"Số trang Hán Nôm: {num_pages_nom}")
    
    if crop:
        if os.path.exists("before_handle_data.json") == False:
            raise "Chưa Extract File"
        
        info = read_file_info()
        output_vi_dir = f"{os.environ['OUTPUT_FOLDER']}/image_processed/Quoc Ngu"
        output_nom_dir = f"{os.environ['OUTPUT_FOLDER']}/image_processed/Han Nom"

        edge_detection = EdgeDetection(info["vi_dir"], output_vi_dir,path_module=os.environ['VI_MODEL'])
        edge_detection.process(crop=crop[0],info="Cropping Quoc Ngu: ")

        edge_detection = EdgeDetection(info["nom_dir"], output_nom_dir,path_module=os.environ['NOM_MODEL'])
        edge_detection.process(crop=crop[1], info="Cropping Nom: ")

        info["vi_dir"] = output_vi_dir
        info["nom_dir"] = output_nom_dir

        write_file_info(info)
        print("cropped !!!")
    
    if align_number_reverse is not None:
        try:
            have_reverse = align_number_reverse
            info = read_file_info()

            list_image_vi = os.listdir(info['vi_dir'])
            list_image_nom = os.listdir(info['nom_dir'])
            
            if len(list_image_vi) == 0 or len(list_image_nom) == 0 or len(list_image_nom) > len(list_image_vi):
                raise ValueError("No images found in the specified directories.")

            list_image_vi = sorted(list_image_vi, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            list_image_nom = sorted(list_image_nom, key=lambda x: int(x.split('.')[0].split('_')[-1]))

            if have_reverse:
                list_image_nom.reverse()

            for i in tqdm(range(len(list_image_nom)), desc="rename to algin: "):
                output_path_vi = os.path.join(info['vi_dir'], list_image_vi[i])
                output_path_nom = os.path.join(info['nom_dir'], list_image_nom[i])
                new_name_vi = replace_number_in_filename(output_path_vi, i+1,type = "vi")
                new_name_nom = replace_number_in_filename(output_path_nom, i+1,type = "nom")
                os.rename(output_path_vi, new_name_vi)
                os.rename(output_path_nom, new_name_nom)     

            list_image_vi = os.listdir(info['vi_dir'])
            list_image_nom = os.listdir(info['nom_dir'])
            list_image_vi = sorted(list_image_vi, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            list_image_nom = sorted(list_image_nom, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            # Đánh số theo chữ quốc ngữ
            for i in tqdm(range(len(list_image_nom)), desc="Đánh lại số: "):
                output_path_vi = os.path.join(info['vi_dir'], list_image_vi[i]) 
                output_path_nom = os.path.join(info['nom_dir'], list_image_nom[i])
                name_image = list_image_vi[i].replace("_vi_", "_")
                new_name_vi = os.path.join(info['vi_dir'], name_image) #<- đổi tại đây để đánh số.
                new_name_nom = os.path.join(info['nom_dir'], name_image) #<- Đổi tại đây để đánh số.
                os.rename(output_path_nom, new_name_nom)  
                os.rename(output_path_vi, new_name_vi)
                
        except Exception as e:
            raise e
    
    