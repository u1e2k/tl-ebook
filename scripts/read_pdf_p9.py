import pypdf

pdf_path = r'C:\Users\user\.gemini\antigravity\brain\4988f021-de17-4c56-b9e3-5b1310e4244d\.user_uploaded\media_1795009754855_e80e405f.pdf'
reader = pypdf.PdfReader(pdf_path)

page9 = reader.pages[8].extract_text()
print("=== Page 9 raw text ===")
print(page9)
