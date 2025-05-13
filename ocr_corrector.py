from vi_ocr.vi_ocr import vi_ocr
from nom_ocr.resize import process_images_in_directory
from nom_ocr.nom_ocr import nom_ocr
from dotenv import load_dotenv
import argparse
import json
from handle_data import read_file_info, write_file_info, str2bool
from align.color import convert_txt_to_ecel, marking
from align.align import align
import pandas as pd
import os
load_dotenv('.env')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        'Sentence alignment using sentence embeddings',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--ocr', type=str2bool, nargs=2, metavar={'QN', 'HN'},
                    help='ocr vi nom')
    
    parser.add_argument('--align', type=int, required=False,
                    help='align vi nom')
    
    parser.add_argument('--corrector', type=str2bool, required=False,
                        help='correct')

    args = parser.parse_args()
    ocr_vi_nom = args.ocr if args.ocr else None
    algin = args.align if args.align else None
    correct = args.corrector

    if ocr_vi_nom:
        info = read_file_info()
        if ocr_vi_nom[0]: # <--- ocr quốc ngữ
            info['ocr_txt_qn'] = f"{os.environ['OUTPUT_FOLDER']}/ocr/Quoc Ngu ocr"
            vi_ocr(info['vi_dir'], info['ocr_txt_qn'])
        
        if ocr_vi_nom[1]: # <--- ocr hán nôm
            info['ocr_json_nom'] = f"{os.environ['OUTPUT_FOLDER']}/ocr/Han Nom ocr"
            info['ocr_image_nom'] = f"{os.environ['OUTPUT_FOLDER']}/ocr/image_bbox"
            output_resize_path = f"{os.environ['OUTPUT_FOLDER']}/image_processed/resized_images.txt"
            process_images_in_directory(info['nom_dir'], output_resize_path)
            nom_ocr(info['nom_dir'], info['ocr_json_nom'], info['ocr_image_nom'])    
        write_file_info(info)
    
    if algin:
        info = read_file_info()
        ocr_txt_qn = info.get('ocr_txt_qn')
        ocr_json_nom = info.get('ocr_json_nom')
        if (ocr_txt_qn is None) or (ocr_json_nom is None):
            raise ValueError("chưa ocr !!!")
        info['output_txt'] = f"{os.environ['OUTPUT_FOLDER']}/result.txt"
        align(ocr_json_nom, ocr_txt_qn, info['output_txt'], int(algin), name_book=info['file_name'])
        write_file_info(info)
    
    if correct is not None:
        info = read_file_info()
        info['Result'] = f"{os.environ['OUTPUT_FOLDER']}/result.xlsx"
        convert_txt_to_ecel(info['output_txt'], info['Result'], debug=correct, namebook=info['file_name'])
        df = pd.read_excel(info['Result'])
        marking(df, info['Result'], debug=correct,type_qn=int(os.environ['TYPE_QN']))
        write_file_info(info)
