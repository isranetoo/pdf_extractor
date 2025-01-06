import PyPDF2
import re

def extract_patterns_from_pdf(file_path, page_index, patterns):
    """
    Extracts specific patterns from a PDF file.

    Args:
        file_path (str): Path to the PDF file.
        page_index (int): Index of the page to extract text from.
        patterns (dict): A dictionary of patterns to search for.

    Returns:
        dict: A dictionary with pattern names as keys and extracted values as values.
    """
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

# Define the patterns to extract
patterns = {
    "APELANTE": r'APELANTE:\s*(.+)',
    "APELADO": r'APELADO:\s*(.+)',
    "AGRAVANTE": r'AGRAVANTE:\s*(.+)',
    "AGRAVADO": r'AGRAVADO:\s*(.+)',
    "AGRAVADA": r'AGRAVADA:\s*(.+)',
    "EMBARGANTE": r'EMBARGANTE:\s*(.+)',
    "EMBARGADO": r'EMBARGADO:\s*(.+)',
    "R$": r'R\$\s*([\d\.,]+)',
}

# List of PDF files to process
pdf_files = [
    "processo_18746960.pdf",
    "processo_18746961.pdf",
    "processo_18746962.pdf",
    "processo_18746963.pdf",
    "processo_18746965.pdf",
    "processo_18746966.pdf",
    "processo_18746967.pdf",
    "processo_18746968.pdf",
    "processo_18746969.pdf",
    "processo_18746970.pdf",
    "processo_18746961.pdf",
    "processo_18746962.pdf",
]


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
           
    print()
