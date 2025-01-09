import os
import re
import pdfplumber
from pathlib import Path

def collect_pdfs(folder_path):
    """Collect all PDF files from the specified folder"""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Creating folder: {folder_path}")
        folder.mkdir(parents=True, exist_ok=True)
        return []
    
    pdf_files = list(folder.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files in {folder_path}")
    return pdf_files

def extract_legal_parties(pdf_path, page_number=0):
    """Extract legal parties information from PDF using specific keywords"""
    legal_terms = {
        'APELANTE': r'APELANTE:\s*(.+?)(?=\n|$)',
        'APELANTES': r'APELANTES:\s*(.+?)(?=\n|$)',
        'APELADO': r'APELADO:\s*(.+?)(?=\n|$)',
        'AGRAVANTE': r'AGRAVANTE:\s*(.+?)(?=\n|$)',
        'AGRAVADO': r'AGRAVADO:\s*(.+?)(?=\n|$)',
        'AGRAVADA': r'AGRAVADA:\s*(.+?)(?=\n|$)',
        'EMBARGANTE': r'EMBARGANTE:\s*(.+?)(?=\n|$)',
        'EMBARGADO': r'EMBARGADO:\s*(.+?)(?=\n|$)'
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_number < len(pdf.pages):
                page = pdf.pages[page_number]
                text = page.extract_text()
                
                results = {}
                for term, pattern in legal_terms.items():
                    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    results[term] = match.group(1).strip() if match else None
                return results
            
            print(f"Page {page_number} not found in {pdf_path}")
            return None
                
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return None

def main():
    folder_path = "./pdfs_folder"
    pdf_files = collect_pdfs(folder_path)
    
    if not pdf_files:
        print("No PDF files found!")
        return
    
    all_results = []
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        print("=" * 50)
        
        results = extract_legal_parties(pdf_file)
        if results:
            all_results.append({"file": pdf_file.name, "data": results})
            for term, value in results.items():
                if value:
                    print(f"{term}:")
                    print("-" * 30)
                    print(value)
                    print()
        print("=" * 50)
    
    print(f"\nProcessed {len(all_results)} files successfully")

if __name__ == "__main__":
    main()
