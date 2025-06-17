from concurrent.futures import ThreadPoolExecutor
import time
import ollama

def call_model(i):
    start = time.time()
    prompt = f"Test de performance, requête numéro {i}"
    ollama.generate(
        model="mistral",
        prompt=prompt,
        options={"temperature": 0.3}
    )
    duration = time.time() - start
    print(f"✅ Requête {i} terminée en {duration:.2f}s")
    return duration

def tester_parallel(n):
    print(f"\n🔁 Test avec {n} workers en parallèle...")
    start = time.time()
    with ThreadPoolExecutor(max_workers=n) as executor:
        durations = list(executor.map(call_model, range(n)))
    total = time.time() - start
    print(f"⏱️ Temps total pour {n} requêtes : {total:.2f}s")
    print(f"⏱️ Temps moyen par requête : {sum(durations)/n:.2f}s")

if __name__ == "__main__":
    for workers in [1, 2, 4, 6, 8]:
        tester_parallel(workers)
