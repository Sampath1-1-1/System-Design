# Extracted from manuscript/book1-traditional/16-search-systems.md §16.5.4 (listing 3). Edit the manuscript, not this file.
"""A tiny search engine: analysis, a positional inverted index, BM25 with field boosts.
Standard library only. Run: python3 search_engine.py"""
import math
import re
from collections import defaultdict

STOP_WORDS = {"a", "an", "and", "the", "for", "with", "of", "in", "to", "is", "are"}

def s_stem(token):
    """Harman's 'S' stemmer: strips only plural endings (like Lucene's EnglishMinimalStemFilter)."""
    if len(token) > 3 and token.endswith("ies") and not token.endswith(("eies", "aies")):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("es") and not token.endswith(("aes", "ees", "oes")):
        return token[:-1]
    if len(token) > 3 and token.endswith("s") and not token.endswith(("us", "ss")):
        return token[:-1]
    return token

def analyze(text):
    """Tokenize on non-alphanumerics, lowercase, drop stop words, stem. Keeps positions."""
    out = []
    for pos, raw in enumerate(re.findall(r"[a-z0-9]+", text.lower())):
        if raw not in STOP_WORDS:
            out.append((s_stem(raw), pos))
    return out

class InvertedIndex:
    def __init__(self, fields):
        self.fields = fields
        # postings[field][term] -> {doc_id: [positions]}  (doc_ids inserted in increasing order)
        self.postings = {f: defaultdict(dict) for f in fields}
        self.doc_len = {f: {} for f in fields}
        self.n_docs = 0

    def add(self, doc_id, doc):
        self.n_docs += 1
        for f in self.fields:
            tokens = analyze(doc[f])
            self.doc_len[f][doc_id] = len(tokens)
            for term, pos in tokens:
                self.postings[f][term].setdefault(doc_id, []).append(pos)

    def avgdl(self, f):
        return sum(self.doc_len[f].values()) / self.n_docs

    def idf(self, f, term):
        n = len(self.postings[f].get(term, {}))
        return math.log(1 + (self.n_docs - n + 0.5) / (n + 0.5))   # Lucene's BM25 IDF

    def bm25_term(self, f, term, doc_id, k1=1.2, b=0.75):
        tf = len(self.postings[f].get(term, {}).get(doc_id, []))
        if tf == 0:
            return 0.0
        norm = k1 * (1 - b + b * self.doc_len[f][doc_id] / self.avgdl(f))
        return self.idf(f, term) * tf * (k1 + 1) / (tf + norm)

    def search(self, query, boosts, k=5):
        terms = [t for t, _ in analyze(query)]
        scores = defaultdict(float)
        for f, boost in boosts.items():
            for term in terms:                       # OR semantics: any matching term scores
                for doc_id in self.postings[f].get(term, {}):
                    scores[doc_id] += boost * self.bm25_term(f, term, doc_id)
        return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:k]

    def phrase(self, f, phrase):
        """Docs where the analyzed terms appear at consecutive positions (stop-word gaps kept)."""
        toks = analyze(phrase)
        first, offsets = toks[0][0], [p - toks[0][1] for _, p in toks]
        hits = []
        for doc_id, positions in self.postings[f].get(first, {}).items():
            for p in positions:
                if all(p + off in self.postings[f].get(t, {}).get(doc_id, [])
                       for (t, _), off in zip(toks[1:], offsets[1:])):
                    hits.append(doc_id)
                    break
        return sorted(hits)

DOCS = {
    1: {"title": "Wireless noise cancelling headphones",
        "body": "Over-ear wireless headphones with active noise cancelling and a 30 hour battery."},
    2: {"title": "Wired studio headphones",
        "body": "Closed-back wired headphones for mixing and mastering in the studio."},
    3: {"title": "Portable Bluetooth speaker",
        "body": "Waterproof wireless speaker with deep bass. Pairs with phones and headphones."},
    4: {"title": "Noise cancelling wireless earbuds",
        "body": "True wireless earbuds with noise cancelling and a charging case."},
    5: {"title": "Headphone stand",
        "body": "Aluminum stand for headphones with a cable organizer."},
    6: {"title": "Wireless charging pad",
        "body": "Fast wireless charger for phones and earbuds. Charging cable included."},
    7: {"title": "Kids headphones",
        "body": "Volume-limited wired headphones for kids. Foldable, light, and less noise on long trips."},
    8: {"title": "Travel case for headphones and earbuds",
        "body": "Hard shell case that protects headphones, earbuds, cables and chargers on trips."},
}

if __name__ == "__main__":
    idx = InvertedIndex(["title", "body"])
    for doc_id, doc in DOCS.items():
        idx.add(doc_id, doc)

    print("analyze('Noise-Cancelling Headphones'):", analyze("Noise-Cancelling Headphones"))
    print("postings[body]['noise']:", dict(idx.postings["body"]["noise"]))
    print(f"N={idx.n_docs}  avgdl(title)={idx.avgdl('title'):.3f}  avgdl(body)={idx.avgdl('body'):.3f}")
    q = "wireless noise cancelling headphones"
    for f in ("title", "body"):
        row = {t: (len(idx.postings[f].get(t, {})), round(idx.idf(f, t), 4)) for t, _ in analyze(q)}
        print(f"df, idf in {f}:", row)
    print("\nBM25, body only:")
    for d, s in idx.search(q, {"body": 1.0}, k=8):
        print(f"  doc {d}: {s:.4f}  ({DOCS[d]['title']})")
    print("\nBM25, title^2 + body:")
    for d, s in idx.search(q, {"title": 2.0, "body": 1.0}, k=8):
        print(f"  doc {d}: {s:.4f}  ({DOCS[d]['title']})")
    print("\nterm 'noise' in body of doc 7:", round(idx.bm25_term("body", "noise", 7), 4),
          " len =", idx.doc_len["body"][7])
    print("term 'noise' in body of doc 4:", round(idx.bm25_term("body", "noise", 4), 4),
          " len =", idx.doc_len["body"][4])
    print("phrase 'noise cancelling' in body:", idx.phrase("body", "noise cancelling"))
    print("phrase 'cancelling noise' in body:", idx.phrase("body", "cancelling noise"))
