import json


# def read_json(file_name):
#     with open(file=file_name, mode='r', encoding='utf-8') as file:
#         data = json.load(file)

#     return data['data']['result_bbox']

def print_box(data):
    for box in data:
        point = box[0]
        text = box[1][0]
        conf = box[1][1]
        print(f"{text} - {conf} - {point}")

def remove_edge_box(bboxes, edge_count=4, x_thresh=10, short_len=4):
    """
    Loại bỏ các bounding box có khả năng nhiễu nằm ở viền ngoài ảnh.

    Điều kiện bị loại bỏ:
        - Nằm trong top/bottom `edge_count` box (theo x)
        - Có chiều dài text ≤ short_len
        - Hoặc là ký tự đơn
        - Và/hoặc nằm quá gần lề trái (x < x_thresh)

    Args:
        bboxes (list): Danh sách các box có "points" và "transcription".
        edge_count (int): Số lượng box ngoài cùng để kiểm tra.
        x_thresh (int): Ngưỡng x bên trái để coi là "sát lề".
        short_len (int): Độ dài text được coi là ngắn/rác.

    Returns:
        list: Các box đã được lọc bỏ nhiễu.
    """
    if not bboxes:
        return []

    sorted_boxes = sorted(bboxes, key=lambda x: x["points"][0][0], reverse=True)
    edge_boxes = sorted_boxes[:edge_count] + sorted_boxes[-edge_count:]

    invalid_ids = set(id(box) for box in edge_boxes if (
        len(box.get("transcription", "")) <= short_len or
        len(box.get("transcription", "")) == 1 or
        box["points"][0][0] < x_thresh
    ))

    # Trả lại các box hợp lệ
    return [box for box in bboxes if id(box) not in invalid_ids]




def to_cols(bbox, k):
    if k == 4:
        return  sorted(bbox, key=lambda x: x["points"][0][1])
    
    bbox = sorted(bbox, key=lambda x: x["points"][0][0], reverse=True)
    cols = []
    for box in bbox:
        if len(cols) == 0:
            cols.append([box])
            continue
        last_box = cols[-1][-1]
        if abs(last_box["points"][0][0] - box["points"][0][0]) < 10:
            cols[-1].append(box)
        else:
            cols.append([box])

    for i, col in enumerate(cols):
        cols[i] = sorted(col, key=lambda x: x["points"][0][1])

    return cols


def read_json(file_name):
    # with open(file=file_name, mode='r', encoding='utf-8') as file:
    #     data = json.load(file)

    # return data['data']['details']['details']
    with open(file_name, mode='r', encoding='utf-8') as file:
        data = file.read()
    return {
        "text": [data],
        "bbox": [[0, 0, 0, 0]]
    }

def process_nom(file_path, k):
    data = read_json(file_path)

    bbox_data = data  # dùng phiên bản đã chỉnh
    # cols = to_cols(bbox_data, k)

    # nom_dict = {
    #     "text": [],
    #     "bbox": []
    # }
    # if k == 4:
    #     for box in cols:
    #         nom_dict['text'].append(box["transcription"])
    #         nom_dict['bbox'].append(box["points"]) 
    # elif k == 1:
    #     for col in cols:
    #         for box in col:
    #             nom_dict['text'].append(box["transcription"])
    #             nom_dict['bbox'].append(box["points"])

    # return nom_dict
    return  data
