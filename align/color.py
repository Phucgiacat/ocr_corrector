import pandas as pd # type: ignore
from openpyxl import load_workbook #type: ignore
from xlsxwriter import Workbook # type: ignore
import os
from tqdm import tqdm # type: ignore
from .tokenizer import LoadModel
import re
import Levenshtein
import unicodedata

quocngu_dict = pd.read_excel(r'dict\QuocNgu_SinoNom_Dic.xlsx')
similar_dict = pd.read_excel(r'dict\SinoNom_Similar_Dic_v2.xlsx')
model = LoadModel()


def normalize_vietnamese_text(text):
    text = unicodedata.normalize('NFKC', text)
    
    gi_consonant_corrections = {
        "gía": "giá", "gìa": "già", "gỉa": "giả", "gĩa": "giã", "gịa": "giạ",
        "gíu": "giú", "gìu": "giù", "gỉu": "giủ", "gĩu": "giũ", "gịu": "giụ",
        
        "gío": "gió", "gìo": "giò", "gỉo": "giỏ", "gĩo": "giõ", "gịo": "giọ",
        "gíê": "giế", "gìê": "giề", "gỉê": "giể", "gĩê": "giễ", "gịê": "giệ",
    
        "gíơ": "giớ", "gìơ": "giờ", "gỉơ": "giở", "gĩơ": "giỡ", "gịơ": "giợ",
        
        "gíâ": "giấ", "gìâ": "giầ", "gỉâ": "giẩ", "gĩâ": "giẫ", "gịâ": "giậ",
        
        "gíô": "giố", "gìô": "giồ", "gỉô": "giổ", "gĩô": "giỗ", "gịô": "giộ",
        "gíă": "giắ", "gìă": "giằ", "gỉă": "giẳ", "gĩă": "giẵ", "gịă": "giặ",
        
        "gían": "gián", "gìan": "giàn", "gỉan": "giản", "gĩan": "giãn", "gịan": "giạn",
        "gíang": "giáng", "gìang": "giàng", "gỉang": "giảng", "gĩang": "giãng", "gịang": "giạng",
        "gíêng": "giếng", "gìêng": "giềng", "gỉêng": "giểng", "gĩêng": "giễng", "gịêng": "giệng",
        "gíêt": "giết", "gìêt": "giệt", "gỉêt": "giệt", "gĩêt": "giệt", "gịêt": "giệt",
        "gíêu": "giếu", "gìêu": "giều", "gỉêu": "giểu", "gĩêu": "giễu", "gịêu": "giệu",
        "gíong": "giống", "gìong": "giồng", "gỉong": "giổng", "gĩong": "giỗng", "gịong": "giộng",
        "gíông": "giống", "gìông": "giồng", "gỉông": "giổng", "gĩông": "giỗng", "gịông": "giộng",
        "gíai": "giái", "gìai": "giài", "gỉai": "giải", "gĩai": "giãi", "gịai": "giại",
        "gíam": "giám", "gìam": "giàm", "gỉam": "giảm", "gĩam": "giãm", "gịam": "giạm",
        "gíáp": "giáp",
        "gíóc": "giốc", "gịoc": "giộc",
        "gíuc": "giúc", "gịuc": "giục",
        "gíup": "giúp", "gịup": "giụp",
        "qủa": "quả", "qúa": "quá", "qũa": "quã", "qùa": "quà", "qụa": "quạ",
        "qủă": "quẳ", "qúă": "quắ", "qũă": "quẵ", "qùă": "quằ", "qụă": "quặ",
        "qủâ": "quẩ", "qúâ": "quấ", "qũâ": "quẫ", "qùâ": "quầ", "qụâ": "quậ",
        "qủe": "quẻ", "qúe": "qué", "qũe": "quẽ", "qùe": "què", "qụe": "quẹ",
        "qủê": "quể", "qúê": "quế", "qũê": "quễ", "qùê": "quề", "qụê": "quệ",
        "qủy": "quỷ", "qúy": "quý", "qũy": "quỹ", "qùy": "quỳ", "qụy": "quỵ",
    }
    
    o_vowel_pairs = {
        "òa": "oà", "óa": "oá", "ỏa": "oả", "õa": "oã", "ọa": "oạ",
        "òac": "oàc", "óac": "oác", "ỏac": "oảc", "õac": "oãc", "ọac": "oạc",
        "òach": "oàch", "óach": "oách", "ỏach": "oảch", "õach": "oãch", "ọach": "oạch",
        "òai": "oài", "óai": "oái", "ỏai": "oải", "õai": "oãi", "ọai": "oại",
        "òam": "oàm", "óam": "oám", "ỏam": "oảm", "õam": "oãm", "ọam": "oạm",
        "òan": "oàn", "óan": "oán", "ỏan": "oản", "õan": "oãn", "ọan": "oạn",
        "òang": "oàng", "óang": "oáng", "ỏang": "oảng", "õang": "oãng", "ọang": "oạng",
        "òanh": "oành", "óanh": "oánh", "ỏanh": "oảnh", "õanh": "oãnh", "ọanh": "oạnh",
        "òao": "oào", "óao": "oáo", "ỏao": "oảo", "õao": "oão", "ọao": "oạo",
        "òap": "oàp", "óap": "oáp", "ọap": "oạp",
        "òat": "oàt", "óat": "oát", "ọat": "oạt",
        "òay": "oày", "óay": "oáy", "ỏay": "oảy", "õay": "oãy", "ọay": "oạy",
        
        "òăc": "oằc", "óăc": "oắc", "ọăc": "oặc",
        "òăm": "oằm", "óăm": "oắm", "ỏăm": "oẳm", "õăm": "oẵm", "ọăm": "oặm",
        "òăn": "oằn", "óăn": "oắn", "ỏăn": "oẳn", "õăn": "oẵn", "ọăn": "oặn",
        "òăng": "oằng", "óăng": "oắng", "ỏăng": "oẳng", "õăng": "oẵng", "ọăng": "oặng",
        "òăp": "oằp", "óăp": "oắp", "ọăp": "oặp",
        "òăt": "oằt", "óăt": "oắt", "ọăt": "oặt",
        
        "òe": "oè", "óe": "oé", "ỏe": "oẻ", "õe": "oẽ", "ọe": "oẹ",
        "òen": "oèn", "óen": "oén", "ỏen": "oẻn", "õen": "oẽn", "ọen": "oẹn",
        "òeo": "oèo", "óeo": "oéo", "ỏeo": "oẻo", "õeo": "oẽo", "ọeo": "oẹo",
        "óep": "oép", "ọep": "oẹp",
        "óet": "oét", "ọet": "oẹt",
    }
    
    u_vowel_pairs = {
        "ùâ": "uầ", "úâ": "uấ", "ủâ": "uẩ", "ũâ": "uẫ", "ụâ": "uậ",
        "ùâc": "uầc", "úâc": "uấc", "ụâc": "uậc",
        "ùân": "uần", "úân": "uấn", "ủân": "uẩn", "ũân": "uẫn", "ụân": "uận",
        "ùâng": "uầng", "úâng": "uấng", "ủâng": "uẩng", "ũâng": "uẫng", "ụâng": "uậng",
        "ùât": "uầt", "úât": "uất", "ụât": "uật",
        "ùây": "uầy", "úây": "uấy", "ủây": "uẩy", "ũây": "uẫy", "ụây": "uậy",
        
        "ùê": "uề", "úê": "uế", "ủê": "uể", "ũê": "uễ", "ụê": "uệ",
        "ùêch": "uềch", "úêch": "uếch", "ụêch": "uệch",
        "ùên": "uền", "úên": "uến", "ủên": "uển", "ũên": "uễn", "ụên": "uện",
        "ùênh": "uềnh", "úênh": "uếnh", "ủênh": "uểnh", "ũênh": "uễnh", "ụênh": "uệnh",
        "ùêt": "uềt", "úêt": "uết", "ụêt": "uệt",
        "ùêu": "uều", "úêu": "uếu", "ủêu": "uểu", "ũêu": "uễu", "ụêu": "uệu",
        
        "ùy": "uỳ", "úy": "uý", "ủy": "uỷ", "ũy": "uỹ", "ụy": "uỵ",
        "ùych": "uỳch", "úych": "uých", "ụych": "uỵch",
        "ùyn": "uỳn", "úyn": "uýn", "ủyn": "uỷn", "ũyn": "uỹn", "ụyn": "uỵn",
        "ùynh": "uỳnh", "úynh": "uýnh", "ủynh": "uỷnh", "ũynh": "uỹnh", "ụynh": "uỵnh",
        "ùyp": "uỳp", "úyp": "uýp", "ụyp": "uỵp",
        "ùyt": "uỳt", "úyt": "uýt", "ụyt": "uỵt",
        "ùyu": "uỳu", "úyu": "uýu", "ủyu": "uỷu", "ũyu": "uỹu", "ụyu": "uỵu",
        
        "ùơ": "uờ", "úơ": "uớ", "ủơ": "uở", "ũơ": "uỡ", "ụơ": "uợ",
        "ùơi": "uời", "úơi": "uới", "ủơi": "uởi", "ũơi": "uỡi", "ụơi": "uợi",
        
        "ùô": "uồ", "úô": "uố", "ủô": "uổ", "ũô": "uỗ", "ụô": "uộ",
        "ùôc": "uồc", "úôc": "uốc", "ụôc": "uộc",
        "ùôi": "uồi", "úôi": "uối", "ủôi": "uổi", "ũôi": "uỗi", "ụôi": "uội",
        "ùôm": "uồm", "úôm": "uốm", "ủôm": "uổm", "ũôm": "uỗm", "ụôm": "uộm",
        "ùôn": "uồn", "úôn": "uốn", "ủôn": "uổn", "ũôn": "uỗn", "ụôn": "uộn",
        "ùông": "uồng", "úông": "uống", "ủông": "uổng", "ũông": "uỗng", "ụông": "uộng",
        "ùôt": "uồt", "úôt": "uốt", "ụôt": "uột",
    }
    
    i_vowel_pairs = {
        "ỳa": "ỳa", "ýa": "ýa", "ỷa": "ỷa", "ỹa": "ỹa", "ỵa": "ỵa",
        
        "ùya": "uỳa", "úya": "uýa", "ủya": "uỷa", "ũya": "uỹa", "ụya": "uỵa",
        
        "ìê": "iề", "íê": "iế", "ỉê": "iể", "ĩê": "iễ", "ịê": "iệ",
        "ỳê": "yề", "ýê": "yế", "ỷê": "yể", "ỹê": "yễ", "ỵê": "yệ",
        
        "ìêc": "iềc", "íêc": "iếc", "ịêc": "iệc",
        
        "ìêm": "iềm", "íêm": "iếm", "ỉêm": "iểm", "ĩêm": "iễm", "ịêm": "iệm",
        "ỳêm": "yềm", "ýêm": "yếm", "ỷêm": "yểm", "ỹêm": "yễm", "ỵêm": "yệm",
        
        "ìên": "iền", "íên": "iến", "ỉên": "iển", "ĩên": "iễn", "ịên": "iện",
        "ỳên": "yền", "ýên": "yến", "ỷên": "yển", "ỹên": "yễn", "ỵên": "yện",
        
        "ìêng": "iềng", "íêng": "iếng", "ỉêng": "iểng", "ĩêng": "iễng", "ịêng": "iệng",
        "ỳêng": "yềng", "ýêng": "yếng", "ỷêng": "yểng", "ỹêng": "yễng", "ỵêng": "yệng",
        
        "ìêp": "iềp", "íêp": "iếp", "ịêp": "iệp",
        
        "ìêt": "iềt", "íêt": "iết", "ịêt": "iệt",
        "ỳêt": "yềt", "ýêt": "yết", "ỵêt": "yệt",
        
        "ìêu": "iều", "íêu": "iếu", "ỉêu": "iểu", "ĩêu": "iễu", "ịêu": "iệu",
        "ỳêu": "yều", "ýêu": "yếu", "ỷêu": "yểu", "ỹêu": "yễu", "ỵêu": "yệu",
        
        "ùyên": "uyền", "úyên": "uyến", "ủyên": "uyển", "ũyên": "uyễn", "ụyên": "uyện",
        "ùyêt": "uyềt", "úyêt": "uyết", "ụyêt": "uyệt",
    }
    
    ư_vowel_pairs = {
        "ưà": "ừa", "ưá": "ứa", "ưả": "ửa", "ưã": "ữa", "ưạ": "ựa",
        
        "ưò": "ườ", "ưó": "ướ", "ưỏ": "ưở", "ưõ": "ưỡ", "ưọ": "ượ",
        
        "ưòc": "ườc", "ưóc": "ước", "ưọc": "ược",
        
        "ưòi": "ười", "ưói": "ưới", "ưỏi": "ưởi", "ưõi": "ưỡi", "ưọi": "ượi",
        "ừoi": "ười", "ứoi": "ưới", "ửoi": "ưởi", "ữoi": "ưỡi", "ựoi": "ượi",
        
        "ưòm": "ườm", "ưóm": "ướm", "ưỏm": "ưởm", "ưõm": "ưỡm", "ưọm": "ượm",
        
        "ưòn": "ườn", "ưón": "ướn", "ưỏn": "ưởn", "ưõn": "ưỡn", "ưọn": "ượn",
        
        "ưòng": "ường", "ưóng": "ướng", "ưỏng": "ưởng", "ưõng": "ưỡng", "ưọng": "ượng",
        
        "ưòp": "ườp", "ưóp": "ướp", "ưọp": "ượp", "ừơp": "ườp", "ứơp": "ướp", "ựơp": "ượp",
        
        "ưót": "ướt", "ưọt": "ượt", "ứơt": "ướt", "ựơt": "ượt",
        
        "ưòu": "ườu", "ưóu": "ướu", "ưỏu": "ưởu", "ưõu": "ưỡu", "ưọu": "ượu",
        "ừơu": "ườu", "ứơu": "ướu", "ửơu": "ưởu", "ữơu": "ưỡu", "ựơu": "ượu",
    }
    
    incorrect_diacritic_placement = {
        "uơì": "ười", "uơí": "ưới", "uơỉ": "ưởi", "uơĩ": "ưỡi", "uơị": "ượi",
        
        "iêù": "iều", "iêú": "iếu", "iêủ": "iểu", "iêũ": "iễu", "iêụ": "iệu",
        "yêù": "yều", "yêú": "yếu", "yêủ": "yểu", "yêũ": "yễu", "yêụ": "yệu",      
    }
    
    reversed_vowels = {
        # "ià": "ìa", "ía": "ía", "ỉa": "ỉa", "ĩa": "ĩa", "ịa": "ịa",
        "aì": "ài", "aí": "ái", "aỉ": "ải", "aĩ": "ãi", "aị": "ại",
        
        "aù": "àu", "aú": "áu", "aủ": "ảu", "aũ": "ãu", "aụ": "ạu",
        
        "aò": "ào", "aó": "áo", "aỏ": "ảo", "aõ": "ão", "aọ": "ạo",
        
        "âù": "ầu", "âú": "ấu", "âủ": "ẩu", "âũ": "ẫu", "âụ": "ậu",
        
        "eò": "èo", "eó": "éo", "eỏ": "ẻo", "eõ": "ẽo", "eọ": "ẹo",
        
        "êù": "ều", "êú": "ếu", "êủ": "ểu", "êũ": "ễu", "êụ": "ệu",
        
        "oì": "òi", "oí": "ói", "oỉ": "ỏi", "oĩ": "õi", "oị": "ọi",
        
        "ôì": "ồi", "ôí": "ối", "ôỉ": "ổi", "ôĩ": "ỗi", "ôị": "ội",
        
        "ơì": "ời", "ơí": "ới", "ơỉ": "ởi", "ơĩ": "ỡi", "ơị": "ợi",
        
        "uì": "ùi", "uí": "úi", "uỉ": "ủi", "uĩ": "ũi", "uị": "ụi",
        
        "ưì": "ừi", "ưí": "ứi", "ưỉ": "ửi", "ưĩ": "ữi", "ưị": "ựi",
        
        "oà": "oà", "oá": "oá", "oả": "oả", "oã": "oã", "oạ": "oạ",
        "òa": "oà", "óa": "oá", "ỏa": "oả", "õa": "oã", "ọa": "oạ",
        
        "oè": "oè", "oé": "oé", "oẻ": "oẻ", "oẽ": "oẽ", "oẹ": "oẹ",
        "òe": "oè", "óe": "oé", "ỏe": "oẻ", "õe": "oẽ", "ọe": "oẹ",
        
        "uề": "uề", "uế": "uế", "uể": "uể", "uễ": "uễ", "uệ": "uệ",
        "ùê": "uề", "úê": "uế", "ủê": "uể", "ũê": "uễ", "ụê": "uệ",
        
       
        # "uá": "úa", "uà": "ùa", "uả": "ủa", "uã": "ũa", "uạ": "ụa",
        
        "ưà": "ừa", "ưá": "ứa", "ưả": "ửa", "ưã": "ữa", "ưạ": "ựa",
        "ưa": "ưa", "ưá": "ứa", "ưà": "ừa", "ưả": "ửa", "ưã": "ữa", "ưạ": "ựa",
        "aò": "ào", "aó": "áo", "aỏ": "ảo", "aõ": "ão", "aọ": "ạo",
        "eò": "èo", "eó": "éo", "eỏ": "ẻo", "eõ": "ẽo", "eọ": "ẹo",
        
        
        "uừ": "ừu", "uứ": "ứu", "uử": "ửu", "uữ": "ữu", "uự": "ựu",   
        
        "aừ": "ừa", "aứ": "ứa", "aử": "ửa", "aữ": "ữa", "aự": "ựa",
    }
    
    html_entities = {
        "&#91;": "[", "&#93;": "]", "&quot;": "\"", "&apos;": "'",
        "&lt;": "<", "&gt;": ">", "&amp;": "&", "&nbsp;": " "
    }
    
    all_corrections = {
        **gi_consonant_corrections,
        **o_vowel_pairs,
        **u_vowel_pairs,
        **i_vowel_pairs,
        **ư_vowel_pairs,
        **incorrect_diacritic_placement,
        **reversed_vowels,
        **html_entities
    }
    
    for src, tgt in all_corrections.items():
        text = text.replace(src, tgt)
    
    text = re.sub(r'(?<!g)i(à|á|ả|ã|ạ)', r'ì\1', text)  
    text = re.sub(r'(?<!g)ìá', r'ía', text)  
    text = re.sub(r'(?<!g)ìà', r'ìa', text)  
    text = re.sub(r'(?<!g)ìả', r'ỉa', text)  
    text = re.sub(r'(?<!g)ìã', r'ĩa', text)  
    text = re.sub(r'(?<!g)ìạ', r'ịa', text)  
    text = re.sub(r'\bu(à|á|ả|ã|ạ)\b', r'ì\1', text)
    text = re.sub(r'(?<!q)ùá', r'úa', text)  
    text = re.sub(r'(?<!q)ùà', r'ùa', text)  
    text = re.sub(r'(?<!q)ùả', r'ủa', text)  
    text = re.sub(r'(?<!q)ùã', r'ũa', text)  
    text = re.sub(r'(?<!q)ùạ', r'ụa', text)
    
    return text

