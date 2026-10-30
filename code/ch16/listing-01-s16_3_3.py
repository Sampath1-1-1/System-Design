# Extracted from manuscript/book1-traditional/16-search-systems.md §16.3.3 (listing 1). Edit the manuscript, not this file.
"""Intersect two sorted postings lists (AND query), with and without skip pointers,
counting comparisons. The skip version drives from the shorter list and calls advance(target),
the operation Lucene's postings iterators expose."""
import math
import random

def intersect_linear(a, b):
    """Textbook merge: step whichever pointer holds the smaller docID."""
    i = j = comparisons = 0
    out = []
    while i < len(a) and j < len(b):
        comparisons += 1
        if a[i] == b[j]:
            out.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out, comparisons

class SkipPostings:
    """A postings list with a skip pointer every `step` entries."""
    def __init__(self, doc_ids, step=None):
        self.ids = doc_ids
        self.step = step or max(1, int(math.sqrt(len(doc_ids))))
        self.pos = 0
        self.comparisons = 0

    def advance(self, target):
        """Move to the first docID >= target; return it (or None when exhausted)."""
        ids, s = self.ids, self.step
        nxt = (self.pos // s + 1) * s                    # next skip-pointer position
        while nxt < len(ids) and ids[nxt] <= target:     # follow skips while they do not overshoot
            self.comparisons += 1
            self.pos, nxt = nxt, nxt + s
        while self.pos < len(ids) and ids[self.pos] < target:   # then scan inside one block
            self.comparisons += 1
            self.pos += 1
        return ids[self.pos] if self.pos < len(ids) else None

def intersect_with_skips(short, long_list, step=None):
    it = SkipPostings(long_list, step)
    out = []
    for doc in short:                                    # drive from the rarer term
        it.comparisons += 1
        found = it.advance(doc)
        if found is None:
            break
        if found == doc:
            out.append(doc)
    return out, it.comparisons

if __name__ == "__main__":
    random.seed(7)
    N = 1_000_000
    common = sorted(random.sample(range(N), 200_000))   # e.g. "wireless": 20% of docs
    rare = sorted(random.sample(range(N), 1_000))       # e.g. "anc": 0.1% of docs
    r1, c1 = intersect_linear(common, rare)
    assert r1 == sorted(set(common) & set(rare))
    print(f"matches={len(r1)}  linear merge: {c1:,} comparisons")
    for step in (447, 128, 20):                       # sqrt(L), Lucene's block size, sqrt(2L/m)
        r2, c2 = intersect_with_skips(rare, common, step)
        assert r2 == r1
        print(f"skip every {step:>3}: {c2:>7,} comparisons  ({c1 / c2:.0f}x fewer)")
