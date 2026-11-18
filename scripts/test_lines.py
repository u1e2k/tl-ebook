import zipfile
import re

epub_path = r'C:/Users/user/.gemini/antigravity/brain/4988f021-de17-4c56-b9e3-5b1310e4244d/.user_uploaded/media_1795009754773_65e55a77.epub'
with zipfile.ZipFile(epub_path, 'r') as z:
    html = z.read('index_split_000.html').decode('utf-8')
    p9 = html.find('<a id="p9"></a>')
    p17 = html.find('<a id="p17"></a>')
    chunk = html[p9:p17]
    paras = re.findall(r'<p[^>]*>(.*?)</p>', chunk, re.DOTALL | re.IGNORECASE)
    
    lines = []
    for p in paras:
        text = re.sub(r'<[^>]+>', ' ', p)
        text = ' '.join(text.split())
        if text and text != 'Introduction':
            lines.append(text)
            
    print(f'Total lines in Intro: {len(lines)}')
    for i, line in enumerate(lines[:30]):
        print(f'{i:2d} (len={len(line):2d}): {line}')