def char_to_unicode_hex(ch):
    return format(ord(ch), '04x')  # lấy mã hex, độ dài 4 chữ số

def similarity_by_unicode_hex(ch1, ch2):
    hex1 = char_to_unicode_hex(ch1)
    hex2 = char_to_unicode_hex(ch2)
    return Levenshtein.ratio(hex1, hex2)

def sort_by_unicode_similarity(target, candidates):
    scored = [(c, similarity_by_unicode_hex(target, c)) for c in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    scored = [char for char, _ in scored]  # giữ lại chỉ ký tự
    return scored  # giữ lại cả điểm để debug

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
    return sort_by_unicode_similarity(ocr, temp) if len(temp) > 0 else temp

def safe_write_rich_string(ws, row, col, fragments):
    if len(fragments) < 3:
        text = ''.join([t if isinstance(t, str) else '' for t in fragments])
        ws.write(row, col, text)
    else:
        ws.write_rich_string(row, col, *fragments)

def marking(df: pd.DataFrame, output_path: str, debug=False, type_qn=2):
    """
    column_qn = {0, 1, 2} nghĩa tương ứng: 
        0: không tô màu.
        1: tô màu từ có trong danh sách syllable.
        2: tô màu theo từ hán nôm.
    """

    list_quocngu = df['Chữ Quốc ngữ'].tolist()
    list_ocr = df['SinoNom OCR'].tolist()

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
        'E': 90,
        'F': 90
    }

    for col_letter, width in column_widths.items():
        worksheet.set_column(f'{col_letter}:{col_letter}', width)

    if debug:
        worksheet.write(0, 0, 'Image_name_path', header)
    else:
        worksheet.write(0, 0, 'Image_name', header)

    worksheet.write(0, 1, 'ID', header)
    worksheet.write(0, 2, 'Image Box', header)
    worksheet.write(0, 3, 'SinoNom OCR', header)
    worksheet.write(0, 4, 'SinoNom char', header)
    worksheet.write(0, 5, 'Chữ Quốc ngữ', header)

    sum_char = 0
    sum_char_red = 0
    sum_char_blue = 0

    print("Đang đánh dấu các từ trong file excel...")
    for row_num, (word, ocr) in enumerate(tqdm(zip(list_quocngu, list_ocr), desc="Marking: ", unit="row")):
        word = normalize_vietnamese_text(word)
        a = word.split()
        b = list(ocr)

        if len(a) != len(b):
            print(f"[⚠️ Warning] Dữ liệu không khớp tại dòng {row_num + 1}: {a} vs {b}")
            continue

        max_len = len(b)
        sum_char += max_len

        temp = []     # nội dung cột 'SinoNom OCR'
        _tem_1 = []   # type_qn == 1, tô syllable đúng
        _tem_2 = []   # type_qn == 2, tô chữ Quốc ngữ
        _tem_3 = []   # cột mới: SinoNom char tô theo Hán Nôm

        for i in range(len(a)):
            color = black if model.is_syllable(a[i]) else red
            _tem_1 += [color, a[i] + " "]

        for i in range(max_len):
            result = compare(a[i], b[i])

            if len(result) > 1:
                sum_char_blue += 1
                temp += [blue, result[0]]
                _tem_2 += [blue, a[i] + " "]
                _tem_3 += [red, b[i]]

            elif a[i] == '*' and b[i] != '*':
                sum_char_red += 1
                temp += [red, b[i]]
                _tem_2 += [red, a[i] + " "]
                _tem_3 += [red, b[i]]

            elif b[i] == '*' and a[i] != '*':
                sum_char_red += 1
                temp += [red, b[i]]
                _tem_2 += [red, a[i] + " "]
                _tem_3 += [red, b[i]]

            elif len(result) == 1:
                temp += [black, b[i]]
                _tem_2 += [black, a[i] + " "]
                _tem_3 += [black, b[i]]

            elif len(result) == 0:
                sum_char_red += 1
                temp += [red, b[i]]
                _tem_2 += [red, a[i] + " "]
                _tem_3 += [red, b[i]]

        # Write to Excel
        if debug:
            worksheet.write(row_num + 1, 0, df['Image_name_path'].iloc[row_num])
        else:
            worksheet.write(row_num + 1, 0, df['Image_name'].iloc[row_num])

        worksheet.write(row_num + 1, 1, df['ID'].iloc[row_num])
        worksheet.write(row_num + 1, 2, df['Image Box'].iloc[row_num])
        safe_write_rich_string(worksheet, row_num + 1, 3, temp)
        safe_write_rich_string(worksheet, row_num + 1, 4, _tem_3)

        if type_qn == 0:
            worksheet.write(row_num + 1, 5, df['Chữ Quốc ngữ'].iloc[row_num])
        elif type_qn == 1:
            safe_write_rich_string(worksheet, row_num + 1, 5, _tem_1)
        elif type_qn == 2:
            safe_write_rich_string(worksheet, row_num + 1, 5, _tem_2)

    print(f"Số Đỏ: {sum_char_red}/{sum_char} chữ => lỗi: {(sum_char_red/sum_char)*100:.2f}%")
    print(f"Số Xanh: {sum_char_blue}/{sum_char} chữ => lỗi {(sum_char_blue/sum_char)*100:.2f}%")
    workbook.close()

# if __name__ == "__main__":
#     txt_path = 'data/result.txt'
#     excel_path = 'data/result.xlsx'
#     output = 'data/result.xlsx'

#     convert_txt_to_ecel(txt_path, excel_path , debug=True)
#     df =  pd.read_excel(excel_path)
#     marking(df, output_path=output, debug=False)
