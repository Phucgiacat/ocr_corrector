from setuptools import setup, find_packages

setup(
    name='nom_vi_ocr_toolkit',
    version='1.0.0',
    description='A Vietnamese-Han Nom OCR processing toolkit',
    author='Bùi Hồng Phúc',
    author_email='duyphuc2425@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'cython',
        'jupyter',
        'fairseq',
        'numpy',
        'pandas',
        'opencv-python',
        'torch',
        'torchvision',
        'matplotlib',
        'lxml',
        'pyyaml',
        'ultralytics',
        'pdfplumber',
        'pdf2image',
        'flask',
        'langdetect',
        'laserembeddings',
        'sentencepiece',
        'transliterate'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
