import pypdf
import json

pdf_path = r'C:\Users\user\.gemini\antigravity\brain\4988f021-de17-4c56-b9e3-5b1310e4244d\.user_uploaded\media_1795009754855_e80e405f.pdf'
reader = pypdf.PdfReader(pdf_path)

def extract_page_lines(page):
    parts = []
    def visitor(text, cm, tm, font_dict, font_size):
        if text.strip():
            parts.append((tm[4], tm[5], text))
    
    page.extract_text(visitor_text=visitor)
    if not parts:
        return []
    
    # Sort lines by y descending (top to bottom of page)
    # y coordinate in PDF: larger y is higher on the page!
    sorted_parts = sorted(parts, key=lambda p: -p[1])
    
    lines = []
    current_y = None
    current_line = []
    for p in sorted_parts:
        x, y, text = p
        if current_y is None or abs(y - current_y) <= 3:
            current_y = y
            current_line.append(p)
        else:
            current_line.sort(key=lambda item: item[0])
            lines.append((current_line[0][0], current_line[0][1], "".join([item[2] for item in current_line])))
            current_y = y
            current_line = [p]
    if current_line:
        current_line.sort(key=lambda item: item[0])
        lines.append((current_line[0][0], current_line[0][1], "".join([item[2] for item in current_line])))
    
    return lines

intro_pages = range(8, 15) # pages 9 to 15
all_lines = []
for p_idx in intro_pages:
    lines = extract_page_lines(reader.pages[p_idx])
    for l in lines:
        all_lines.append((p_idx + 1, l[0], l[1], l[2]))

paragraphs = []
cur_p = ""

for page_no, x0, y, text in all_lines:
    t = text.strip()
    if not t:
        continue
    if t == "Introduction":
        continue
    
    # Indent detection:
    # If x0 > 10, it's a new paragraph
    if x0 > 10.0:
        if cur_p:
            paragraphs.append(cur_p.strip())
        cur_p = t
    else:
        # continuation line
        if cur_p:
            if cur_p.endswith("-"):
                # check if hyphen is word break or hyphenated word
                # if followed by lowercase, it's likely a word break
                cur_p = cur_p[:-1] + t
            else:
                cur_p += " " + t
        else:
            cur_p = t

if cur_p:
    paragraphs.append(cur_p.strip())

print(f"Total reconstructed paragraphs in Introduction: {len(paragraphs)}")
for i, p in enumerate(paragraphs):
    print(f"\n[{i+1}] {p}")

with open("src_en/00_introduction_paragraphs.json", "w", encoding="utf-8") as f:
    json.dump(paragraphs, f, ensure_ascii=False, indent=2)
