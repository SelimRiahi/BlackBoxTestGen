from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

embedding_model = SentenceTransformer('paraphrase-mpnet-base-v2')
model_name = "joeddav/xlm-roberta-large-xnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()  # eval mode

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_functional_requirements(filepath, func):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("**Exigences Fonctionnelles :**\n")
        for i, line in enumerate(func, 1):
            f.write(f"{i}. {line.strip()}\n")

def extract_sections(filepath):
    text = read_file(filepath)
    func_match = re.search(
        r"Exigences Fonctionnelles ?:?\s*\n(.*?)(?=\n\s*\n|Exigences Non Fonctionnelles ?:|$)",
        text, re.DOTALL | re.IGNORECASE
    )
    func_text = func_match.group(1) if func_match else ""

    def extract_items(block):
        lines = block.strip().split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            if not line or line == '**':
                continue
            line = re.sub(r'^\d+\.\s*', '', line)
            line = line.strip('*').strip()
            if line:
                clean_lines.append(line)
        return clean_lines

    func_list = extract_items(func_text)
    return {'func': func_list}

def get_similar_pairs(reqs, embeddings, candidate_threshold=0.6):
    pairs = []
    n = len(reqs)
    for i in range(n):
        for j in range(i+1, n):
            sim = util.pytorch_cos_sim(embeddings[i], embeddings[j])[0].item()
            if sim > candidate_threshold:
                pairs.append((i, j, sim))
    return pairs

def deduplicate_by_similarity(reqs, candidate_threshold=0.6, removal_threshold=0.9):
    embeddings = embedding_model.encode(reqs, convert_to_tensor=True)
    to_remove = set()
    n = len(reqs)

    with open("similarity_log.txt", "a", encoding="utf-8") as sim_log:
        pairs = get_similar_pairs(reqs, embeddings, candidate_threshold)
        for i, j, sim in pairs:
            if i in to_remove or j in to_remove:
                continue
            sim_log.write(f"Similarity '{reqs[i]}' ↔ '{reqs[j]}' = {sim:.3f}\n")
            if sim >= removal_threshold:
                # Remove the shorter sentence to keep the longer one
                removed = i if len(reqs[i]) < len(reqs[j]) else j
                sim_log.write(f"Removing index {removed} due to similarity >= {removal_threshold}\n")
                to_remove.add(removed)

    filtered = [reqs[i] for i in range(n) if i not in to_remove]
    return filtered

def is_paraphrase(s1, s2, threshold=0.9):
    inputs = tokenizer(s1, s2, return_tensors='pt', truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1)
    entailment1 = probs[0][2].item()

    inputs = tokenizer(s2, s1, return_tensors='pt', truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1)
    entailment2 = probs[0][2].item()

    with open("nli_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(
            f"NLI '{s1}' ↔ '{s2}' = entail1={entailment1:.3f}, entail2={entailment2:.3f}, "
            f"→ max={max(entailment1, entailment2):.3f}\n"
        )

    return max(entailment1, entailment2) >= threshold

def deduplicate_by_nli_parallel(reqs, candidate_threshold=0.6, threshold=0.9):
    embeddings = embedding_model.encode(reqs, convert_to_tensor=True)
    pairs = get_similar_pairs(reqs, embeddings, candidate_threshold)

    to_remove = set()

    def nli_worker(pair):
        i, j, _ = pair
        if i in to_remove or j in to_remove:
            return None
        if is_paraphrase(reqs[i], reqs[j], threshold):
            # Remove the shorter sentence to keep the longer one
            return i if len(reqs[i]) < len(reqs[j]) else j
        return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(nli_worker, pair) for pair in pairs]
        for future in as_completed(futures):
            res = future.result()
            if res is not None:
                to_remove.add(res)

    filtered = [reqs[i] for i in range(len(reqs)) if i not in to_remove]
    return filtered

def clean_requirements(reqs):
    print(f"\nStarting with {len(reqs)} requirements.")

    print("=== Step 1: Similarity Deduplication ===")
    reqs_step1 = deduplicate_by_similarity(reqs, candidate_threshold=0.6, removal_threshold=0.9)
    removed_sim = len(reqs) - len(reqs_step1)
    print(f"Similarity deduplication removed {removed_sim} items.")

    print("\n=== Step 2: NLI Deduplication (parallel) ===")
    reqs_final = deduplicate_by_nli_parallel(reqs_step1, candidate_threshold=0.6, threshold=0.9)
    removed_nli = len(reqs_step1) - len(reqs_final)
    print(f"NLI deduplication removed {removed_nli} items.")

    print(f"Final count after deduplication: {len(reqs_final)} requirements.")
    return reqs_final

def main():
    # Clear logs before starting
    open("similarity_log.txt", "w").close()
    open("nli_log.txt", "w").close()

    file_path = 'exigences_organisees.txt'
    sections = extract_sections(file_path)
    func_clean = clean_requirements(sections['func'])
    write_functional_requirements(file_path, func_clean)

if __name__ == "__main__":
    main()
