import os
import hashlib
import docx
import ollama
import pdfplumber
import time
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
            tables = page.extract_tables()
            for table in tables:
                table_text = "\n".join(["\t".join(cell if cell is not None else "" for cell in row) for row in table if row])
                all_text.append(table_text)
    return "\n\n".join(all_text)

def chunk_text(text, max_size=800):
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 2 <= max_size:
            current += p + "\n\n"
        else:
            chunks.append(current.strip())
            current = p + "\n\n"
    if current:
        chunks.append(current.strip())
    print(f"Chunks count after resizing: {len(chunks)}")
    return chunks

def get_cache_filename(text_chunk):
    chunk_hash = hashlib.md5(text_chunk.encode('utf-8')).hexdigest()
    return f"cache_{chunk_hash}.txt"

def save_to_cache(text_chunk, response):
    filename = get_cache_filename(text_chunk)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(response)

def load_from_cache(text_chunk):
    filename = get_cache_filename(text_chunk)
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def traiter_chunk_avec_cache(text_chunk):
    cached = load_from_cache(text_chunk)
    if cached is not None:
        print("♻️ Réponse chargée depuis le cache.")
        return cached

    start = time.time()
    print(f"⏱️ Démarrage à {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

    prompt = f"""
Nettoie ce texte de cahier des charges :

- Supprime noms propres, titres, éléments inutiles
- Reformule en phrases claires
- Extrait les exigences :

# Exigences Fonctionnelles
- ...

# Exigences Non Fonctionnelles
- ...

Texte :
{text_chunk}
"""
    response = ollama.generate(
        model="mistral",
        prompt=prompt,
        options={"temperature": 0.3}
    )
    end = time.time()
    print(f"✅ Terminé à {datetime.now().strftime('%H:%M:%S.%f')[:-3]} — durée : {end - start:.2f}s")

    result = response['response'].strip()
    save_to_cache(text_chunk, result)
    return result

def main():
    raw_cahier = extract_text_from_pdf("cahier1.pdf")
    chunks = chunk_text(raw_cahier)
    print(f"✅ Cahier divisé en {len(chunks)} morceaux.\n")

    all_outputs = []
    for chunk in chunks:
        result = traiter_chunk_avec_cache(chunk)
        all_outputs.append(result)

    full_result = "\n\n".join(all_outputs)

    print("✅ Terminé.")
    with open("exigences.txt", "w", encoding="utf-8") as f:
        f.write(full_result)

if __name__ == "__main__":
    main()
