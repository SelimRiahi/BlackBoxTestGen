import os
import re
import time
import hashlib
import pdfplumber
import ollama
from datetime import datetime

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


def traiter_document_complet(text):
    prompt = f"""
Tu es un expert en analyse de cahiers des charges techniques. À partir du texte ci-dessous, ta tâche est d’extraire **uniquement** les exigences fonctionnelles et non fonctionnelles, et de les formuler de manière **très concise**, en te limitant à **quelques mots clairs et standardisés**.

---

### Instructions :
- Ignore les exigences qui ne contiennent pas une action claire et observable, un objet ou un contexte précis, ainsi que les détails nécessaires pour permettre la création d’un scénario de test concret.
- Ne conserve que les exigences permettant de décrire une interaction ou un résultat observable par un utilisateur final.
- Décris uniquement ce que l’utilisateur peut faire, voir ou recevoir depuis l’extérieur du système.
- Chaque exigence fonctionnelle doit être résumée en **4 à 8 mots maximum**, sous la forme d’une action concrète faite ou observée par l’utilisateur.
- Utilise un vocabulaire standardisé (ex. : « Se connecter », « Voir les messages », « Envoyer un message »).
- Ne décris **jamais** le fonctionnement interne du système.
- Évite toute phrase ou formulation longue, descriptive ou narrative.
- Supprime les doublons ou exigences très similaires.
- Garde uniquement les exigences **black-box**, visibles côté utilisateur.
- Si plusieurs actions sont mentionnées dans une seule exigence, reformule-les en **exigences séparées, chacune avec une action unique**.
- Ignore les rôles administrateur, backend, base de données, traitement technique.
- Ne génère **aucun texte explicatif**. Seulement deux listes.

---

### Format de sortie attendu :

Exigences Fonctionnelles :
1. ...
2. ...
3. ...

Exigences Non Fonctionnelles :
1. ...
2. ...
3. ...

---

Voici le texte à analyser :
{text}
"""

    print(f"⏱️ Début traitement à {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    response = ollama.generate(
        model="llama3.1",
        prompt=prompt,
        options={"temperature": 0}
    )
    print(f"✅ Fin traitement à {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    return response["response"].strip()


def main():
    pdf_path = "cahier1.pdf"
    full_text = extract_text_from_pdf(pdf_path)
    result = traiter_document_complet(full_text)

    with open("test.txt", "w", encoding="utf-8") as f:
        f.write(result)

    print("📄 Résultat enregistré dans test.txt")


if __name__ == "__main__":
    main()
