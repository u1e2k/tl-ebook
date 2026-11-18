import zipfile
import re
import json
import os

epub_path = r'C:/Users/user/.gemini/antigravity/brain/4988f021-de17-4c56-b9e3-5b1310e4244d/.user_uploaded/media_1795009754773_65e55a77.epub'
out_dir = r'c:\Users\user\repos\tl-ebook\src_en'
os.makedirs(out_dir, exist_ok=True)

sections = [
    {"id": "00_introduction", "title": "Introduction", "start_page": 9, "end_page": 16},
    {"id": "01_chapter1", "title": "Chapter 1: What Is Visual Thinking?", "start_page": 17, "end_page": 52},
    {"id": "02_chapter2", "title": "Chapter 2: Screened Out", "start_page": 53, "end_page": 85},
    {"id": "03_chapter3", "title": "Chapter 3: Where Are All the Clever Engineers?", "start_page": 86, "end_page": 118},
    {"id": "04_chapter4", "title": "Chapter 4: Complementary Minds", "start_page": 119, "end_page": 149},
    {"id": "05_chapter5", "title": "Chapter 5: Genius and Neurodiversity", "start_page": 150, "end_page": 183},
    {"id": "06_chapter6", "title": "Chapter 6: Visualizing Risk to Prevent Disasters", "start_page": 184, "end_page": 223},
    {"id": "07_chapter7", "title": "Chapter 7: Animal Consciousness and Visual Thinking", "start_page": 224, "end_page": 258},
    {"id": "08_afterword", "title": "Afterword", "start_page": 259, "end_page": 262},
    {"id": "09_acknowledgments", "title": "Acknowledgments", "start_page": 263, "end_page": 263},
    {"id": "10_about_the_author", "title": "About the Author", "start_page": 377, "end_page": 377},
]

# Read all html files concatenated in order
with zipfile.ZipFile(epub_path, 'r') as z:
    all_html = ""
    for i in range(8):
        fn = f'index_split_{i:03d}.html'
        if fn in z.namelist():
            all_html += z.read(fn).decode('utf-8', errors='ignore')

for sec in sections:
    s_tag = f'<a id="p{sec["start_page"]}">'
    e_page = sec["end_page"] + 1
    e_tag = f'<a id="p{e_page}">'
    
    s_pos = all_html.find(s_tag)
    e_pos = all_html.find(e_tag)
    
    if s_pos != -1:
        chunk = all_html[s_pos:e_pos] if e_pos != -1 else all_html[s_pos:]
        
        # Parse paragraphs
        paras = re.findall(r'<p[^>]*>(.*?)</p>', chunk, re.DOTALL | re.IGNORECASE)
        clean_paras = []
        for p in paras:
            # check if paragraph is just an anchor or image
            text = re.sub(r'<[^>]+>', ' ', p)
            text = ' '.join(text.split())
            if text:
                clean_paras.append(text)
        
        out_file = os.path.join(out_dir, f'{sec["id"]}.json')
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump({
                "id": sec["id"],
                "title": sec["title"],
                "paragraphs": clean_paras
            }, f, ensure_ascii=False, indent=2)
        print(f'Extracted {sec["id"]}: {len(clean_paras)} paragraphs')
    else:
        print(f'Warning: start tag {s_tag} not found')
