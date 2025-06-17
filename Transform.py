import re
import spacy
from sentence_transformers import SentenceTransformer, util

# Load French model once globally
#pip uninstall fr-core-news-lg
nlp = spacy.load("fr_core_news_lg")

def extract_sections(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    func_match = re.search(r'Exigences Fonctionnelles\s*:(.*?)(?=Exigences Non Fonctionnelles\s*:|$)', content, re.DOTALL)
    non_func_match = re.search(r'Exigences Non Fonctionnelles\s*:(.*)', content, re.DOTALL)

    def extract_items(block_text):
        if not block_text:
            return []
        items = re.findall(r'^\d+\.\s+(.*)$', block_text, flags=re.MULTILINE)
        return [item.strip() for item in items]

    func_reqs = extract_items(func_match.group(1) if func_match else "")
    non_func_reqs = extract_items(non_func_match.group(1) if non_func_match else "")

    return {'func': func_reqs, 'non_func': non_func_reqs}

def write_sections(file_path, func_reqs, non_func_reqs):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("Exigences Fonctionnelles :\n")
        for i, req in enumerate(func_reqs, 1):
            f.write(f"{i}. {req}\n")
        f.write("\nExigences Non Fonctionnelles :\n")
        for i, req in enumerate(non_func_reqs, 1):
            f.write(f"{i}. {req}\n")



def simplify_sentence(sentence):
    doc = nlp(sentence)
    important_deps = {"nsubj", "nsubjpass", "ROOT", "obj", "dobj", "iobj", "ccomp", "xcomp", "compound"}

    tokens_to_keep = set()

    def include_aux_neg(token):
        tokens = [token]
        tokens += [child for child in token.children if child.dep_ in ("aux", "auxpass", "neg")]
        return tokens

    for token in doc:
        if token.dep_ in important_deps:
            tokens_to_keep.update(include_aux_neg(token))

    tokens_to_keep = sorted(tokens_to_keep, key=lambda t: t.i)

    # Optionally lemmatize:
    simplified = " ".join([token.lemma_ for token in tokens_to_keep])

    return simplified.strip()


def deduplicate_requirements(reqs, similarity_threshold=0.85):
    if not reqs:
        return []

    # Simplify sentences before comparing
    simplified_reqs = [simplify_sentence(r) for r in reqs]

    model = SentenceTransformer('paraphrase-mpnet-base-v2')
    embeddings = model.encode(simplified_reqs, convert_to_tensor=True)

    unique_indices = []
    seen = set()

    for i in range(len(reqs)):
        if i in seen:
            continue
        unique_indices.append(i)
        cos_scores = util.pytorch_cos_sim(embeddings[i], embeddings)[0]
        similar_idxs = (cos_scores > similarity_threshold).nonzero(as_tuple=True)[0].tolist()
        for idx in similar_idxs:
            if idx != i:
                seen.add(idx)

    return [reqs[i] for i in unique_indices]

def main():
    file_path = 'exigences_organisees.txt'
    print("Cleaning pending...")

    # Extract requirements sections from file
    sections = extract_sections(file_path)

    # Deduplicate functional and non-functional separately
    func_clean = deduplicate_requirements(sections['func'])
    non_func_clean = deduplicate_requirements(sections['non_func'])

    print(f"Writing cleaned requirements back to {file_path}...")
    write_sections(file_path, func_clean, non_func_clean)

    print("Done!")

if __name__ == "__main__":
    main()
