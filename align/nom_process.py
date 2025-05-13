import json


def read_json(file_name):
    with open(file=file_name, mode='r', encoding='utf-8') as file:
        data = json.load(file)

    return data['data']['result_bbox']

def print_box(data):
    for box in data:
        point = box[0]
        text = box[1][0]
        conf = box[1][1]
        print(f"{text} - {conf} - {point}")

def remove_edge_box(bbox):
    bbox = sorted(bbox, key=lambda x: x[0][0][0], reverse=True)
    check_box = bbox[:4] + bbox[-4:]
    invalid_box = []
    for box in check_box:
        text = box[1][0]
        conf = box[1][1]
        point = box[0]
        if len(text) <= 4 and point[0][0] < 30:
            invalid_box.append(box)
            continue
        if len(text) <= 4 and conf < 0.7:
            invalid_box.append(box)
            continue
    
        if len(text) == 1 and conf < 0.98:
            invalid_box.append(box)
            continue
    for box in invalid_box:
        if box in bbox:
            bbox.remove(box)

    return bbox


def to_cols(bbox):
    bbox = sorted(bbox, key=lambda x: x[0][0][0], reverse=True)
    cols = []
    for box in bbox:
        if len(cols) == 0:
            cols.append([box])
            continue
        last_box = cols[-1][-1]
        if last_box[0][0][0] - box[0][0][0] < 10:
            cols[-1].append(box)
        else:
            cols.append([box])
    # sort each column
    for i, col in enumerate(cols):
        cols[i] = sorted(col, key=lambda x: x[0][0][1])

    cols_dict = {}
    for i, col in enumerate(cols):
        cols_dict[f"columns {i+1}"] = col
    
    return cols

def read_json(file_name):
    with open(file=file_name, mode='r', encoding='utf-8') as file:
        data = json.load(file)

    return data['data']['result_bbox']

def process_nom(file_path):
    data = read_json(file_path)
    bbox_data = remove_edge_box(data)
    cols = to_cols(bbox_data)

    nom_dict = {
        "text": [],
        "bbox": []
    }

    for col in cols:
        for box in col:
            nom_dict['text'].append(box[1][0])
            nom_dict['bbox'].append(box[0])

    return nom_dict