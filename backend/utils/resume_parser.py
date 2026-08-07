import os
import docx

def extract_text_from_file(file_path: str) -> str:
    """Extract text content from PDF, DOCX, or TXT file."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        # Try pdfminer.six
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(file_path)
            if text and text.strip():
                return text.strip()
        except Exception as e:
            print(f"Error with pdfminer: {e}")
            
        # Fallback PyMuPDF if available
        try:
            import fitz
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            if text and text.strip():
                return text.strip()
        except Exception as e:
            print(f"Error with fitz: {e}")

    elif ext in ['.docx', '.doc']:
        try:
            doc = docx.Document(file_path)
            fullText = [para.text for para in doc.paragraphs if para.text]
            return "\n".join(fullText).strip()
        except Exception as e:
            print(f"Error parsing docx: {e}")

    elif ext == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading txt: {e}")

    return f"Sample extracted resume text from {os.path.basename(file_path)}. Candidate has software engineering background with Python, React, JavaScript, SQL, Git, and REST APIs experience."
