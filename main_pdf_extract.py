import os
import PyPDF2
import re

def extract_patterns_from_pdf(file_path, page_index, patterns):
    """  """
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        if page_index >= len(reader.pages):
            print(f"Page {page_index} not found in {file_path}. Skipping...")
            return {key: None for key in patterns}
        
        page = reader.pages[page_index]  
        text = page.extract_text()
        
        results = {}
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                results[pattern_name] = match.group(1).strip()
            else:
                results[pattern_name] = None
        return results


patterns = {
    #POLO ATIVO
    "APELANTE": r'APELANTE:\s*(.+)',
    "APELANTES": r'APELANTES:\s*(.+)',
    #POLO PASSIVO
    "APELADO": r'APELADO:\s*(.+)',

    #POLO ATIVO
    "AGRAVANTE": r'AGRAVANTE:\s*(.+)',
    #POLO PASSIVO
    "AGRAVADO": r'AGRAVADO:\s*(.+)',
    "AGRAVADA": r'AGRAVADA:\s*(.+)',

    #POLO ATIVO
    "EMBARGANTE": r'EMBARGANTE:\s*(.+)',
    #POLO PASSIVO
    "EMBARGADO": r'EMBARGADO:\s*(.+)',
    
    "R$": r'R\$\s*([\d\.,]+)',
}


folder_path = "./pdfs_folder"  


pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".pdf")]

page_index = 1 

all_results = []
for pdf_file in pdf_files:
    results = extract_patterns_from_pdf(pdf_file, page_index, patterns)
    results["File"] = pdf_file
    all_results.append(results)


for result in all_results:
    print(f"Results for {result['File']}:")
    for key, value in result.items():
        if key != "File":
            if value:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: None")
    print()
