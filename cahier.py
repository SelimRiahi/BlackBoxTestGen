import os
import hashlib
import pdfplumber
import ollama
import time
from datetime import datetime
import re

def extract_text_from_pdf(pdf_path):
    """
    Extrait tout le texte (y compris les tables) d'un PDF.
    Retourne un texte unique avec paragraphes séparés par des doubles sauts de ligne.
    """
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
            tables = page.extract_tables()
            for table in tables:
                # Convertir la table en texte tabulé
                table_text = "\n".join([
                    "\t".join(cell if cell is not None else "" for cell in row)
                    for row in table if row
                ])
                all_text.append(table_text)
    return "\n\n".join(all_text)

def split_into_sentences(text):
    """
    Découpe un texte en phrases en se basant sur la ponctuation classique.
    """
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    sentences = sentence_endings.split(text)
    return sentences

def chunk_text(text, max_size=800):
    """
    Découpe le texte en morceaux ("chunks") de taille maximale max_size,
    en évitant de couper au milieu des phrases autant que possible.
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
            # Paragraphe trop long, on découpe en phrases
            sentences = split_into_sentences(p)
            for s in sentences:
                if len(s) > max_size:
                    # Phrase très longue, on la coupe en morceaux stricts
                    for i in range(0, len(s), max_size):
                        piece = s[i:i+max_size]
                        if len(current) + len(piece) + 1 <= max_size:
                            current += piece + " "
                        else:
                            if current:
                                chunks.append(current.strip())
                            current = piece + " "
                else:
                    if len(current) + len(s) + 1 <= max_size:
                        current += s + " "
                    else:
                        if current:
                            chunks.append(current.strip())
                        current = s + " "
            current += "\n\n"

    if current:
        chunks.append(current.strip())

    print(f"Chunks count after improved resizing: {len(chunks)}")
    return chunks

def get_cache_filename(text_chunk):
    """
    Génère un nom de fichier unique pour chaque chunk à partir de son hash MD5.
    Permet de stocker en cache les réponses LLM.
    """
    chunk_hash = hashlib.md5(text_chunk.encode('utf-8')).hexdigest()
    return f"cache_{chunk_hash}.txt"

def save_to_cache(text_chunk, response):
    """
    Sauvegarde la réponse dans un fichier cache spécifique au chunk.
    """
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
Tu es un expert en analyse de cahiers des charges techniques. Ta tâche est d’extraire *Uniquement* les exigences fonctionnelles et non fonctionnelles claires et précises, en les reformulant pour qu’elles soient concises, distinctes, non répétées, et facilement exploitables par une équipe de développement.

### Règles :

- Ignore *tout contenu narratif*, descriptif, introductif ou stratégique *qui ne correspond pas directement à une exigence technique précise*.
- Supprime les phrases génériques, vagues ou marketing (ex : “le logiciel sera performant”, “interface intuitive”) si elles ne contiennent pas de critères mesurables ou d’indications claires.
- Ne conserve pas d’exigences trop générales ou imprécises qui ne peuvent pas être traduites en tâches techniques concrètes.
- Reformule les exigences avec un vocabulaire technique clair et précis, compréhensible par des développeurs.
- Découpe toute exigence composée en *plusieurs exigences unitaires*.
- Chaque exigence doit pouvoir être transformée en tâche dans un backlog technique.
- Si le texte ne contient que des informations vagues ou trop générales, ne génère pas d’exigences fonctionnelles ou non fonctionnelles pour ces passages.


- Ne sois pas obligé de créer des exigences fonctionnelles si le texte ne contient pas d’informations précises, concrètes et observables selon une approche boîte noire.  
- Il vaut mieux laisser la liste fonctionnelle vide plutôt que d’inclure des exigences vagues, imprécises, ou basées sur des suppositions internes.  
- Priorise toujours la qualité et la précision des exigences plutôt que la quantité.
---

### Précisions sur les exigences fonctionnelles :

- Les exigences fonctionnelles doivent décrire uniquement des actions, comportements ou fonctionnalités directement observables et réalisables par les utilisateurs finaux (approche boîte noire).
- Ne jamais mentionner d’éléments techniques internes, comme base de données, architecture, systèmes, plateformes ou processus backend.
- Évite les formulations vagues, générales ou passives telles que « assurer la communication », « permettre la gestion », « faciliter la collaboration ».
- Chaque exigence fonctionnelle doit décrire précisément ce que fait l’utilisateur ou ce que le système affiche, en termes concrets, par exemple :  
   • Un utilisateur peut envoyer un message à un autre utilisateur.  
   • Un administrateur peut ajouter, modifier ou supprimer un compte utilisateur.  
   • Le système affiche une notification lorsque l’utilisateur reçoit un nouveau message.
- Si une exigence est trop générale, découpe-la en sous-exigences claires et concrètes ou ne la conserve pas si elle reste imprécise.

---


Voici la distinction importante à garder en tête :

1.Exigences Fonctionnelles : ce que le logiciel doit faire, c’est-à-dire les fonctionnalités, actions, processus ou comportements observables que l’utilisateur peut réaliser, exclusivement selon une approche boîte noire (fonctionnalités visibles et utilisables par l’utilisateur, sans aucune information interne, technique ou d’architecture).
Les exigences fonctionnelles doivent être formulées selon une approche boîte noire, sans mention d’éléments techniques internes, bases de données, ou architecture.
Exemples :  
- Un utilisateur peut s’inscrire et se connecter à son compte.  
- Un administrateur peut gérer les utilisateurs (créer, modifier, supprimer des comptes).  
- Un stagiaire peut consulter et postuler aux offres de stage disponibles.  
- Le système envoie automatiquement un email de confirmation lors de l’inscription d’un utilisateur.  

2. Exigences Non Fonctionnelles : les caractéristiques ou qualités du logiciel, c’est-à-dire *comment* il doit être (qualité, performance, sécurité, maintenance, accessibilité, etc.).  
Exemples :  
- Temps de réponse inférieur à 300 ms  
- Sécurité par authentification multi-niveau (OAuth2, JWT)  
- Conformité à la norme WCAG 2.1 pour l’accessibilité  

Tu dois produire une réponse structurée en deux listes numérotées, une pour chaque type d’exigences, en évitant tout chevauchement.

### Consignes importantes :
- Ne conserve *que* les exigences, en supprimant tout contexte, justification, historique, ou information superflue.
- Reformule les exigences pour qu’elles soient claires, concises, distinctes, et compréhensibles par une équipe de développement.
- Assure-toi que chaque exigence soit unique. Si deux phrases expriment la même intention, conserve uniquement la version la plus claire.
- Ne mélange pas exigences fonctionnelles et non fonctionnelles.

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
    # Extraction texte complet du PDF
    raw_cahier = extract_text_from_pdf("cahier1.pdf")

    # Découpage du texte en chunks optimisés
    chunks = chunk_text(raw_cahier)
    print(f"✅ Cahier divisé en {len(chunks)} morceaux.\n")

    all_outputs = []
    # Traitement séquentiel de chaque chunk
    for chunk in chunks:
        result = traiter_chunk_avec_cache(chunk)
        all_outputs.append(result)

    full_result = "\n\n".join(all_outputs)

    # Sauvegarde du résultat final dans un fichier texte
    print("✅ Terminé.")
    with open("exigences.txt", "w", encoding="utf-8") as f:
        f.write(full_result)

if __name__ == "__main__":
    main()
