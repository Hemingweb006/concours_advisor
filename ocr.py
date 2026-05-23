import os
from pdf2image import convert_from_path
import pytesseract

def ocr_pdf_to_txt(pdf_path):
    """
    Takes a PDF file, performs OCR page by page, and saves the text
    in a .txt file with the exact same name as the PDF.
    """
    dir_name = os.path.dirname(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    txt_filename = f"{base_name}.txt"
    txt_path = os.path.join(dir_name, txt_filename)
    
    print(f"Processing: '{pdf_path}'...")
    
    try:
        print("  Converting PDF pages to images...")
        pages = convert_from_path(pdf_path, dpi=300)
        
        extracted_text = ""
        
        for i, page in enumerate(pages):
            print(f"  Scanning page {i + 1} of {len(pages)}...")
            
            text = pytesseract.image_to_string(page, lang='fra')
            
            extracted_text += f"--- Page {i + 1} ---\n{text}\n\n"
            
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
            
        print(f"Success! Saved as: '{txt_path}'\n")
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}\n")


folder = "concours"

for sub_folder in os.listdir(folder):

    folder_to_scan = f"concours/{sub_folder}"
    if os.path.isdir(folder_to_scan):
        for filename in os.listdir(folder_to_scan):
            if filename.lower().endswith(".pdf"):
                full_pdf_path = os.path.join(folder_to_scan, filename)
                ocr_pdf_to_txt(full_pdf_path)
    else:
        continue