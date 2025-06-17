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

def chunk_text(text, max_size=1500):
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
Tu es un expert en analyse de cahiers des charges techniques. Ta tâche est d’extraire **Uniquement** les exigences fonctionnelles et non fonctionnelles claires et précises, en les reformulant pour qu’elles soient concises, distinctes, non répétées, et facilement exploitables par une équipe de développement.

### Règles :

- Ignore **tout contenu narratif**, descriptif, introductif ou stratégique **qui ne correspond pas directement à une exigence technique précise**.
- Supprime les phrases génériques, vagues ou marketing (ex : “le logiciel sera performant”, “interface intuitive”) si elles ne contiennent pas de critères mesurables ou d’indications claires.
- Ne conserve pas d’exigences trop générales ou imprécises qui ne peuvent pas être traduites en tâches techniques concrètes.
- Reformule les exigences avec un vocabulaire technique clair et précis, compréhensible par des développeurs, en utilisant des phrases courtes, claires et simples pour faciliter la détection des doublons.
- Utilise un vocabulaire simple, standard et cohérent, compris de tous les membres de l’équipe (développeurs, testeurs, PO).  
  Privilégie des verbes d’action usuels comme « consulter », « envoyer », « accéder », « modifier » et évite les variations inutiles (ex : ne pas alterner entre “visualiser” et “consulter”).
-Utilise un vocabulaire standardisé et des formulations uniformes, en commençant chaque exigence fonctionnelle par « Un utilisateur peut... » suivi d’un verbe à l’infinitif décrivant l’action (ex : « accéder », « consulter », « suivre »).
- Découpe toute exigence composée en **plusieurs exigences unitaires**.
- Chaque exigence doit pouvoir être transformée en tâche dans un backlog technique.
- Si le texte ne contient que des informations vagues ou trop générales, ne génère pas d’exigences fonctionnelles ou non fonctionnelles pour ces passages.

- **N’inclus aucune exigence liée aux actions ou droits des administrateurs ou gestionnaires.**  
- Si une exigence mentionne plusieurs rôles (utilisateur, administrateur, système), conserve uniquement la partie relative aux utilisateurs finaux (approche boîte noire).
- Quand tu parles du système, inclus uniquement des exigences **précises, concrètes et observables**.  
- Chaque exigence fonctionnelle doit décrire une **action ou un effet initié ou observable par un utilisateur final** (ex. utilisateur ou entreprise).
- Les tests doivent pouvoir être réalisés du point de vue de l’utilisateur, sans connaissance du fonctionnement interne.
- Si une exigence mentionne une action système (ex. validation, filtrage, tri), elle doit être reformulée selon l’expérience utilisateur observable.
  - ❌ "Le système trie les offres par pertinence."
  - ✅ "Un utilisateur peut consulter les offres triées automatiquement par pertinence."
  - ❌ "Le système vérifie la taille des pièces jointes."
  - ✅ "Un utilisateur ne peut pas envoyer de pièce jointe trop volumineuse."
- L’objectif est de refléter uniquement ce que **l’utilisateur peut voir, faire ou recevoir**, pas ce que le système exécute en arrière-plan.

  Par exemple, **conserve** :
  - "Le système affiche une notification lorsqu’un utilisateur reçoit un nouveau message."  
  - "Le système valide le format de l’adresse email lors de la saisie."  
  Et **exclue** :  
  - "Le système gère les données utilisateurs."  
  - "Le système assure la sécurité des accès."  
  - "Le système peut évaluer la pertinence des candidatures." (trop vague ou non observable)

- Ne mentionne **aucun format technique** (ex : Base64, JSON, PDF, XML) ni aucun traitement algorithmique interne (ex : parsing, analyse sémantique, extraction automatique, NLP, cryptage, matching de compétences, Machine Learning).
- Si une exigence décrit une analyse ou un traitement interne, **ne conserve que le résultat visible pour l’utilisateur**.
  - ❌ "Le système extrait les compétences du CV en PDF."
  - ✅ "Un utilisateur peut consulter les compétences détectées dans son CV."
- Ne conserve que les effets ou interactions **directement visibles ou compréhensibles par un utilisateur final** (ex : affichage, bouton, message, interaction).

---

### Précisions sur les exigences fonctionnelles :

- Les exigences fonctionnelles décrivent uniquement les actions, comportements ou fonctionnalités directement observables et réalisables par les utilisateurs finaux (approche boîte noire).
- Ne jamais mentionner d’éléments techniques internes, comme base de données, architecture, systèmes backend ou plateformes.
- Évite les formulations vagues, générales ou passives telles que « assurer la communication », « permettre la gestion », « faciliter la collaboration ».
- Chaque exigence fonctionnelle doit décrire précisément ce que fait l’utilisateur, par exemple :  
   • Un utilisateur peut envoyer un message à un autre utilisateur.  
   • Un utilisateur peut s’inscrire et se connecter à son compte.  
   • Le système affiche une notification lorsque l’utilisateur reçoit un nouveau message.  
- Si une exigence est trop générale, découpe-la en sous-exigences claires et concrètes ou ne la conserve pas si elle reste imprécise.

---

### Exigences Non Fonctionnelles :

- Décrivent les qualités ou caractéristiques du logiciel (performance, sécurité, accessibilité, etc.).
- Doivent être précises et mesurables.

---

### Consignes importantes :

- Ne fournis **que** deux listes numérotées, une pour les exigences fonctionnelles et une pour les exigences non fonctionnelles.
- Ne fournis aucun autre texte, explication, ni introduction.
- Reformule les exigences pour qu’elles soient claires, concises, distinctes et uniques.
- Ne mélange pas exigences fonctionnelles et non fonctionnelles.
- Si aucune exigence fonctionnelle ou non fonctionnelle claire n’est trouvée, renvoie simplement les listes vides.

---

### Structure de sortie attendue :

Exigences Fonctionnelles :  
1. Fonctionnalité 1  
2. Fonctionnalité 2  
...

Exigences Non Fonctionnelles :  
1. Caractéristique 1  
2. Caractéristique 2  
...

---

Voici le texte à analyser et traiter :  
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
    """
    Lit un fichier texte contenant des exigences fonctionnelles et non fonctionnelles, 
    extrait et regroupe toutes ces exigences en deux listes numérotées distinctes.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Expressions régulières pour trouver les blocs d'exigences
    func_pattern = re.compile(
        r'Exigences Fonctionnelles\s*:(.*?)(?=Exigences Non Fonctionnelles|Exigences Fonctionnelles|$)',
        re.DOTALL
    )
    non_func_pattern = re.compile(
        r'Exigences Non Fonctionnelles\s*:(.*?)(?=Exigences Fonctionnelles|Exigences Non Fonctionnelles|$)',
        re.DOTALL
    )

    func_blocks = func_pattern.findall(content)
    non_func_blocks = non_func_pattern.findall(content)

    def extract_items(block):
        # Découpe sur les lignes numérotées, ex: "1. ", "2. ", etc.
        items = re.split(r'\n\d+\.\s+', block.strip())
        if items and not items[0].strip():
            items.pop(0)
        return [item.strip().replace('\n', ' ') for item in items if item.strip()]

    all_func = []
    for block in func_blocks:
        all_func.extend(extract_items(block))

    all_non_func = []
    for block in non_func_blocks:
        all_non_func.extend(extract_items(block))

    output = "Exigences Fonctionnelles :\n"
    for i, req in enumerate(all_func, 1):
        output += f"{i}. {req}\n"
    output += "\nExigences Non Fonctionnelles :\n"
    for i, req in enumerate(all_non_func, 1):
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