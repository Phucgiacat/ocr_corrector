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

# def get_similar_characters(nom_char, similar_dict):
#     similar_chars = similar_dict.loc[similar_dict['Input Character'] == nom_char, 'Top 20 Similar Characters']
#     result_set = set()
    
#     if not similar_chars.empty:
#         result_set = set(ast.literal_eval(similar_chars.values[0]))
    
#     return result_set

# def get_possible_characters(qn_char, quoc_ngu_dict):
#     possible_chars = quoc_ngu_dict.loc[quoc_ngu_dict['QuocNgu'] == qn_char, 'SinoNom']
#     if not possible_chars.empty:
#         return set(possible_chars.values)
#     return set()

# def needleman_wunsch_with_lists_2(nom_list, quoc_ngu_list, possible_chars_nom, possible_chars_quoc_ngu_dict, match_score=1, gap_penalty=-1):
#     len_nom = len(nom_list)
#     len_quoc_ngu = len(quoc_ngu_list)
    
#     # Precompute possible characters for quoc_ngu_list
#     possible_chars_quoc_ngu = [possible_chars_quoc_ngu_dict[char] for char in quoc_ngu_list]
    
#     scores = [[0] * (len_quoc_ngu + 1) for _ in range(len_nom + 1)]
#     traceback = [[None] * (len_quoc_ngu + 1) for _ in range(len_nom + 1)]
    
#     for i in range(1, len_nom + 1):
#         scores[i][0] = i * gap_penalty
#         traceback[i][0] = 'U'
#     for j in range(1, len_quoc_ngu + 1):
#         scores[0][j] = j * gap_penalty
#         traceback[0][j] = 'L'
    
#     for i in range(1, len_nom + 1):
#         nom_char = nom_list[i - 1]
#         similar_chars_nom = possible_chars_nom[nom_char]
#         possible_nom_set = set(similar_chars_nom)
        
#         for j in range(1, len_quoc_ngu + 1):
#             qn_char = quoc_ngu_list[j - 1]
#             possible_chars_qn = possible_chars_quoc_ngu[j - 1]
            
#             if nom_char in possible_chars_qn or (possible_nom_set & possible_chars_qn):
#                 score_match = scores[i - 1][j - 1] + match_score
#             else:
#                 score_match = scores[i - 1][j - 1] - match_score
            
#             score_delete = scores[i - 1][j] + gap_penalty
#             score_insert = scores[i][j - 1] + gap_penalty
            
#             max_score = max(score_match, score_delete, score_insert)
#             scores[i][j] = max_score
            
#             if max_score == score_match:
#                 traceback[i][j] = 'D'
#             elif max_score == score_delete:
#                 traceback[i][j] = 'U'
#             else:
#                 traceback[i][j] = 'L'
    
#     # Early exit if no matches found
#     match_found = False
#     for nom_char in nom_list:
#         for qn_char in quoc_ngu_list:
#             possible_this_chars_qn = possible_chars_quoc_ngu_dict[qn_char]
#             if nom_char in possible_this_chars_qn or any(char in possible_chars_qn for char in possible_chars_nom[nom_char]):
#                 match_found = True
#                 break
#         if match_found:
#             break
    
#     if not match_found:
#         aligned_nom = nom_list + ['_'] * len(quoc_ngu_list)
#         aligned_quoc_ngu = ['_'] * len(nom_list) + quoc_ngu_list
#         return aligned_nom, aligned_quoc_ngu
    
#     aligned_nom = []
#     aligned_quoc_ngu = []
#     i, j = len_nom, len_quoc_ngu
    
#     while i > 0 or j > 0:
#         if i > 0 and j > 0 and traceback[i][j] == 'D':
#             aligned_nom.insert(0, nom_list[i - 1])
#             aligned_quoc_ngu.insert(0, quoc_ngu_list[j - 1])
#             i -= 1
#             j -= 1
#         elif i > 0 and (j == 0 or traceback[i][j] == 'U'):
#             aligned_nom.insert(0, nom_list[i - 1])
#             aligned_quoc_ngu.insert(0, '_')
#             i -= 1
#         elif j > 0 and (i == 0 or traceback[i][j] == 'L'):
#             aligned_nom.insert(0, '_')
#             aligned_quoc_ngu.insert(0, quoc_ngu_list[j - 1])
#             j -= 1
    
#     return aligned_nom, aligned_quoc_ngu

# def align_boxes_2(nom_data, quoc_ngu_list, SinoNom_similar_dict, QuocNgu_Sinonom_dict, k=2):
#     nom_list = nom_data['text']
#     aligned_results = []
#     begin_len = 0
#     possible_chars_quoc_ngu = {char: get_possible_characters(char, QuocNgu_Sinonom_dict) for char in quoc_ngu_list}
#     for idx, nom_string in enumerate(nom_list):
#         precomputed_similar_nom = {char:get_similar_characters(char, SinoNom_similar_dict) for char in nom_string}
#         result = find_best_alignment_box_2(
#             nom_string, quoc_ngu_list, 
#             precomputed_similar=precomputed_similar_nom, precomputed_QN=possible_chars_quoc_ngu, 
#             begin_len=begin_len, k=k
#         )
#         result+=(nom_data['bbox'][idx],)
#         aligned_results.append(result)
#         _, _, _, _, end_position, _ = result
#         if end_position is not None:
#             begin_len = end_position
#         else:
#             break
    
