# Extracted from manuscript/book1-traditional/04-quantitative-foundations.md §4.9.3 (listing 2). Edit the manuscript, not this file.
import math

def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))

def norm(a):
    return math.sqrt(dot(a, a))

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

def matmul(A, B):
    """Naive matrix multiply: (m x k) times (k x n) -> (m x n)."""
    m, k, n = len(A), len(B), len(B[0])
    assert all(len(row) == k for row in A), "inner dimensions must match"
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(n)]
            for i in range(m)]

query = [1, 2, 2]
docs = {"doc_a": [2, 1, 2], "doc_b": [2, 4, 4], "doc_c": [-2, 1, 0]}
for name, vec in docs.items():
    print(f"{name}: dot = {dot(query, vec):3d}, cosine = {cosine_similarity(query, vec):.3f}")

# Score all documents at once: (1 x 3) query times (3 x 3) matrix of doc columns
D = [list(col) for col in zip(*docs.values())]   # 3 x 3, one document per column
print("scores via matmul:", matmul([query], D)[0])
