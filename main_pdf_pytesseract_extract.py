import os
import re
from pdf2image import convert_from_path
from PIL import Image, ImageFilter
import pytesseract

def save_pdf_cuts_as_images(pdf_path, page_index, cuts, output_folder):
    try:
        poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"  
        pages = convert_from_path(
            pdf_path, 
            first_page=page_index + 1, 
            last_page=page_index + 1,
            poppler_path=poppler_path
        )
        
        if not pages:
            print(f"Page {page_index} not found in {pdf_path}. Skipping...")
            return

        page = pages[0]
        for i, cut in enumerate(cuts):
            cropped_image = page.crop(cut)
            output_path = os.path.join(output_folder, f"{os.path.basename(pdf_path).replace('.pdf', '')}_cut_{i}.png")
            cropped_image.save(output_path)
            print(f"Saved cut {i} to {output_path}")
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")

def format_judicial_number(text):
    """Format judicial numbers like: 1234567-12.2023.8.26.0000"""
    text = re.sub(r'\s+', '', text)
    pattern = r'(\d{7})-?(\d{2}).?(\d{4}).?(\d).?(\d{2}).?(\d{4})'
    match = re.search(pattern, text)
    if match:
        return f"{match.group(1)}-{match.group(2)}.{match.group(3)}.{match.group(4)}.{match.group(5)}.{match.group(6)}"
    return text

def format_process_number(text):
    """Format process numbers like: Nº 1026047-48.2024.8.26.0100"""
    text = ' '.join(text.split())
    
    patterns = [
        r'(?:Nº|N°|No|Nº)\s*(\d{6,7})-?(\d{2})\.?(\d{4})\.?(\d)\.?(\d{2})\.?(\d{4})',
        r'(\d{6,7})-?(\d{2})\.?(\d{4})\.?(\d)\.?(\d{2})\.?(\d{4})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 6:
                formatted = f"{groups[0]}-{groups[1]}.{groups[2]}.{groups[3]}.{groups[4]}.{groups[5]}"
                if not re.search(r'(?:Nº|N°|No|Nº)', text, re.IGNORECASE):
                    return f"Nº {formatted}"
                return f"Nº {formatted}"
    return text

def format_currency(text):
    """Format currency values like: R$ 1.234,56"""
    text = text.strip()
    if 'R$' in text or re.search(r'\d+[.,]\d{2}', text):
        number = re.findall(r'[\d.,]+', text)
        if number:
            try:
                value = number[0].replace('.', '').replace(',', '.')
                amount = float(value)
                return f"R$ {amount:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
            except ValueError:
                return text
    return text

def normalize_text(text):
    """Normalize special characters and maintain original format"""
    replacements = {
        'º': 'º',
        '°': 'º',
        '¢': 'º',
        '®': 'º',
        'ª': 'ª',
        '§': '§',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def extract_text_from_images(img_path, lista_cortes_imagem):
    resultados = {}
    for i, coordenadas in enumerate(lista_cortes_imagem):
        image = Image.open(img_path)
        cropped_imagem = image.crop(coordenadas)
        
        enhanced_image = cropped_imagem.convert('L')
        enhanced_image = enhanced_image.filter(ImageFilter.SHARPEN)
        enhanced_image = enhanced_image.filter(ImageFilter.EDGE_ENHANCE)
        enhanced_image = enhanced_image.point(lambda x: 0 if x < 128 else 255, '1')

        custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,()-:/$°ºªN§ '
        
        text_result = pytesseract.image_to_string(
            enhanced_image,
            config=custom_config,
            lang='por'
        ).strip()
        

        text_result = normalize_text(text_result)
        
        if re.search(r'(?:Nº|N°|No|Nº)?\s*\d{6,7}-?\d{2}', text_result, re.IGNORECASE):
            text_result = format_process_number(text_result)
        elif 'R$' in text_result or re.search(r'\d+[.,]\d{2}', text_result):
            text_result = format_currency(text_result)
        
        formatted_result = '\n'.join(
            line.strip() for line in text_result.splitlines()
            if line.strip()
        )

        resultados[f"processo_{i}"] = formatted_result

    return resultados

folder_path = "./pdfs_folder"  
output_folder = "./output_images"

pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".pdf")]

page_index = 1 
cuts = [
    (0, 250, 1550, 724),
    (0, 250, 1650, 864),
    (0, 250, 1650, 630),  #left, top, right, bottom
    (0, 250, 1650, 724),
]

if os.name == "nt":
    tesseract_path = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    if not os.path.exists(tesseract_path):
        raise FileNotFoundError(f"Tesseract executable not found at {tesseract_path}")

for pdf_file in pdf_files:
    save_pdf_cuts_as_images(pdf_file, page_index, cuts, output_folder)
    
    for i in range(len(cuts)):
        img_path = os.path.join(output_folder, f"{os.path.basename(pdf_file).replace('.pdf', '')}_cut_{i}.png")
        if os.path.exists(img_path):
            text_results = extract_text_from_images(img_path, cuts)
            print(f"\nResults for {img_path}:")
            print("=" * 50)
            for key, value in text_results.items():
                if value:
                    print(f"\n{key}:")
                    print("-" * 30)
                    print(value)
            print("=" * 50)
