# nom_ocr_corrector

nom_ocr_corrector is a multimodal sentence alignment tool for Sino-Nôm (NS) - Vietnamese (QN) parallel corpora. It uses [LASER](https://github.com/facebookresearch/LASER) embeddings and VecAlign to find sentence pairs that are similar in meaning 
and an alignment algorithm based on Levenshtein's algorithm to find the optimal alignment. 

## Building the environment

If you haven't already check out the repository:
```bash
https://github.com/davidle2810/nom_ocr_corrector.git
cd nom_ocr_corrector
```

The environment can be built using the provided environment.yml file:
```bash
conda env create -f environment.yml
conda activate ocr_corrector
python -m laserembeddings download-models
```

## Setup `.env` file
```
NOM_SIMILARITY_DICTIONARY = dict\SinoNom_similar_Dic_v2.xlsx
QN2NOM_DICTIONARY = dict\QuocNgu_SinoNom_Dic.xlsx

SN_DOMAIN = tools.clc.hcmus.edu.vn

OUTPUT_FOLDER = Output
GOOGLE_APPLICATION_CREDENTIALS = 
LOG_DIR = vi_ocr/logs
SYLLABLE = model\tokenization\syllable.txt

NAME_FILE_INFO = before_handle_data.json

NUM_CROP_QN = 1
NUM_CROP_HN = 1

VI_MODEL = model\vi\best.pt
NOM_MODEL = model\nom\best_v2.pt

TYPE_QN = 2 
```
Trong đó:
-`NUM_CROP_QN`: splits one page into n sub-pages because a single page may contain multiple Quốc Ngữ sections.
- `NUM_CROP_HN`:  similar to above, but for Hán Nôm.
- `TYPE_QN`:has three options — 0, 1, or 2, corresponding to:
    - `0`: no coloring.
    - `1`: highlight tokens not found in the syllable list,
    - `2`: color according to corresponding Hán Nôm characters.
## Run nom_ocr_corrector
### Using provided data
In your terminal, type
```
python handle_data.py --input "data/truyen_cac_thanh.pdf"
```
Then, remove unnecessary images. If needed, crop to extract the relevant content by running the following command (this step can be skipped):\
In this command, two arguments are passed to determine which type of image to crop:
- The first argument is for cropping Quốc Ngữ (modern Vietnamese script). This part is usually clean, so you can set it to false.
- The second argument is for cropping Hán Nôm (classical script).
```
python handle_data.py --crop false true
```
Next, index the images so that corresponding Quốc Ngữ and Hán Nôm content can be aligned (this step is mandatory):\
Pass one argument as either true or false, meaning whether to index in reverse order or not.
```
python handle_data.py --align_number_reverse true
```
Next, perform OCR:\
There are two arguments: one for Quốc Ngữ, and one for Hán Nôm:
```
python ocr_corrector.py --ocr true true
```
Then, perform sentence alignment:
Pass a single argument k which helps find the best matching lines (recommended: k=5).
```
python ocr_corrector.py --align 5
```
Finally, apply correction and color marking:\
It is recommended to run the code as below.
```
python ocr_corrector.py --corrector false
```
***Note: Going through each step carefully will lead to better results.***


