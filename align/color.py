import pandas as pd # type: ignore
from openpyxl import load_workbook #type: ignore
from xlsxwriter import Workbook # type: ignore
import os
from tqdm import tqdm # type: ignore
from .tokenizer import LoadModel
import re

quocngu_dict = pd.read_excel(r'dict\QuocNgu_SinoNom_Dic.xlsx')
similar_dict = pd.read_excel(r'dict\SinoNom_Similar_Dic_v2.xlsx')
model = LoadModel()

def convert_txt_to_ecel(file_path: str, output_path: str , debug=False,namebook='book'):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    data = []
    last_name = ""
    count_box = 0
    count_page = 0
    print("Đang chuyển đổi file txt sang file excel...")
    for line in tqdm(lines, desc="Converting", unit="line"):
        file_name , bbox,  nom , vi = line.split("\t")
        pattern = r'_\d+_\.json'
        file_name = re.sub(pattern,'.json',file_name)
        if file_name != last_name:
            last_name = file_name
            count_box = 1
            count_page += 1
        page = "{:03d}".format(count_page)
        page_path = os.path.splitext(os.path.basename(file_name))[0].split("_")[1]
        if debug:
            file_name_path = f"{namebook}_page{page_path}.jpg"
        file_name = f"{namebook}_{page_path}_{page}.jpg"

        id_name = f"{namebook}." + page_path + "." + "{:03d}".format(count_box)
        
        count_box += 1

        if debug:
            data.append({
                "Image_name_path": file_name_path,
                "Image_name": file_name,
                "ID": id_name,
                "Image Box": bbox,
                "SinoNom OCR": nom,
                "Chữ Quốc ngữ": vi
            })
        else:
            data.append({
                    "Image_name": file_name,
                    "ID": id_name,
                    "Image Box": bbox,
                    "SinoNom OCR": nom,
                    "Chữ Quốc ngữ": vi
                })


    df = pd.DataFrame(data)
    output_file = output_path
    df.to_excel(output_file, index=False)

    print(f"File Excel đã được tạo tại: {output_file}")


def compare(quoc_ngu: str, ocr: str):
    quoc_ngu = quoc_ngu.strip().lower()
    ocr = ocr.strip()
    result_word = list(quocngu_dict[quocngu_dict['QuocNgu'] == quoc_ngu]['SinoNom'])
    result_OCR = list(similar_dict[similar_dict['Input Character'] == ocr]['Top 20 Similar Characters'])

    if len(result_OCR) == 1:
        result_OCR = [ocr] + list(result_OCR[0])
    else:
        result_OCR = [ocr]
    if ocr in  result_word:
        return [ocr]
    temp = list(set(result_word) & set(result_OCR))
    return temp

def marking(df: pd.DataFrame, output_path: str , debug=False, type_qn = 2):
    """
    column_qn = {0, 1, 2} nghĩa tương ứng: 
        0: không tô màu.
        1: tô màu từ có trong danh sách syllable.
        2: tô màu theo từ hán nôm.
    """

    list_quocngu = df['Chữ Quốc ngữ'].tolist()
    list_ocr = list(df['SinoNom OCR'])

    workbook = Workbook(output_path)
    worksheet = workbook.add_worksheet()

    red = workbook.add_format({'font_color': 'red'})   
    blue = workbook.add_format({'font_color': 'blue'})
    black = workbook.add_format({'font_color': 'black'})
    header = workbook.add_format({'bold': True, 'align': 'center'})

    column_widths = {
        'A': 18, 
        'B': 18,  
        'C': 50,
        'D': 90,
        'E': 90
    }

    for col_letter, width in column_widths.items():
        worksheet.set_column(f'{col_letter}:{col_letter}', width)

    if debug:
        worksheet.write(0, 0, *['Image_name_path', header])
    worksheet.write(0, 0, *['Image_name', header])          
    worksheet.write(0, 1, *['ID', header])            
    worksheet.write(0, 2, *['Image Box', header])  
    worksheet.write(0, 3, *['SinoNom OCR', header])
    worksheet.write(0, 4, *['Chữ Quốc ngữ', header])

    print("Đang đánh dấu các từ trong file excel...")
    for row_num, (word, ocr) in enumerate(tqdm(zip(list_quocngu, list_ocr), desc="Marking: ", unit="row")): #enumerate(tqdm(zip(list_quocngu, list_ocr)):
        a = word.split()
        b = list(ocr)
        # distance, b_new, a_new = edit_distance(a, b)
        max_len = len(b)
        temp = []
        _tem_1 = []
        _tem_2 = []
        for i in range(len(a)):
            color = black if model.is_syllable(a[i]) else red
            _tem_1 += [color, a[i] + " "]

        for i in range(max_len):
            # print(a[i], b[i], compare(a[i], b[i]), sep='\n', end='\n\n')

            if len(compare(a[i], b[i])) >1:
                temp+=(blue, b[i])
                _tem_2 += (blue, a[i]+ " ")

            elif a[i] == '*' and b[i] != '*':
                temp+=(red, b[i])
                _tem_2 += (red, a[i]+" ")

            elif b[i] == '*' and a[i] != '*':
                temp+=(red, b[i])
                _tem_2+=(red, a[i]+" ")

            elif len(compare(a[i], b[i])) == 1:
                temp+=(black, b[i])
                _tem_2 += (black, a[i] + " ")
            elif len(compare(a[i], b[i])) == 0:
                temp+=(red, b[i])
                _tem_2+=(red, a[i]+" ")
        if debug:
            worksheet.write(row_num + 1, 0, df['Image_name_path'].iloc[row_num])
        worksheet.write(row_num + 1, 0, df['Image_name'].iloc[row_num])
        worksheet.write(row_num + 1, 1, df['ID'].iloc[row_num])
        worksheet.write(row_num + 1, 2, df['Image Box'].iloc[row_num])
        worksheet.write_rich_string(row_num + 1, 3, *temp)
        if type_qn == 0:
            worksheet.write(row_num + 1, 4, df['Chữ Quốc ngữ'].iloc[row_num])
        elif type_qn == 1:
            worksheet.write_rich_string(row_num + 1, 4, *_tem_1)
        elif type_qn == 2:
            worksheet.write_rich_string(row_num + 1, 4, *_tem_2)
    workbook.close()


# if __name__ == "__main__":
#     txt_path = 'data/result.txt'
#     excel_path = 'data/result.xlsx'
#     output = 'data/result.xlsx'

#     convert_txt_to_ecel(txt_path, excel_path , debug=True)
#     df =  pd.read_excel(excel_path)
#     marking(df, output_path=output, debug=False)
