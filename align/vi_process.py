import re
import os
from dotenv import load_dotenv
load_dotenv('.env')
# syllable_file_path = os.environ['SYLLABLE']
syllable_file_path = os.environ['SYLLABLE']

with open(syllable_file_path, encoding='utf-16') as f:
    morpho_syllable = f.read().splitlines() 

def number_to_text(n: str):
    ones = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    tens = ["lẻ", "mười", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
    hundreds = ["", "một trăm", "hai trăm", "ba trăm", "bốn trăm", "năm trăm", "sáu trăm", "bảy trăm", "tám trăm", "chín trăm"]
    if n == "0":
        return "không"
    result = []
    if n >= 1000000:
        result.append(number_to_text(n//1000000)+' triệu')
        n %= 1000000
    # Process thousands
    if n>=1000:
        result.append(number_to_text(n // 1000)+' nghìn')
        n %= 1000
    # Process hundreds
    if n >= 100:
        result.append(hundreds[n // 100])
        n %= 100
    # Process tens
    if n >= 10:
        result.append(tens[n // 10])
        n %= 10
    else:
        if len(result)>=1:
            result.append('lẻ')
    # Process ones
    if n > 0:
        if n==1:
            if (len(result)>=1) and ('mươi' in result[-1]):
                result.append('mốt')
            else:
                result.append('một')
        elif n==5:
            if (len(result)>=1) and (result[-1]!='lẻ'):
                result.append('lăm')
            else:
                result.append('năm')
        else:
            result.append(ones[n])
    if len(result)>1 and result[-1]=='lẻ':
        return ' '.join(result[:-1]).strip()
    else:
        return ' '.join(result).strip()

# Regex to find numbers in the text
def split_words(word):
    if word == '':
        return ''
    list_chars=list(word)
    words = ''
    for i in range(len(list_chars)):
        if ''.join(list_chars[:i+1]) in morpho_syllable:
            words = ''.join(list_chars[:i+1]) + ' '
            new_list_chars = list_chars[i+1:]
            words += split_words(''.join(new_list_chars))
            if len(word)==len(''.join(words.strip().split())):
                return words
    if len(list_chars)> 0 and ''.join(list_chars) not in morpho_syllable:
        return ''

def clean_text(text):
    """ 
    Removing non-latin chars
    But keeping numbers and punctuations as default
    """
    text = re.sub(r'-\s*\d+\s*-', '', text)  # Remove "- digits -"
    text = re.sub(r'\(\s*\d+\s*\)', '', text)  # Remove "( digits )"
    # text = re.sub(r"\(.*?\)", '', text) # Remove "( content )"
    text = re.sub(r'[^a-zA-Z0-9\u00C0-\u1EF9\s\n]+', ' ', text)
     # Replace multiple consecutive spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    def replace_number(match):
        num = int(match.group(0))  # Get the number from the match
        return number_to_text(num)  # Convert number to Vietnamese words
    
    # Replace all numbers in the text with their Vietnamese words
    text = re.sub(r'\d+', replace_number, text.lower())
    text = re.sub(r'\s+', ' ', text).strip()
    new_line = ''
    for word in text.split():
        if (word in morpho_syllable) or (word.isdigit()) or len(word)==1:
            new_line += word + ' '
        else:
            candidate = split_words(word)
            if candidate:
                new_line+= candidate + ' '
            else:
                new_line += word + ' '
    return re.sub(r'\s+', ' ', new_line).strip()

def process_quoc_ngu(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
        text_clearn = clean_text(text)
        data = text_clearn.split()        
    return data