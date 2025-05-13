import shutil
import os



def split_nom_vi(src_dir, nom_dir, vi_dir, index, default= False): #option = {"start_vi": 491, "asc_vi":False ,"start_nom": 251, "asc_nom": True}
    image_paths = os.listdir(src_dir)
    if image_paths is None:
        print("don't file images !!")
        return None
    os.makedirs(nom_dir, exist_ok=True)
    os.makedirs(vi_dir, exist_ok=True)

    for image_path in image_paths:
        src = os.path.join(src_dir,image_path)
        idx = int(os.path.basename(image_path).split(".")[0].split("_")[-1])
        output = image_path.split("_")[0]
        if idx >= index:
            if default:
                output = nom_dir
            # else:
            #     currency_idx = option['start_nom']
            #     if option['asc_nom']:
            #         option['start_nom'] += 1
            #     else:
            #         option['start_nom'] -= 1
            #     output = os.path.join(nom_dir,f"{output}_{str(currency_idx).zfill(3)}.jpg")
        else:
            if default:
                output = vi_dir
            # else:
            #     currency_idx = option['start_vi']
            #     if option['asc_vi']:
            #         option['start_vi'] += 1
            #     else:
            #         option['start_vi'] -= 1
            #     output = os.path.join(vi_dir,f"{output}_{str(currency_idx).zfill(3)}.jpg")
        shutil.move(src,output) 

if __name__ == "__main__":
    src_dir = "data/pages"
    vi_dir = "data/vi/crawl"
    nom_dir = "data/nom/crawl"
    split_nom_vi(src_dir, nom_dir, vi_dir, 244)