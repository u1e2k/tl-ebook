import zipfile
import re

epub_path = r'C:/Users/user/.gemini/antigravity/brain/4988f021-de17-4c56-b9e3-5b1310e4244d/.user_uploaded/media_1795009754773_65e55a77.epub'
with zipfile.ZipFile(epub_path, 'r') as z:
    html = z.read('index_split_000.html').decode('utf-8')
    p9 = html.find('<a id="p9"></a>')
    print(html[p9:p9+2500])
