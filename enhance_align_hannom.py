import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path
import numpy as np
load_dotenv(".env")

similar = pd.read_excel(os.environ['NOM_SIMILARITY_DICTIONARY'])
trans = pd.read_excel(os.environ['QN2NOM_DICTIONARY']).iloc[:, [0,1]]


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
    # Tiền xử lý: tạo dict để truy xuất nhanh hơn
    trans_dict, similar_dict = build_dicts(similar_df, trans_df)

    m, n = len(nom_list), len(qn_list)
    dp = np.zeros((m + 1, n + 1), dtype=int)
    backtrace = np.full((m + 1, n + 1), '', dtype=object)

    # Khởi tạo hàng và cột đầu tiên
    for i in range(m + 1):
        dp[i][0] = i
        backtrace[i][0] = 'U'
    for j in range(n + 1):
        dp[0][j] = j
        backtrace[0][j] = 'L'
    backtrace[0][0] = ''  # góc trên cùng

    # Tính chi phí từng ô
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = is_compatible(nom_list[i - 1], qn_list[j - 1], trans_dict, similar_dict)
            cost = 0 if match else 1
            options = [
                (dp[i - 1][j] + 1, 'U'),          # delete
                (dp[i][j - 1] + 1, 'L'),          # insert
                (dp[i - 1][j - 1] + cost, 'D')    # substitute / match
            ]
            dp[i][j], backtrace[i][j] = min(options)

    # Truy vết để tạo danh sách align
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
            aligned_qn.append("_")
            i -= 1
        elif j > 0 and backtrace[i][j] == 'L':
            aligned_nom.append("_")
            aligned_qn.append(qn_list[j - 1])
            j -= 1

    aligned_nom.reverse()
    aligned_qn.reverse()

    return aligned_nom, aligned_qn
