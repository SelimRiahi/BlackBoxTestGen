import PyPDF2

pdf_path = 'CahierGlovo.pdf'
output_path = 'docs/requirements.txt'

with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text() + '\n'

# Simple extraction: look for lines with 'requirement', 'exigence', or similar
import re
requirements = []
for line in text.split('\n'):
    if re.search(r'(requirement|exigence|fonctionnelle|doit|must|should)', line, re.IGNORECASE):
        requirements.append(line.strip())

with open(output_path, 'w', encoding='utf-8') as out:
    for req in requirements:
        out.write(req + '\n')

print(f"Extracted {len(requirements)} possible requirements to {output_path}")
