import pandas as pd
import numpy as np
import ast
import os
from pathlib import Path
from .nom_process import process_nom
from .vi_process import process_quoc_ngu
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)

def build_dicts(similar_df, trans_df):
    trans_dict = {}
    for _, row in trans_df.iterrows():
        word, han_char = row[0], row[1]
        trans_dict.setdefault(word, []).append(han_char)

    similar_dict = {}
    for _, row in similar_df.iterrows():
        char, sim_char = row[0], row[1]
        similar_dict.setdefault(char, []).append(sim_char)

    return trans_dict, similar_dict

def is_compatible(han_nom_char, quoc_ngu_word, trans_dict, similar_dict):
    hn_candidates = trans_dict.get(quoc_ngu_word, [])
    similar_chars = similar_dict.get(han_nom_char, []) + [han_nom_char]
    return bool(set(hn_candidates) & set(similar_chars))

def levenshtein_align_boxes(nom_list, qn_list, similar_df, trans_df):
    trans_dict, similar_dict = build_dicts(similar_df, trans_df)
    m, n = len(nom_list), len(qn_list)
    dp = np.zeros((m + 1, n + 1), dtype=int)
    backtrace = np.full((m + 1, n + 1), '', dtype=object)

    for i in range(m + 1):
        dp[i][0] = i
        backtrace[i][0] = 'U'
    for j in range(n + 1):
        dp[0][j] = j
        backtrace[0][j] = 'L'
    backtrace[0][0] = ''

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = is_compatible(nom_list[i - 1], qn_list[j - 1], trans_dict, similar_dict)
            cost = 0 if match else 1
            options = [
                (dp[i - 1][j] + 1, 'U'),
                (dp[i][j - 1] + 1, 'L'),
                (dp[i - 1][j - 1] + cost, 'D')
            ]
            dp[i][j], backtrace[i][j] = min(options)

    aligned_nom, aligned_qn = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and backtrace[i][j] == 'D':
            aligned_nom.append(nom_list[i - 1])
            aligned_qn.append(qn_list[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and backtrace[i][j] == 'U':
            aligned_nom.append(nom_list[i - 1])
            aligned_qn.append("*")
            i -= 1
        elif j > 0 and backtrace[i][j] == 'L':
            aligned_nom.append("*")
            aligned_qn.append(qn_list[j - 1])
            j -= 1

    aligned_nom.reverse()
    aligned_qn.reverse()
    return [aligned_nom, aligned_qn]

def align(nom_dir, vi_dir, output_txt, k=2, name_book="book"):
    similar = pd.read_excel(os.environ['NOM_SIMILARITY_DICTIONARY'])
    trans = pd.read_excel(os.environ['QN2NOM_DICTIONARY']).iloc[:, [0, 1]]
    list_file = sorted(os.listdir(nom_dir), key=lambda x: int(os.path.splitext(x)[0].split(".")[-2]))

    # # Chạy với 1 file duy nhất
    # file = "D:\\learning\\lab NLP\\WeekOCR\\test\\new.txt"
    # if file:
    #     with open(file, "r", encoding="utf-8") as f:
    #         list_file = [line.strip() for line in f.readlines()]
    #     if not list_file:
    #         print("❌ Không có file nào trong danh sách.")
    #         return
    #     for idx, line in tqdm(enumerate(list_file)):
    #         split = line.split("\t")
    #         flatten_nom = list(split[0].strip())
    #         quoc_ngu_list = split[1].strip().split(" ")
    #         aligned_hn, aligned_qn = levenshtein_align_boxes(flatten_nom, quoc_ngu_list, similar, trans)
    #         with open(output_txt, "a", encoding="utf-8") as f:
    #             if len(aligned_hn) != len(aligned_qn):
    #                 print(f"⚠️ Warning: Mismatch độ dài align tại file {file}. Hán={len(aligned_hn)}, Việt={len(aligned_qn)}")
    #                 continue
    #             nom = ''.join(aligned_hn).strip()
    #             qn = ' '.join(aligned_qn).strip()

    #             if not nom and not qn:
    #                 continue
    #             f.write(f"{name_book}_{str(idx + 1).zfill(4)}.json\t[]\t{nom}\t{qn}\n")
    # return

    for file_name in tqdm(list_file, desc="Processing files", unit="file"):

        try:
            nom_data = process_nom(os.path.join(nom_dir, file_name), k)
            quoc_ngu_list = process_quoc_ngu(os.path.join(vi_dir, file_name.replace("json", "txt")))
        except Exception as e:
            print(f"❌ Lỗi khi đọc file {file_name}: {e}")
            continue

        segments = []

        # if k == 1:
        num_word_hn = [len(sentence) for sentence in nom_data['text']]
        flatten_nom = list("".join(nom_data['text']))
        aligned_hn, aligned_qn = levenshtein_align_boxes(flatten_nom, quoc_ngu_list, similar, trans)
        hn_remain, qn_remain = aligned_hn.copy(), aligned_qn.copy()
        for num in num_word_hn:
            count, i = 0, 0
            while i < len(hn_remain):
                if hn_remain[i] != "*":
                    count += 1
                i += 1
                if count == num:
                    break

            han_seg = hn_remain[:i]
            qn_seg = qn_remain[:i]
            segments.append((han_seg, qn_seg))
            hn_remain = hn_remain[i:]
            qn_remain = qn_remain[i:]

        if hn_remain or qn_remain:
            if segments:
                last_han, last_qn = segments[-1]
                segments[-1] = (last_han + hn_remain, last_qn + qn_remain)
            else:
                segments.append((hn_remain, qn_remain))
        # elif k == 4:
        #     for hn, qn in zip(nom_data['text'], quoc_ngu_list):
        #         aligned_hn, aligned_qn = levenshtein_align_boxes(hn, qn, similar, trans)
        #         segments.append((aligned_hn, aligned_qn))

        with open(output_txt, "a", encoding="utf-8") as f:
            if len(nom_data['bbox']) != len(segments):
                raise ValueError("Lỗi nặng")
            for bbox, (han_seg, qn_seg) in zip(nom_data['bbox'], segments):
                if len(han_seg) != len(qn_seg):
                    print(f"⚠️ Warning: Mismatch độ dài align tại file {file_name}. Hán={len(han_seg)}, Việt={len(qn_seg)}")
                    continue
                nom = ''.join(han_seg).strip()
                qn = ' '.join(qn_seg).strip()

                if not nom and not qn:
                    continue

                f.write(f"{file_name}\t{str(bbox)}\t{nom}\t{qn}\n")


# if __name__ == "__main__":
#     input_dir = r"D:\lab NLP\test\output\json\\"
#     vi_dir = r"D:\lab NLP\test\output\vi_gg"
#     output_txt = "data/result.txt"
#     k = 5
#     align(input_dir, vi_dir, output_txt,k)
