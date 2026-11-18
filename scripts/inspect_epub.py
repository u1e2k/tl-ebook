import zipfile
import re

epub_path = r'C:/Users/user/.gemini/antigravity/brain/4988f021-de17-4c56-b9e3-5b1310e4244d/.user_uploaded/media_1795009754773_65e55a77.epub'

with zipfile.ZipFile(epub_path, 'r') as z:
    html = z.read('index_split_000.html').decode('utf-8')
    p9 = html.find('<a id="p9"></a>')
    p17 = html.find('<a id="p17"></a>')
    intro_html = html[p9:p17]
    print(f'Introduction len: {len(intro_html)}')
    # strip tags for raw text inspection
    clean_intro = re.sub(r'<[^>]+>', '\n', intro_html)
    clean_intro = '\n'.join([line.strip() for line in clean_intro.splitlines() if line.strip()])
    print('First 1000 chars:')
    print(clean_intro[:1000])
