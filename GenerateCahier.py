import os
import re
import time
import hashlib
import pdfplumber
import ollama
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess




CACHE_DIR = "cache"


def extract_text_from_pdf(pdf_path):
    """
    Extrait tout le texte d’un fichier PDF (y compris les tableaux).
    """
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
            tables = page.extract_tables()
            for table in tables:
                table_text = "\n".join([
                    "\t".join(cell if cell is not None else "" for cell in row)
                    for row in table if row
                ])
                all_text.append(table_text)
    return "\n\n".join(all_text)

"""def split_into_sentences(text):

    sentence_endings = re.compile(r'(?<=[.!?]) +')
    sentences = sentence_endings.split(text)
    return sentences"""

def chunk_text(text, max_size=2500):
    """
    Découpe le texte en morceaux ("chunks") de taille maximale max_size,
    sans découper au milieu des phrases (simplifié, découpe juste par paragraphe ou morceaux fixes).
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for p in paragraphs:
        if len(p) <= max_size:
            # Si le paragraphe est court, on tente de l'ajouter au chunk courant
            if len(current) + len(p) + 2 <= max_size:
                current += p + "\n\n"
            else:
                if current:
                    chunks.append(current.strip())
                current = p + "\n\n"
        else:
            # Paragraphe trop long, on coupe en morceaux fixes max_size
            for i in range(0, len(p), max_size):
                piece = p[i:i+max_size]
                if len(current) + len(piece) + 1 <= max_size:
                    current += piece + " "
                else:
                    if current:
                        chunks.append(current.strip())
                    current = piece + " "

            current += "\n\n"

    if current:
        chunks.append(current.strip())

    print(f"Chunks count after resizing: {len(chunks)}")
    return chunks

def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_filename(text_chunk):
    """
    Génère un nom de fichier unique pour chaque chunk à partir de son hash MD5.
    Permet de stocker en cache les réponses LLM dans le dossier cache/.
    """
    chunk_hash = hashlib.md5(text_chunk.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"cache_{chunk_hash}.txt")  # <-- Add cache/ folder here

def save_to_cache(text_chunk, response):
    """
    Sauvegarde la réponse dans un fichier cache spécifique au chunk.
    """
    ensure_cache_dir()  # Make sure cache/ exists before saving

    filename = get_cache_filename(text_chunk)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(response)

def load_from_cache(text_chunk):
    """
    Charge la réponse d'un chunk depuis le cache si disponible.
    """
    filename = get_cache_filename(text_chunk)
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def traiter_chunk_avec_cache(text_chunk):
    """
    Traite un chunk :
    - Vérifie le cache avant d'appeler Ollama
    - Envoie le prompt à Ollama avec le chunk
    - Sauvegarde la réponse en cach
    """
    cached = load_from_cache(text_chunk)
    if cached is not None:
        print("♻️ Réponse chargée depuis le cache.")
        return cached

    start = time.time()
    print(f"⏱️ Démarrage à {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

    prompt = f"""
Tu es un expert en analyse de cahiers des charges techniques. À partir du texte ci-dessous, ta tâche est d’extraire **uniquement** les exigences fonctionnelles et non fonctionnelles, et de les formuler de manière **très concise**, en te limitant à **6 mots maximum**, avec un vocabulaire simple et clair.

---

### Instructions :
- Ignore les exigences sans action claire, objet ou contexte précis, ainsi que les détails inutiles pour un scénario de test.
- Ne conserve que les exigences décrivant une interaction observable par un utilisateur final, avec assez d’informations pour être testées.
- Décris uniquement ce que l’utilisateur (rôle) peut faire, voir ou recevoir depuis l’extérieur du système.
- Chaque exigence doit inclure un **rôle** (ex : utilisateur, étudiant), un **verbe** (action), et un **objet**.  
- L’**objet** peut être détaillé si nécessaire pour être clair et compréhensible.
- Utilise un vocabulaire standardisé et simple (ex : « Étudiant s'inscrire », « Utilisateur voir messages »).
- Reformule toute exigence avec plusieurs actions en exigences séparées avec une seule action chacune.
- Supprime les doublons ou exigences très similaires.
- Ignore les rôles techniques (administrateur, backend, base de données).
- Ne génère **aucun texte explicatif**. Seulement deux listes.

---

### Format de sortie attendu :

Exigences Fonctionnelles :  
1. ...  
2. ...  
3. ...  



Voici le texte à analyser :
{text_chunk}
"""









    response = ollama.generate(
        model="llama3.1",
        prompt=prompt,
        options={"temperature": 0}
    )
    end = time.time()
    print(f"✅ Terminé à {datetime.now().strftime('%H:%M:%S.%f')[:-3]} — durée : {end - start:.2f}s")

    result = response['response'].strip()
    save_to_cache(text_chunk, result)
    return result



def organize_exigences(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    func_pattern = re.compile(
        r'Exigences Fonctionnelles\s*:(.*?)(?=Exigences Fonctionnelles|Exigences Non Fonctionnelles|$)',
        re.DOTALL
    )
    func_blocks = func_pattern.findall(content)

    def extract_items(block):
        # Extraction simple des lignes numérotées
        items = re.findall(r'\d+\.\s+(.*)', block)
        return [item.strip().replace('\n', ' ') for item in items if item.strip()]

    all_func = []
    for block in func_blocks:
        all_func.extend(extract_items(block))

    output = "Exigences Fonctionnelles :\n"
    for i, req in enumerate(all_func, 1):
        output += f"{i}. {req}\n"

    return output


def main():
    # Extraction texte complet du PDF
    raw_cahier = extract_text_from_pdf("cahier1.pdf")

    # Découpage du texte en morceaux
    chunks = chunk_text(raw_cahier)
    print(f"✅ Cahier divisé en {len(chunks)} morceaux.\n")

    all_outputs = [""] * len(chunks)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(traiter_chunk_avec_cache, chunk): idx for idx, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result()
                all_outputs[idx] = result
            except Exception as e:
                print(f"⚠️ Erreur lors du traitement du chunk {idx}: {e}")

    # Fusion des résultats bruts
    full_result = "\n\n".join(all_outputs)
    with open("exigences.txt", "w", encoding="utf-8") as f:
        f.write(full_result)
    print("📄 Exigences brutes enregistrées dans exigences.txt")

    # Nettoyage final
    organized_text = organize_exigences('exigences.txt')

   

    # Optional: save to a new file
    with open('exigences_organisees.txt', 'w', encoding='utf-8') as f_out:
        f_out.write(organized_text)


    subprocess.run(['python', 'Transform.py'], check=True)
    ##subprocess.run(['python', 'verifier_exigences.py'], check=True)


if __name__ == "__main__":
    main()