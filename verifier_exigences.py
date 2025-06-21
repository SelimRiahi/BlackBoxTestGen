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
Tu es un expert en analyse de cahiers des charges fonctionnels.

Je vais te donner une liste d'exigences (fonctionnelles ou non) déjà nettoyées. Certaines peuvent néanmoins exprimer la même idée avec des formulations différentes.

Ta tâche est la suivante :

1. Compare toutes les phrases entre elles.
2. Si plusieurs phrases expriment la **même idée** ou **même intention**, **garde uniquement celle qui est la plus claire, précise et testable**.
3. Supprime celles qui disent **exactement la même chose**, même si elles utilisent d'autres mots.
4. Ne touche pas aux autres.

### Attention :
- ❌ Ne reformule rien.
- ❌ Ne modifie pas l’ordre.
- ✅ Supprime uniquement les doublons sémantiques.
- ✅ Préserve toutes les différences de sens, de contexte ou d’action.


**Exigences Fonctionnelles :**  
1. ...  
2. ...  

**Exigences Non Fonctionnelles :**  
1. ...  
2. ...  

Voici les exigences à traiter :  

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
