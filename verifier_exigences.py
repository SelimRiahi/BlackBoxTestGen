"""
Script: verifier_exigences.py
Purpose: 
- Load already organized requirements file (exigences_organisees.txt)
- Use AI model with a custom prompt to check and flag misplaced or non-black-box-testable functional requirements, or technical details that shouldn't be there
- Keep everything else unchanged
- Output the cleaned/verified requirements into exigences_finales.txt
"""

from datetime import datetime
import ollama  # Make sure ollama is installed and imported

def read_file(filepath):
    """Read and return the entire text content of the given file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    """Write the given content string into the specified file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)



def verify_exigences(text):
    prompt = f"""
Tu es un expert en analyse de cahiers des charges techniques. Je vais te fournir un long texte contenant des exigences fonctionnelles et non fonctionnelles (parfois mélangées, parfois redondantes).

Ta mission est de **supprimer uniquement les vraies doublons** (deux phrases qui expriment exactement la même intention, avec les mêmes mots ou quasi les mêmes mots, sans distinction d’action ou de perspective). Ne touche à rien d’autre.

### Règles à suivre strictement :

1. ❌ **Ne reformule aucune exigence.**
2. ❌ **Ne supprime pas une exigence parce qu’elle te semble "redondante" s’il y a une nuance** (exemple : "l’utilisateur peut signer" ≠ "le rapport affiche la signature").
3. ✅ **Supprime seulement les phrases réellement identiques ou disant exactement la même chose.**
4. ✅ **Préserve toutes les différences d’actions, d’acteurs, de cibles ou de contextes.**
5. ❌ **Ne classe pas, ne trie pas, ne résume pas.**
6. ❌ **Ne fusionne pas des phrases ensemble.**
7. ✅ **Garde la structure et l’ordre d’origine.**

### Exemple de cas à garder tous les deux :
- "L’utilisateur peut déposer un document."
- "Le système affiche le document déposé dans l’interface admin."
👉 Ce sont deux comportements différents et testables, donc à garder.

À la fin, rends-moi le texte nettoyé uniquement des doublons exacts, sans toucher à tout le reste.


**Exigences Fonctionnelles :**  
1. ...  
2. ...  

**Exigences Non Fonctionnelles :**  
1. ...  
2. ...  

Voici le texte à traiter :  
{text}

"""

    print(f"⏱️ Starting verification at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

    response = ollama.generate(
        model="llama3.1",
        prompt=prompt,
        options={"temperature": 0}
    )

    result = response['response'].strip()

    print(f"✅ verification done at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

    return result


def main():
    input_file = "exigences_organisees.txt"
    output_file = "exigences_finales.txt"

    # Read the organized exigences file
    exigences_text = read_file(input_file)

    # Use model to verify and mark misplaced exigences
    verified_text = verify_exigences(exigences_text)

    # Write the verified exigences to the new file
    write_file(output_file, verified_text)

    print(f"✅ Vérification terminée. Résultat sauvegardé dans {output_file}")

if __name__ == "__main__":
    main()
