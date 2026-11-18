import pypdf
import re

pdf_path = r'C:\Users\user\.gemini\antigravity\brain\4988f021-de17-4c56-b9e3-5b1310e4244d\.user_uploaded\media_1795009754855_e80e405f.pdf'
reader = pypdf.PdfReader(pdf_path)

intro_text = ""
for p in range(8, 15): # pages 9 to 15
    intro_text += reader.pages[p].extract_text() + "\n"

# Clean up hyphenation at line breaks: e.g. "seventeenth-\ncentury" -> "seventeenth-century"
# If hyphen at end of line:
intro_clean = re.sub(r'(\w+)-\n(\w+)', r'\1\2', intro_text)

# Also let's inspect the paragraphs in the prompt's OCR text for Introduction!
# We know each paragraph in Introduction from page 9 to 15:
# Page 9:
# P1: We come into the world without words... language is the water we drink, the air we breathe.
# P2: We assume that the dominance of language... for more than half a century.
# P3: The first step toward understanding... (continues to page 10)
# Page 10:
# ...how we think and we perceive.
# P4: Because the world I was born into... disability advocates, and people in industry.
# P5: It wasn’t exactly a eureka moment... (continues to page 11)
# Page 11:
# ...the spatial visualizers make them run.
# P6: This book also grows out of two major revelations... more than one hundred shipping containers.
# Page 12:
# P7: I stood on an overhead catwalk... are now gone.
# P8: My second eureka moment arrived later that year... “We don’t make it anymore!”
# P9: What I quickly came to realize... crisis in American ingenuity.
# Page 13:
# P10: We are losing essential technical skills, for three main reasons... stop screening out the very people who could save us.
# P11: Most people don’t fully comprehend the way their mind works... where are today’s clever engineers?
# Page 14:
# P12: From there we’ll look at the brilliant collaborations... changed the course of history.
# P13: Then we’ll turn to the sometimes life-and-death... could make all the difference.
# P14: Last, I’ll return to a subject I’ve written about extensively... what can they teach us about the ways we think?
# P15: How can you tell if you’re a visual thinker?... assess their workforce and to (continues to page 15)
# Page 15:
# ...harnessing the power of every kind of mind.

print("Target Introduction Paragraphs: exactly 15 paragraphs!")
