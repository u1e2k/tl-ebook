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
    if text:
        lines.append(text)

# Let's inspect where paragraph breaks occur in PDF OCR for Introduction:
# We know page 9 has:
# 1. "We come into the world without words. ... the air we breathe."
# 2. "We assume that the dominance of language forms ... more than half a century."
# 3. "The first step toward understanding ... until I was nearly thirty ... we perceive."
# 4. "Because the world I was born into ... in industry."
# 5. "It wasn’t exactly a eureka moment, ... Maria Kozhevnikov showed that there are object visualizers ... make them run."

# In the lines, let's see how they match:
print("Total lines:", len(lines))
for i, l in enumerate(lines):
    if "water we drink" in l or "half a century" in l or "think and we perceive" in l or "people in industry" in l or "make them run" in l:
        print(f"Match at line {i} (len={len(l)}): {l}")
