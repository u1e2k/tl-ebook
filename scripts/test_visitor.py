import pypdf

pdf_path = r'C:\Users\user\.gemini\antigravity\brain\4988f021-de17-4c56-b9e3-5b1310e4244d\.user_uploaded\media_1795009754855_e80e405f.pdf'
reader = pypdf.PdfReader(pdf_path)

parts = []
def visitor_body(text, cm, tm, font_dict, font_size):
    if text.strip():
        parts.append((tm[4], tm[5], text)) # x, y, text

reader.pages[8].extract_text(visitor_text=visitor_body)

# Sort by y descending, then x ascending
# Group by lines
lines_dict = {}
for x, y, t in parts:
    # round y to nearest 2 points
    ry = round(y / 2.0) * 2.0
    if ry not in lines_dict:
        lines_dict[ry] = []
    lines_dict[ry].append((x, t))

for y in sorted(lines_dict.keys(), reverse=True):
    line_parts = sorted(lines_dict[y], key=lambda item: item[0])
    first_x = line_parts[0][0]
    line_str = "".join([p[1] for p in line_parts])
    print(f'y={y:5.1f}, x0={first_x:5.1f} | {line_str}')