#     return aligned_results

# def find_best_alignment_box_2(nom_string, quoc_ngu_list, precomputed_similar, precomputed_QN, begin_len=0, k=2):
#     nom_length = len(nom_string)
#     quoc_ngu_length = len(quoc_ngu_list)
    
#     best_score = float('-inf')
#     best_quoc_ngu_substring = None
#     aligned_nom_string = None
#     aligned_quoc_ngu_string = None
#     end_position = None
    
#     # Define the range for start_idx
#     start_idx_range = range(begin_len, min(begin_len + k, quoc_ngu_length))
    
#     for start_idx in start_idx_range:
#         # Define the range for end_idx based on start_idx and k
#         end_idx_min = start_idx + nom_length - 1 - k
#         end_idx_max = start_idx + nom_length + k
#         end_idx_range = range(max(start_idx, end_idx_min), min(end_idx_max, quoc_ngu_length) + 1)
        
#         for end_idx in end_idx_range:
#             quoc_ngu_chars = quoc_ngu_list[start_idx:end_idx]
#             # Perform alignment
#             aligned_nom, aligned_quoc_ngu = needleman_wunsch_with_lists_2(
#                 list(nom_string), quoc_ngu_chars,
#                 precomputed_similar, possible_chars_quoc_ngu_dict=precomputed_QN
#             )
#             # Compute alignment score using NumPy
#             aligned_nom_array = np.array(aligned_nom)
#             aligned_quoc_ngu_array = np.array(aligned_quoc_ngu)
#             gaps = (aligned_nom_array == '_') | (aligned_quoc_ngu_array == '_')
#             alignment_score = np.sum(-1.5 * gaps + 1.0 * ~gaps)
#             # Update best alignment
#             if alignment_score > best_score:
#                 best_score = alignment_score
#                 best_quoc_ngu_substring = quoc_ngu_chars
#                 aligned_nom_string = ''.join(aligned_nom)
#                 aligned_quoc_ngu_string = ' '.join(aligned_quoc_ngu)
#                 end_position = end_idx
    
#     return best_quoc_ngu_substring, aligned_nom_string, aligned_quoc_ngu_string, best_score, end_position

import os
import pandas as pd
import numpy as np
from tqdm import tqdm

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
            aligned_qn.append("_")
            i -= 1
        elif j > 0 and backtrace[i][j] == 'L':
            aligned_nom.append("_")
            aligned_qn.append(qn_list[j - 1])
            j -= 1

    aligned_nom.reverse()
    aligned_qn.reverse()
    return [aligned_nom, aligned_qn]

def align(nom_dir, vi_dir, output_txt, k=2, name_book="book"):
    similar = pd.read_excel(os.environ['NOM_SIMILARITY_DICTIONARY'])
    trans = pd.read_excel(os.environ['QN2NOM_DICTIONARY']).iloc[:, [0, 1]]

    start_nom_index = 1
    list_file = sorted(os.listdir(nom_dir), key=lambda x: int(os.path.splitext(x)[0].split("_")[-1]))

    for file_name in tqdm(list_file, desc="Processing files", unit="file"):
        inx = int(os.path.splitext(file_name)[0].split("_")[-1])
        if inx < start_nom_index:
            continue

        try:
            nom_data = process_nom(os.path.join(nom_dir, file_name))
            quoc_ngu_list = process_quoc_ngu(os.path.join(vi_dir, file_name.replace("json", "txt")))
        except Exception as e:
            print(f"❌ Lỗi khi đọc file {file_name}: {e}")
            continue

        num_word_hn = [len(sentence) for sentence in nom_data['text']]
        flatten_nom = list("".join(nom_data['text']))
        aligned_hn, aligned_qn = levenshtein_align_boxes(flatten_nom, quoc_ngu_list, similar, trans)

        segments = []
        hn_remain, qn_remain = aligned_hn.copy(), aligned_qn.copy()

        for num in num_word_hn:
            count, i = 0, 0
            while i < len(hn_remain):
                if hn_remain[i] != "_":
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
            print(f"⚠️ File {file_name}: còn dư sau phân đoạn:\n  hn → {hn_remain}\n  qn → {qn_remain}")
            if segments:
                last_han, last_qn = segments[-1]
                segments[-1] = (last_han + hn_remain, last_qn + qn_remain)
            else:
                segments.append((hn_remain, qn_remain))

        with open(output_txt, "a", encoding="utf-8") as f:
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
