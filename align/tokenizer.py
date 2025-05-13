import pandas as pd
import torch
import torch.nn as nn

class LoadModel:
    def __init__(self):
        with open("model/tokenization/syllable.txt", "r", encoding="utf-16") as f:
            self.words = f.readlines()
            self.words = [word.strip() for word in self.words]

    #===================end init===============================#
    
    def is_syllable(self, word):
        return word in self.words

    def find_syllabel(self, word: str) -> list:
        lst_syllabel = []
        for word_ in self.words:
            if word.find(word_) != -1:
                lst_syllabel.append(word_)
        return lst_syllabel


    # Chỉnh lại tên riêng cho đúng
    def correct_named_entities(self, word: str):
        """
        Chỉnh sửa các tên riêng trong văn bản.
        """
        if self.is_syllable(word) == False:
            lst_word = self.find_syllabel(word)
            i = 0
            token = ""
            while i < len(word):
                lst_need = [ word_ for word_ in lst_word if word_.find(word[i]) == 0]
                lst_need = [word_ for word_ in lst_need if word.find(word_) == i]
                lst_need = sorted(lst_need ,key = lambda x: len(x))
                lst_need.reverse()
                if len(lst_need) == 0:
                    token += word[i] +" "
                    i += 1
                elif len(lst_need) >= 1:
                    token += lst_need[0] + " "
                    i += len(lst_need[0])
                else:
                    raise "error!"
            word = token.strip()
        return word
                


# if __name__ == "__main__":
#     model = LoadModel()
#     lst = []
#     for key in dict_saint.keys():
#         text = model.correct_named_entities(key.lower())
#         lst.append(f"{key} -> {text}")
#     with open("test.txt", "w", encoding="utf-8") as f:
#         f.write("\n".join(lst))