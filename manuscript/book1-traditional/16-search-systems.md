# Chapter 16 — Search Systems

> **Level:** 3 · **Track:** A (Traditional) · **Estimated reading time:** 5 h

Type "wireless noise cancelling headphones" into an online store and, within about a tenth of a second, a ranked list of products comes back from a catalog of tens of millions of items. None of the database machinery from Chapters 11–14 can do this directly. A B-tree index (§11.8) finds rows whose key *equals* or *starts with* a value. A `WHERE description LIKE '%noise%'` clause cannot use that index at all, so the database reads every row. Even if it could find the matching rows quickly, it would have no notion of which match is *best*.

Search systems solve three problems that ordinary databases do not:

1. **Finding documents by the words inside them**, quickly, across billions of words. The answer is the **inverted index** (§16.3), together with the text analysis that decides what counts as a "word" (§16.4).
2. **Ordering matches by relevance**, so the most useful result comes first. The answer is a scoring function, today usually **BM25** (§16.5).
3. **Doing both at scale and in near real time**, while documents are being added, changed and deleted. The answer is immutable index segments that are merged in the background (§16.6), partitioned and replicated across nodes (§16.7). Elasticsearch and OpenSearch package all of this (§16.8), and an indexing pipeline keeps the index in step with the source of truth (§16.10).

Autocomplete (§16.9) is a special case with a latency budget so tight that it gets its own data structures. The chapter ends with a short bridge to semantic and hybrid retrieval (§16.11), treated in depth in Chapters 74 and 75.

A brief historical note shows how stable these ideas are. Brin and Page's 1998 description of the Google prototype already had a forward index, an inverted index stored as "barrels" partitioned by word ID, hit lists recording word positions and formatting, and a ranking function that combined text-match scores with PageRank [Brin and Page 1998]. A modern Elasticsearch cluster contains recognizable descendants of every one of those parts.

The running example is a product search service for an online electronics store. Figure 16.1 shows its two halves: an indexing path that turns documents into an index, and a query path that turns a query into a ranked list.

**Figure 16.1 — The two paths of a search system.**

```mermaid
flowchart LR
  subgraph Indexing path
    SRC[(Product database)] -.->|CDC events| K[[Kafka topic]]
    K -.->|consume| IX[Indexer service]
    IX -->|analyze + bulk write| IDX[(Inverted index segments)]
  end
  subgraph Query path
    U([Shopper]) -->|HTTPS query| API[Search API]
    API -->|analyze query| QP[Query planner]
    QP -->|postings lookup| IDX
    IDX -->|candidate docs| RK[BM25 ranker + top-k]
    RK -->|ranked IDs + snippets| API
  end
```

**Reading the diagram.** The left subgraph is the **indexing path**. The product database is the source of truth; change data capture (CDC) publishes every insert, update and delete as an event to a Kafka topic. Those dotted arrows are asynchronous: the shopper never waits for them. The indexer consumes events, runs text analysis and writes to the index in bulk. The right subgraph is the **query path**, which is synchronous (solid arrows) from the shopper's HTTPS request to the ranked response. The query is analyzed with the *same* rules as the documents, the planner looks up postings lists, and the ranker scores candidates and keeps the top *k*. There are two storage boundaries, the product database and the index, and they are eventually consistent with each other; the lag between them is the **freshness** of search (§16.10). Failure points: if Kafka or the indexer stalls, search keeps serving but grows stale; if the index is unavailable, search fails even though the database is healthy. The two paths scale independently: indexing by adding partitions and indexer consumers, querying by adding replicas (§16.7).

## 16.1 Learning objectives

After this chapter you should be able to:

- Explain how an inverted index, postings lists, positions and skip pointers answer keyword, Boolean and phrase queries, and estimate an index's size with delta and variable-byte compression.
- Design an analysis chain (tokenizer, lowercasing, stemming or lemmatization, stop words, n-grams, synonyms) and predict how each choice changes recall, precision and index size.
- Compute TF-IDF and BM25 scores by hand, explain the roles of $k_1$ and $b$, and apply field boosting.
- Describe how Lucene builds indexes from immutable segments, handles deletes with tombstones, and merges segments, and estimate merge write amplification.
- Compare document and term partitioning, compute scatter–gather tail latency, and explain query-then-fetch, deep-pagination cost and the global-versus-local IDF problem.
- Describe the Elasticsearch/OpenSearch cluster model: node roles, shards, replicas, the translog, refresh, flush and near-real-time search.
- Design an autocomplete service with a trie or FST holding precomputed top-*k* completions and meet a 100 ms end-to-end budget.
- Build a near-real-time indexing pipeline with CDC and Kafka, and reason about its freshness latency and refresh-interval trade-offs.

## 16.2 Prerequisites

- B-trees and secondary indexes — §11.7–§11.8 (the inverted index is a different answer to the same "avoid a full scan" problem).
- Log-structured storage, LSM trees and compaction — §13.7–§13.9 (Lucene segments are an LSM-like design; this chapter cross-references rather than repeats).
- Partitioning and replication — §14.3 and §14.6–§14.7 (search clusters apply them to indexes).
- Percentiles and fan-out amplification — §4.8 (scatter–gather latency builds directly on $p^N$).
- Logarithms — §4.4 (IDF and merge-tier arithmetic use them).
- Tries — §17.11 gives the data structure; this chapter applies it to autocomplete.
- Python 3.10 or later to run the listings; all use only the standard library.

## 16.3 Inverted indexes

### 16.3.1 From the index at the back of a book to an inverted index

::: definition
**Definition — Inverted index.** A mapping from each distinct **term** (a normalized word or token) to a **postings list**: the sorted list of identifiers of the documents that contain the term, optionally with the term's frequency and positions in each document. The set of all terms is the **dictionary** (or **vocabulary**, or **lexicon**).
:::

#### First-principles explanation

Open a textbook at the back. The index lists "Bloom filter … 211, 340, 512". Nobody reads the whole book to find Bloom filters; you look up the word and jump to the pages. The book's body maps *page → words*. The index at the back is that mapping turned inside out: *word → pages*. That is all an inverted index is. The "forward" direction (document → terms) is how documents are written; the "inverted" direction (term → documents) is how they are searched.

Three refinements turn the book index into a search engine index. First, each page number becomes a **document identifier (docID)**, a small integer. Second, the list for each word is kept **sorted** by docID, which makes combining lists cheap. Third, each entry can carry extra data: how often the word occurs in the document (**term frequency**, tf) and where (**positions**), so the engine can rank documents and match phrases.

#### Why does this exist?

Consider answering "documents containing *noise* and *headphones*" by scanning. A catalog of 100 million documents averaging 2.4 KB of text is 240 GB. Reading 240 GB at a generous 10 GB/s of memory bandwidth takes 24 s per query on one core, before any matching work. An inverted index instead reads two postings lists. If *noise* appears in 1 million documents and *headphones* in 100,000, the engine touches about 1.1 million entries; at roughly 2.4 bytes per compressed entry (§16.3.5) that is about 2.6 MB, read in well under a millisecond. The index trades storage and indexing work for a 10,000-fold reduction in query work.

#### How it works internally

1. **Analyze** each document into a stream of terms with positions (§16.4).
2. **Assign** the document a docID. Lucene assigns docIDs in insertion order within each segment, so postings lists are naturally sorted (§16.6).
3. **Append** the docID (with tf and positions) to the postings list of each distinct term in the document.
4. **Store** the dictionary in a structure that supports fast exact lookup and prefix ranges: a sorted array with binary search, a B-tree, a hash table, or in Lucene a block tree whose index is a finite-state transducer (FST) (§16.9.3).
5. **Compress** postings lists (§16.3.4) and write them sequentially to disk.

#### Architecture diagram

**Figure 16.2 — Dictionary, postings lists and positions.**

```mermaid
flowchart LR
  subgraph Dictionary
    T1["cancelling<br/>df=2"]
    T2["headphone<br/>df=6"]
    T3["noise<br/>df=3"]
    T4["wireless<br/>df=4"]
  end
  subgraph Postings lists
    P1["1 → pos 7<br/>4 → pos 5"]
    P2["1, 2, 3, 5, 7, 8<br/>with tf and positions"]
    P3["1 → pos 6<br/>4 → pos 4<br/>7 → pos 10"]
    P4["1, 3, 4, 6<br/>with tf and positions"]
  end
  T1 --> P1
  T2 --> P2
  T3 --> P3
  T4 --> P4
  P1 -.->|docID| DS[(Stored documents)]
  P3 -.->|docID| DS
```

**Reading the diagram.** The left subgraph is the dictionary: one entry per distinct term with its **document frequency** (df, the number of documents containing it). Each solid arrow is a pointer, in practice a file offset, from a dictionary entry to its postings list. The right subgraph shows postings for the body field of this chapter's eight-product example (§16.5.4): *noise* occurs in documents 1, 4 and 7, at positions 6, 4 and 10. The dotted arrows show the last step of a query: docIDs are turned into displayable results by fetching stored fields, a separate storage structure. The dictionary is small and usually memory-resident; postings are large and read sequentially; stored documents are read only for the final top results. Failure points are corruption of any of the three structures, which is why Lucene checksums every file. Scaling is by partitioning documents across shards, each with its own complete dictionary and postings (§16.7).

### 16.3.2 Query evaluation with postings lists

Because postings are sorted, Boolean operators become list operations:

- **AND** (*noise* AND *wireless*) is an **intersection**: walk both lists in step, advancing whichever pointer holds the smaller docID, and output docIDs found in both. Cost is $O(L_1 + L_2)$ for lists of lengths $L_1$ and $L_2$.
- **OR** is a **union**, also a linear merge. Ranked retrieval is usually OR-like: any document containing any query term is a candidate and scoring sorts them out.
- **NOT** is a difference: output docIDs in the first list that are not in the second.
- A **phrase query** ("noise cancelling") first intersects the lists, then checks positions: a document matches only if *cancelling* occurs at position $p+1$ for some position $p$ of *noise*. Positional data typically makes the index two to four times larger, which is why some fields are indexed without positions (in Elasticsearch, `index_options: docs` or `freqs`).

An evaluation trick that pays off everywhere: process the **rarest term first**. The intersection can never be larger than the shortest list, so starting there keeps intermediate results small.

### 16.3.3 Skip pointers

Intersecting a list of 200,000 docIDs with one of 1,000 by linear merge costs about 200,000 comparisons, almost all of them spent stepping through the long list past docIDs that cannot match. **Skip pointers** are shortcuts stored every $s$ entries of a postings list: "the entry $s$ positions ahead holds docID $X$". When the target docID is beyond $X$, the iterator jumps $s$ entries at once.

Lucene exposes this as an iterator operation, `advance(target)`: move to the first docID $\geq$ target. Its postings formats store multi-level skip data so `advance` can take long jumps, then shorter ones, then scan within one compressed block [Lucene Docs: postings format]. The skip interval trades jump distance against scan length. Manning et al. suggest $\sqrt{L}$ for a list of length $L$ [Manning et al. 2008, §2.3], but that heuristic assumes lists of similar length. When a short list of $m$ targets drives a long list of length $L$, the total cost is roughly $L/s$ skip-follows plus $m \cdot s/2$ in-block steps, minimized at $s = \sqrt{2L/m}$.

```python
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
```

Output (Python 3.13):

```text
matches=184  linear merge: 200,611 comparisons
skip every 447: 121,210 comparisons  (2x fewer)
skip every 128:  53,587 comparisons  (4x fewer)
skip every  20:  20,909 comparisons  (10x fewer)
```

What to notice:

- The intersection is **driven by the rare list**: 1,000 calls to `advance`, not 200,000 steps.
- The $\sqrt{L} = 447$ heuristic helps only 2× here because each `advance` then scans about 224 entries inside a block. Spacing tuned to the list-length ratio, $\sqrt{2 \times 200{,}000 / 1{,}000} = 20$, gives 10×. Multi-level skip lists, as in Lucene, get coarse and fine jumps without choosing one spacing.
- In a real engine the bigger win is not comparisons but **decoding**: a skipped block of compressed postings is never decompressed at all.

### 16.3.4 Compression: delta encoding and variable-byte codes

A docID stored as a 32-bit integer costs 4 bytes. Postings lists hold one entry per (term, document) pair, so they dominate index size. Two observations make them highly compressible.

**Delta (gap) encoding.** A sorted list such as 824, 829, 215406 can be stored as its first value followed by differences: 824, 5, 214577. A frequent term has small gaps (a term in 20% of documents has an average gap of 5), and small numbers need few bits. Rare terms have large gaps but short lists, so they contribute little to total size.

**Variable-byte (VByte) codes.** Encode each gap in as many bytes as it needs, using 7 data bits per byte and the eighth bit as a flag. In Lucene's `VInt` convention the low-order 7 bits come first and a high bit of 1 means "more bytes follow" [Lucene Docs: DataOutput.writeVInt]. Manning et al. describe the same code with the flag set on the *last* byte instead [Manning et al. 2008, §5.3.1]; the two are equivalent in size.

::: formula
**Variable-byte length of an integer**

$$\text{bytes}(g) = \max\!\left(1, \left\lceil \frac{\lfloor \log_2 g \rfloor + 1}{7} \right\rceil\right)$$

| Symbol | Meaning | Units |
|---|---|---|
| $g$ | The integer to encode, here a docID gap ($g \geq 1$) | count |
| $\lfloor \log_2 g \rfloor + 1$ | Number of significant bits in $g$ | bits |
| $\text{bytes}(g)$ | Encoded length, 7 payload bits per byte | bytes |
:::

**Table 16.1 — Variable-byte length by gap size.**

| Gap range | Significant bits | VByte bytes | Saving versus 4-byte integer |
|---|---|---|---|
| 1–127 | 1–7 | 1 | 75% |
| 128–16,383 | 8–14 | 2 | 50% |
| 16,384–2,097,151 | 15–21 | 3 | 25% |
| 2,097,152–268,435,455 | 22–28 | 4 | 0% |

::: example
**Worked example — encoding 824, 829, 215406.**

1. Gaps: 824, 829 − 824 = 5, 215406 − 829 = 214577.
2. 824 has 10 significant bits (512 ≤ 824 < 1024), so $\lceil 10/7 \rceil = 2$ bytes. Split into 7-bit groups: $824 = 6 \times 128 + 56$. Low group first with the continuation bit set: $56 + 128 = 184$ = `10111000`; then `00000110` (6, no continuation).
3. 5 fits in one byte: `00000101`.
4. 214577 has 18 bits ($2^{17} = 131072 \leq 214577 < 262144$), so 3 bytes. $214577 = 13 \times 16384 + 12 \times 128 + 49$, giving `10110001` (49 + 128), `10001100` (12 + 128), `00001101` (13).
5. Total: 6 bytes instead of 12.

**Interpretation.** Half the space is saved even on this tiny list, and the saving grows for frequent terms, whose gaps fit in one byte. **Engineering implication.** Postings for common terms (the ones that make queries slow) are also the ones that compress best, so compression reduces both disk and I/O on the hot path.
:::

The listing below implements delta + VByte, checks the worked example, and measures the average bytes per posting on a synthetic collection of 200,000 documents whose term document frequencies follow Zipf's law (a few very common terms, a long tail of rare ones).

```python
"""Delta (gap) encoding + variable-byte (VByte) compression of a postings list,
and a measurement of bytes per posting on a synthetic Zipf-distributed collection."""
import random

def vbyte_encode(n):
    """Lucene-style VInt: 7 data bits per byte, low-order group first,
    high bit = 1 means 'more bytes follow'."""
    out = bytearray()
    while n >= 0x80:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    out.append(n)
    return bytes(out)

def vbyte_decode_all(data):
    nums, n, shift = [], 0, 0
    for byte in data:
        n |= (byte & 0x7F) << shift
        if byte & 0x80:
            shift += 7
        else:
            nums.append(n)
            n, shift = 0, 0
    return nums

def compress_postings(doc_ids):
    gaps = [doc_ids[0]] + [b - a for a, b in zip(doc_ids, doc_ids[1:])]
    return b"".join(vbyte_encode(g) for g in gaps)

def decompress_postings(data):
    doc_ids, total = [], 0
    for gap in vbyte_decode_all(data):
        total += gap
        doc_ids.append(total)
    return doc_ids

if __name__ == "__main__":
    ids = [824, 829, 215406]            # the example used in Manning et al. (2008), ch. 5
    blob = compress_postings(ids)
    print("gaps:", [ids[0]] + [b - a for a, b in zip(ids, ids[1:])])
    print("bytes:", " ".join(f"{b:08b}" for b in blob), f"({len(blob)} bytes vs {4*len(ids)} raw)")
    assert decompress_postings(blob) == ids

    # Synthetic collection: N docs, vocabulary with Zipfian document frequencies.
    random.seed(16)
    N, M, total_postings_target = 200_000, 50_000, 10_000_000
    weights = [1 / r for r in range(1, M + 1)]                 # Zipf, exponent 1
    scale = total_postings_target / sum(weights)
    raw_bytes = vb_bytes = postings = 0
    for w in weights:
        df = max(1, min(N, int(w * scale)))
        doc_ids = sorted(random.sample(range(N), df))
        vb_bytes += len(compress_postings(doc_ids))
        raw_bytes += 4 * df
        postings += df
    print(f"postings={postings:,}  raw={raw_bytes/1e6:.1f} MB  vbyte={vb_bytes/1e6:.1f} MB  "
          f"bytes/posting={vb_bytes/postings:.2f}  ratio={vb_bytes/raw_bytes:.2f}")
```

Output (about 7 s):

```text
gaps: [824, 5, 214577]
bytes: 10111000 00000110 00000101 10110001 10001100 00001101 (6 bytes vs 12 raw)
postings=8,946,910  raw=35.8 MB  vbyte=12.5 MB  bytes/posting=1.39  ratio=0.35
```

What to notice:

- Decoding is a loop of shifts and masks with a data-dependent branch per byte. That branch is why production engines moved to **block** codes.
- On the Zipfian collection, docID postings shrink to **1.39 bytes each**, 35% of their raw size. Manning et al. report the same order for the Reuters RCV1 collection: about 100 million postings take 400 MB as 32-bit integers and 116 MB with variable-byte gaps [Manning et al. 2008, Table 5.6].

Production engines go further. Lucene's postings formats (from Lucene 5 through at least Lucene 9) group docID deltas and frequencies into blocks of 128 values and store each block with **frame-of-reference bit packing**: find the largest value in the block, use exactly that many bits for every value, and decode the block with branch-free code; leftover values at the end of a list use VInt [Lucene Docs: postings format]. Bit-packed blocks decode several times faster than VByte, especially with SIMD instructions [Lemire and Boytsov 2015]. Zobel and Moffat survey the family of codes (Elias gamma and delta, Golomb, VByte) and the trade-off between compression ratio and decoding speed [Zobel and Moffat 2006].

### 16.3.5 Estimating index size

::: formula
**Inverted index size (one copy)**

$$S_{\text{index}} \approx \underbrace{N \cdot u \cdot (b_d + b_f)}_{\text{docIDs + frequencies}} + \underbrace{N \cdot L \cdot b_p}_{\text{positions}} + \underbrace{M \cdot b_t}_{\text{dictionary}}$$

| Symbol | Meaning | Units |
|---|---|---|
| $N$ | Number of documents | documents |
| $u$ | Average number of *distinct* terms per document (postings per document) | postings/document |
| $L$ | Average number of tokens per document (one position each) | tokens/document |
| $b_d$, $b_f$ | Compressed bytes per docID gap and per term frequency | bytes |
| $b_p$ | Compressed bytes per position gap | bytes |
| $M$ | Number of distinct terms in the collection | terms |
| $b_t$ | Dictionary bytes per term (term text + pointers + statistics) | bytes |
:::

::: example
**Worked example — 100 million product and review documents.** Assume $N = 10^8$, $L = 400$ tokens, $u = 200$ distinct terms per document, $M = 5 \times 10^7$ distinct terms (part numbers and misspellings make vocabularies large), $b_d = 1.4$ bytes (measured above), $b_f = 1$ byte, $b_p = 1.5$ bytes, $b_t = 20$ bytes. Sizes in SI units (1 GB = $10^9$ bytes).

1. Postings: $N \cdot u = 10^8 \times 200 = 2 \times 10^{10}$.
2. DocIDs and frequencies: $2 \times 10^{10} \times (1.4 + 1) = 4.8 \times 10^{10}$ bytes = 48 GB.
3. Positions: $N \cdot L = 4 \times 10^{10}$ tokens × 1.5 bytes = $6 \times 10^{10}$ bytes = 60 GB.
4. Dictionary: $5 \times 10^7 \times 20 = 10^9$ bytes = 1 GB.
5. Total inverted index ≈ 48 + 60 + 1 = **109 GB**.
6. Uncompressed for comparison (4-byte docID, tf and position): $2 \times 10^{10} \times 8 + 4 \times 10^{10} \times 4 = 160 + 160 = 320$ GB, about 3× larger.
7. The raw text is $4 \times 10^{10}$ tokens × about 6 bytes = 240 GB, so the positional index is about 45% of the text and the non-positional part about 20%.

**Interpretation.** Positions cost more than docIDs and frequencies combined. **Engineering implication.** The index is only part of the footprint. Elasticsearch also keeps the original JSON (`_source`, compressed), **doc values** (a column store for sorting and aggregations), and **norms** (per-field length factors). Budget roughly the index again for these, then multiply by $1 + r$ for $r$ replicas. With one replica this catalog needs on the order of $2 \times (109 + 110) \approx 440$ GB of disk before headroom for merges (§16.6). Dropping positions on fields never used in phrase queries is the single largest saving available.
:::

#### Real-world industry applications

::: industry
**Early Google: barrels and hit lists.** Brin and Page's prototype stored a forward index partitioned into 64 "barrels" by word ID, then sorted each barrel by word ID to produce the inverted index. Each posting carried a "hit list" of positions encoded compactly, with font size and capitalization squeezed into two bytes per hit, and "fancy" hits for anchor text and titles kept separately so that a query could first consult the short, high-value lists [Brin and Page 1998]. The design choice of storing a small, high-signal subset of postings separately reappears today as field-specific indexes and tiered indexes.
*Evidence: Primary* — [Brin and Page 1998]
:::

#### Failure scenarios

**Table 16.2 — Inverted index failure scenarios.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| Query on a common term is slow | Postings list of tens of millions of entries is fully decoded and scored | Slow-query log; per-term latency | Add top-*k* pruning (§16.5.6); cache results | Block-max skipping; avoid stop-word-only queries on huge fields |
| Index far larger than estimated | Positions and n-gram fields indexed everywhere | Per-field disk usage API | Reindex with `index_options: freqs` where phrases are unused | Review mappings before launch |
| Corrupted segment after disk fault | Bit rot or torn write | Checksum mismatch on open | Recover shard from a replica or snapshot | Replicas on separate failure domains; checksums (Lucene has them) |

#### Common misconceptions

::: mistake
**Mistake — "An inverted index is just a secondary index on a text column."** A B-tree secondary index maps one value per row to rows; an inverted index maps *many* terms per document to documents, keeps term statistics for ranking, stores positions for phrases, and is built and compressed in bulk. The data structures, update patterns and costs are different, which is why relational databases ship separate full-text index types (PostgreSQL's GIN, for example) rather than reusing B-trees.
:::

## 16.4 Tokenization and analysis

### 16.4.1 The analysis chain

::: definition
**Definition — Analysis.** The process that converts raw text into the terms stored in (or looked up from) an inverted index. An **analyzer** is a pipeline of zero or more **character filters** (rewrite the raw character stream), exactly one **tokenizer** (split the stream into tokens with positions and offsets) and zero or more **token filters** (modify, remove or add tokens).
:::

#### First-principles explanation

An inverted index matches terms *exactly*: the bytes `Headphones` and `headphone` are different keys. A shopper does not care. Analysis is the set of decisions about which strings should be treated as "the same word". A librarian who files "Colour", "color" and "COLORS" under one card is doing analysis by hand.

Every decision moves the balance between two quality measures. **Recall** is the fraction of relevant documents that are returned; **precision** is the fraction of returned documents that are relevant. Aggressive normalization (stemming, synonyms, folding accents) raises recall and risks precision: "university" and "universe" both stem to "univers" under the Porter stemmer. Conservative analysis does the opposite.

#### How it works internally

**Figure 16.3 — An analysis chain applied at index time and at query time.**

```mermaid
flowchart LR
  D(["Doc: Noise-Cancelling<br/>Headphones and Earbuds"]) --> CF[Char filters<br/>strip HTML, map chars]
  Q(["Query: noise cancelling<br/>headphone"]) --> CF2[Same char filters]
  CF --> TK[Tokenizer<br/>Unicode word boundaries]
  CF2 --> TK2[Same tokenizer]
  TK --> TF[Token filters<br/>lowercase, stop, stem]
  TK2 --> TF2[Same token filters<br/>+ query synonyms]
  TF -->|terms + positions| IDX[(Inverted index)]
  TF2 -->|term lookups| IDX
```

**Reading the diagram.** Two inputs enter the same pipeline: a document at index time (top) and a query at search time (bottom). Character filters run first on raw text (stripping HTML, mapping "&" to "and"); the tokenizer then splits text into tokens with positions; token filters normalize them. The index stores terms with positions; the query side only looks terms up. All steps are synchronous, in-process transformations; the only storage boundary is the index. The critical failure point is **asymmetry**: if the two pipelines diverge, for example because the index was built with stemming and the query analyzer was changed later, queries look up terms that were never stored and silently return nothing. Changing index-time analysis therefore requires a full reindex (§16.10.4); query-time-only filters such as synonyms can change without one. Analysis is CPU-bound and scales with indexer nodes.

Running the chapter's analyzer (listing in §16.5.4) on "Noise-Cancelling Headphones" yields `noise@0`, `cancelling@1`, `headphone@2`: the hyphen splits tokens, lowercasing normalizes case, and a minimal stemmer strips the plural.

**Table 16.3 — Analysis chain components and their trade-offs.**

| Component | Example | Raises | Risks |
|---|---|---|---|
| Char filter | Strip HTML; map "½" to "1/2" | Clean tokens | Losing meaningful symbols |
| Standard tokenizer | Unicode word boundaries (UAX #29) | Language-neutral splitting | "C++", "U.S.A.", "e-mail" split oddly |
| Lowercase | "Wi-Fi" → "wi", "fi" | Recall | "US" (country) vs "us" (pronoun) |
| ASCII folding | "café" → "cafe" | Recall for unaccented queries | Precision in languages where accents matter |
| Stop words | Drop "the", "of" | Index size, speed | Queries like "The Who", "to be or not to be" |
| Stemming | "running" → "run" | Recall | Over-stemming ("universe" ~ "university") |
| Synonyms | "tv" → "television" | Recall | Drift ("apple" fruit vs company) |
| Edge n-grams | "head" → h, he, hea, head | Prefix matching | Index 3–10× larger |

### 16.4.2 Tokenizers and normalization

A **whitespace tokenizer** splits on spaces and keeps punctuation attached ("headphones," with a comma). Lucene's **standard tokenizer** implements the Unicode word-break rules of UAX #29, which handle most European scripts sensibly. Specialized tokenizers exist for email addresses and URLs, for paths, and for keyword fields that must not be split at all (SKUs, user IDs, tags), where the whole value is one token.

Normalization also includes **Unicode normalization** (the character "é" can be one code point or "e" plus a combining accent; NFC/NFKC normalization makes them identical) and case folding. Normalization bugs are a classic source of "the product is in the index but search cannot find it".

### 16.4.3 Stemming versus lemmatization

**Stemming** chops suffixes by rule. The Porter stemmer [Porter 1980] applies several dozen suffix-rewriting rules in five steps and maps "connection", "connected" and "connecting" to "connect". The "S" stemmer removes only plural endings [Harman 1991]; Lucene ships it as a minimal English stemmer, and this chapter's code uses it. **Lemmatization** maps a word to its dictionary form (lemma) using a vocabulary and part-of-speech information: "better" → "good", "mice" → "mouse", "was" → "be".

**Table 16.4 — Stemming versus lemmatization.**

| | Stemming | Lemmatization |
|---|---|---|
| What it is | Rule-based suffix stripping | Dictionary + morphology lookup |
| Output | A stem, possibly not a word ("univers") | A real word (lemma) |
| Speed | Very fast, no dictionary | Slower; needs POS tagging for accuracy |
| Recall | High (aggressive) | High for irregular forms |
| Precision | Can conflate unrelated words | Better |
| Languages | Per-language rule sets (Snowball) | Needs a lexicon per language |
| Choose when | Large English corpora, speed matters | Morphologically rich languages, precision matters |

Manning et al. observe that stemming helps recall but hurts precision, and its net effect on English retrieval quality is modest; for languages with richer morphology (Finnish, Hungarian, Arabic) normalization matters much more [Manning et al. 2008, §2.2.4].

### 16.4.4 Stop words

**Stop words** are very frequent words such as "the", "a" and "of". Dropping them once saved significant space, because their postings lists are the longest in the index. Modern engines usually *keep* them: compression makes their lists cheap (gaps of 1–2 fit in a byte), BM25's IDF already gives them near-zero weight (§16.5.3), and dropping them breaks phrase queries and queries made mostly of stop words ("The Who", "To Be or Not to Be"). Elasticsearch's default standard analyzer does not remove stop words. If you do remove them, keep the position gaps (as this chapter's analyzer does) so phrase matching remains correct.

### 16.4.5 n-grams and edge n-grams

A **character n-gram** is a substring of length $n$. Indexing all trigrams of "headphone" (hea, ead, adp, dph, …) lets the engine match substrings, misspellings and languages without spaces. An **edge n-gram** keeps only prefixes (h, he, hea, head, …), which supports search-as-you-type (§16.9.4). Both multiply the number of postings: a word of length $\ell$ produces $\ell - n + 1$ n-grams, so a trigram field is several times larger than a word field and its postings lists for common grams are very long.

### 16.4.6 Synonyms

Synonyms map equivalent terms ("tv" ⇔ "television", "laptop" ⇔ "notebook"). Applying them at **index time** expands every document, which makes the index bigger and means a synonym change requires a reindex. Applying them at **query time** keeps the index unchanged and allows synonym lists to be updated without reindexing, at the cost of slightly more expensive queries. Multi-word synonyms ("ny" ⇔ "new york") need care: the expansion has different lengths, so Lucene represents it as a token *graph* and its synonym-graph filter is intended for query-time use. Most teams apply synonyms at query time.

### 16.4.7 Language issues

- **No word separators.** Chinese, Japanese and Thai text has no spaces. Options are dictionary-based segmenters (for example Lucene's Kuromoji for Japanese, or ICU's dictionary-based word breaking) or overlapping character bigrams, which need no dictionary but index more terms.
- **Compounds.** German writes "Kopfhörer" (headphones) and "Kopfhörerverstärker" (headphone amplifier) as single words; a decompounding filter splits them so that a query for "Kopfhörer" finds both.
- **Script and direction.** Arabic and Hebrew need normalization of letter variants and diacritics; Turkish has a dotted and dotless "i", so naive lowercasing is wrong.
- **Mixed-language catalogs.** Index each language into its own field with its own analyzer (`title.en`, `title.de`) and choose fields by detected or declared language, rather than forcing one analyzer onto all text.

An Elasticsearch analyzer is declared in the index settings and attached to fields in the mapping:

```json
{
  "settings": {
    "analysis": {
      "filter": {
        "product_synonyms": { "type": "synonym_graph", "synonyms": ["tv, television", "anc, noise cancelling"] }
      },
      "analyzer": {
        "product_index":  { "tokenizer": "standard", "filter": ["lowercase", "asciifolding", "porter_stem"] },
        "product_search": { "tokenizer": "standard", "filter": ["lowercase", "asciifolding", "product_synonyms", "porter_stem"] }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": { "type": "text", "analyzer": "product_index", "search_analyzer": "product_search" },
      "sku":   { "type": "keyword" }
    }
  }
}
```

What to notice: the index and search analyzers share tokenizer and normalization but the synonym graph is applied only at search time; `sku` is a `keyword` field, indexed as a single unanalyzed token for exact matching.

#### Real-world industry applications

::: industry
**GitHub code search.** Source code defeats word analyzers: users search for punctuation (`foo(`), want no stemming or stop-word removal, and use regular expressions. GitHub's engine (Blackbird, written in Rust) therefore indexes character n-grams and answers a query by intersecting the postings lists of the query's n-grams, then verifying candidate documents; GitHub reported an index of about 25 TB built from 115 TB of source content [Clem 2023]. Trade-off: n-gram postings are numerous and long, which GitHub offset by indexing each unique file content only once and by sharding.
*Evidence: Primary* — [Clem 2023]
:::

#### Failure scenarios

**Table 16.5 — Analysis failure scenarios.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| Known document not found | Index and query analyzers differ | `_analyze` API on both strings | Align analyzers; reindex | One analyzer definition shared by both sides; tests |
| Irrelevant matches after a release | Aggressive stemmer or bad synonym | Relevance test set regression | Roll back query-time synonyms | Offline relevance evaluation gate |
| Index size jumps 5× | n-gram filter added to a large field | Disk usage alert | Move n-grams to a dedicated subfield | Size test on a sample before deploy |

#### Common misconceptions

::: mistake
**Mistake — "Better analysis is always more normalization."** Every normalization merges distinct strings. For SKUs, error codes, names and code, normalization destroys meaning. Analyze each field according to how people search it, and keep an unanalyzed `keyword` subfield for exact matching.
:::

## 16.5 Ranking: TF-IDF and BM25

### 16.5.1 What a ranking function does

::: definition
**Definition — Relevance score.** A number computed for each (query, document) pair that estimates how well the document satisfies the query. A **ranking function** computes it; the engine returns the $k$ highest-scoring documents.
:::

#### First-principles explanation

Imagine asking a librarian for books about "noise cancelling headphones". A sensible librarian reasons in three steps. A book that mentions *noise cancelling* ten times is probably more on topic than one that mentions it once, but not ten times more (**term frequency, with diminishing returns**). The word *headphones* appears in half the catalog, so matching it says little, while *cancelling* is rare and therefore informative (**inverse document frequency**). And a one-page leaflet that mentions *noise* once is more focused than a 900-page encyclopedia that mentions it once (**length normalization**). BM25 is these three intuitions written as one formula.

The theoretical justification is the **probability ranking principle**: if documents are ranked by their probability of relevance to the query, the ranking is optimal for any measure that rewards putting relevant documents first [Robertson 1977]. BM25 approximates that probability from term statistics alone [Robertson and Zaragoza 2009].

### 16.5.2 TF-IDF

Karen Spärck Jones observed in 1972 that a term's value for retrieval falls as the number of documents containing it rises [Spärck Jones 1972]. Combined with term frequency, this gives the classic **TF-IDF** weight, the basis of the vector space model in which documents and queries are vectors of term weights compared by cosine similarity (§4.9.2).

::: formula
**TF-IDF weight of term $t$ in document $d$**

$$w_{t,d} = \text{tf}_{t,d} \times \log_{10}\frac{N}{\text{df}_t} \qquad \text{score}(q,d) = \sum_{t \in q} w_{t,d}$$

| Symbol | Meaning | Units |
|---|---|---|
| $\text{tf}_{t,d}$ | Occurrences of term $t$ in document $d$ | count |
| $N$ | Documents in the collection | documents |
| $\text{df}_t$ | Documents containing $t$ | documents |
| $w_{t,d}$ | Weight of $t$ in $d$ | dimensionless |
:::

::: example
**Worked example — TF-IDF on the product catalog.** The body field of the eight-product catalog (§16.5.4) has $N = 8$. *noise* occurs in 3 documents and *headphone* in 6.

1. $\text{idf}(\textit{noise}) = \log_{10}(8/3) = \log_{10} 2.667 = 0.426$.
2. $\text{idf}(\textit{headphone}) = \log_{10}(8/6) = 0.125$.
3. A document containing *noise* once scores 0.426 for that term; one containing *noise* 10 times scores 4.26.

**Interpretation.** IDF makes *noise* 3.4× more valuable than *headphone*, as intended. But raw tf grows without limit, so a spammy description repeating "noise" ten times beats an accurate one, and nothing corrects for document length. **Engineering implication.** Lucene used a TF-IDF variant (with $\sqrt{\text{tf}}$ and length factors) as its default until Elasticsearch 5.0 and Lucene 6 switched to BM25 [Elastic Docs: similarity].
:::

### 16.5.3 BM25

**BM25** ("Best Matching 25", the 25th weighting scheme in the Okapi experiments at City University London) comes from the probabilistic relevance framework [Robertson and Zaragoza 2009]. It keeps IDF, makes term frequency **saturate**, and normalizes by document length relative to the average.

::: formula
**BM25 inverse document frequency (Lucene form)**

$$\text{IDF}(t) = \ln\!\left(1 + \frac{N - n_t + 0.5}{n_t + 0.5}\right)$$

| Symbol | Meaning | Units |
|---|---|---|
| $N$ | Documents in the collection (or shard; see §16.7.5) | documents |
| $n_t$ | Documents containing term $t$ (document frequency) | documents |
| $\text{IDF}(t)$ | Weight of a match on $t$ | dimensionless |
:::

The classic Robertson–Spärck Jones form, $\ln\frac{N - n_t + 0.5}{n_t + 0.5}$, becomes *negative* for terms in more than half the documents; Lucene adds 1 inside the logarithm so that every match contributes a small positive amount.

::: formula
**BM25 score**

$$\text{score}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f_{t,d}\,(k_1 + 1)}{f_{t,d} + k_1\left(1 - b + b \cdot \dfrac{|d|}{\text{avgdl}}\right)}$$

| Symbol | Meaning | Units |
|---|---|---|
| $f_{t,d}$ | Frequency of term $t$ in document (field) $d$ | count |
| $\lvert d \rvert$ | Length of $d$ in terms after analysis | terms |
| $\text{avgdl}$ | Average length of that field across the collection | terms |
| $k_1$ | Term-frequency saturation parameter; Lucene default 1.2 (typical 1.2–2.0) | dimensionless |
| $b$ | Length-normalization strength, 0 (none) to 1 (full); default 0.75 | dimensionless |
| $\text{score}(q,d)$ | Relevance score; only comparable within one query | dimensionless |
:::

Two properties follow from the formula. As $f_{t,d} \to \infty$ the fraction approaches $k_1 + 1$, so a term can never contribute more than $(k_1 + 1) \cdot \text{IDF}$: repetition has diminishing returns. And the denominator grows with $|d|/\text{avgdl}$, so the same tf in a longer document scores less; $b$ controls how strongly.

**Table 16.6 — BM25 term-frequency factor ($k_1 = 1.2$, $b = 0.75$) versus raw tf.**

| tf | Raw TF-IDF factor | BM25 factor, $\lvert d \rvert = \text{avgdl}$ | BM25 factor at tf = 1 | Length |
|---|---|---|---|---|
| 1 | 1 | 1.000 | 1.257 | $\lvert d \rvert$ = 0.5 avgdl |
| 2 | 2 | 1.375 | 1.000 | $\lvert d \rvert$ = avgdl |
| 3 | 3 | 1.571 | 0.710 | $\lvert d \rvert$ = 2 avgdl |
| 5 | 5 | 1.774 | | |
| 10 | 10 | 1.964 | | |
| ∞ | ∞ | 2.200 | | |

The first three columns show saturation: going from 1 to 10 occurrences raises the BM25 factor by less than 2×, against 10× for raw tf. The last two columns show length normalization for a single occurrence.

::: example
**Worked example — BM25 for *noise* in two product descriptions.** From the catalog in §16.5.4: $N = 8$ body fields, $n_{\textit{noise}} = 3$, $\text{avgdl} = 68/8 = 8.5$ terms. Document 4 (earbuds) has $|d| = 7$; document 7 (kids' headphones) has $|d| = 12$. Each contains *noise* once. $k_1 = 1.2$, $b = 0.75$.

1. IDF: $\ln\!\left(1 + \frac{8 - 3 + 0.5}{3 + 0.5}\right) = \ln(1 + 1.5714) = \ln 2.5714 = 0.9445$.
2. Length factor, document 4: $k_1(1 - b + b \cdot 7/8.5) = 1.2 \times (0.25 + 0.6176) = 1.2 \times 0.8676 = 1.0412$.
3. TF part, document 4: $\frac{1 \times 2.2}{1 + 1.0412} = \frac{2.2}{2.0412} = 1.0778$.
4. Score, document 4: $0.9445 \times 1.0778 = 1.018$.
5. Length factor, document 7: $1.2 \times (0.25 + 0.75 \times 12/8.5) = 1.2 \times 1.3088 = 1.5706$; TF part $2.2 / 2.5706 = 0.8558$; score $0.9445 \times 0.8558 = 0.808$.
6. Saturation check for document 4: with tf = 2 the TF part would be $4.4 / 3.0412 = 1.447$, with tf = 5 it would be $11 / 6.0412 = 1.821$, never exceeding 2.2.

**Interpretation.** The same single mention of *noise* is worth 26% more in the short, focused earbuds description than in the longer kids' description, and repeating it five times would raise its weight by only 69%. The listing below reproduces 1.0179 and 0.8083. **Engineering implication.** BM25 resists keyword stuffing and long-document bias out of the box, which is why it is the default in Lucene, Elasticsearch, OpenSearch and Solr. Tune $k_1$ and $b$ per field only against a relevance test set; for very short fields such as titles, a lower $b$ is common because length differences carry little meaning.
:::

::: note
**Lucene's scores versus the textbook formula.** Lucene 8 removed the constant factor $(k_1 + 1)$ from the numerator because it does not change the ranking; Elasticsearch preserves the classic score values by applying the constant as a boost, which is why `explain` output in Elasticsearch shows a factor of 2.2 [Lucene MIGRATE notes for 8.0]. Lucene also stores document length in a lossy one-byte **norm**, so its scores differ slightly from exact arithmetic.
:::

### 16.5.4 A complete engine in one listing

The listing below implements the analysis chain of §16.4 (tokenize, lowercase, stop words keeping position gaps, S-stemmer), a positional inverted index over two fields, BM25 with per-field boosts, and phrase matching.

```python
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
```

Output:

```text
analyze('Noise-Cancelling Headphones'): [('noise', 0), ('cancelling', 1), ('headphone', 2)]
postings[body]['noise']: {1: [6], 4: [4], 7: [10]}
N=8  avgdl(title)=3.125  avgdl(body)=8.500
df, idf in title: {'wireless': (3, 0.9445), 'noise': (2, 1.2809), 'cancelling': (2, 1.2809), 'headphone': (5, 0.4925)}
df, idf in body: {'wireless': (4, 0.6931), 'noise': (3, 0.9445), 'cancelling': (2, 1.2809), 'headphone': (6, 0.3254)}

BM25, body only:
  doc 4: 3.1456  (Noise cancelling wireless earbuds)
  doc 1: 3.0255  (Wireless noise cancelling headphones)
  doc 7: 1.0868  (Kids headphones)
  doc 3: 1.0437  (Portable Bluetooth speaker)
  doc 6: 0.7102  (Wireless charging pad)
  doc 5: 0.3913  (Headphone stand)
  doc 2: 0.3507  (Wired studio headphones)
  doc 8: 0.2905  (Travel case for headphones and earbuds)

BM25, title^2 + body:
  doc 1: 10.2012  (Wireless noise cancelling headphones)
  doc 4: 9.4376  (Noise cancelling wireless earbuds)
  doc 6: 2.6306  (Wireless charging pad)
  doc 7: 2.2419  (Kids headphones)
  doc 5: 1.5464  (Headphone stand)
  doc 2: 1.3521  (Wired studio headphones)
  doc 8: 1.1742  (Travel case for headphones and earbuds)
  doc 3: 1.0437  (Portable Bluetooth speaker)

term 'noise' in body of doc 7: 0.8083  len = 12
term 'noise' in body of doc 4: 1.0179  len = 7
phrase 'noise cancelling' in body: [1, 4]
phrase 'cancelling noise' in body: []
```

What to notice:

- **Body-only BM25 ranks the earbuds above the headphones** that exactly match the query. Document 4's description is shorter (7 terms versus 10), and *headphone* is so common (in 6 of 8 bodies, IDF 0.33) that matching it barely helps. Lexical scoring has no idea that headphones are what the shopper wants.
- **Boosting the title field 2×** fixes the order: the title "Wireless noise cancelling headphones" matches all four terms, adding $2 \times 3.588 = 7.18$ to document 1. Field structure is one of the strongest relevance signals available.
- The stop word "with" was removed, but positions were kept, so *noise* in document 4 is at position 4, not 3; phrase queries stay correct, and word order matters ("cancelling noise" matches nothing).
- A real engine never scores every matching document this way; see §16.5.6.

### 16.5.5 Field boosting and beyond

Field boosting multiplies each field's score by a weight, as in Elasticsearch's `multi_match` query with `"fields": ["title^2", "body"]`. Summing per-field BM25 scores is simple but statistically awkward: each field has its own IDF and saturation, so a term that appears in both title and body is counted twice. **BM25F** instead combines weighted term frequencies across fields *before* saturation, treating the document as one weighted bag of words [Robertson et al. 2004]; Elasticsearch's `combined_fields` query follows this approach.

Text relevance is rarely the whole ranking. Product search adds popularity, price, stock, margin and personalization; web search added link analysis such as PageRank [Brin and Page 1998]. Two common patterns are **function scoring** (multiply or add a numeric signal, for example $\log(1 + \text{sales})$) and **learning to rank**, where BM25 retrieves a few hundred candidates and a trained model reorders them using many features (Chapter 81 covers ranking models).

### 16.5.6 Retrieving the top *k* efficiently

Scoring every document that matches any query term is wasteful: an OR query containing *headphone* may match millions of documents, but the user sees ten. Because each term's contribution is bounded by $(k_1 + 1)\cdot\text{IDF}(t)$, an engine can compute an upper bound on any document's score and skip documents that cannot beat the current $k$-th best score. **WAND** and its refinement **Block-Max WAND** store the maximum score per postings block and skip whole blocks [Ding and Suel 2011]. Lucene 8 added block-max WAND, and Elasticsearch 7 accordingly stopped counting total hits exactly by default (`track_total_hits` defaults to 10,000), since an exact count would force every match to be visited [Elastic Docs: track_total_hits].

**Figure 16.4 — Ranked query pipeline inside one shard.**

```mermaid
flowchart LR
  Q([Analyzed query terms]) --> IT[Postings iterators<br/>one per term]
  IT -->|advance with<br/>block max scores| WAND{Can doc beat<br/>k-th best score?}
  WAND -->|no: skip block| IT
  WAND -->|yes| SC[Compute BM25<br/>+ field boosts]
  SC --> HEAP[(Top-k min-heap)]
  HEAP -->|k best docIDs| RR[Optional rescoring<br/>of top candidates]
  RR --> OUT([Shard result])
```

**Reading the diagram.** Each query term opens an iterator over its postings list. Before fully scoring a candidate, the WAND decision compares the sum of per-block maximum scores with the score of the current $k$-th best document held in a min-heap; if the bound is too low, whole blocks are skipped (the loop back to the iterators). Survivors are scored exactly and offered to the heap, an in-memory structure of size $k$. An optional rescoring stage applies more expensive signals (phrase proximity, a learned model) to only the top few hundred. All steps are synchronous and CPU-bound within one shard; the storage boundary is the postings files, usually served from the operating system page cache. Failure points are queries whose terms are all very common (little skipping possible) and very large $k$ (deep pagination, §16.7.4). Scaling is by splitting the index into more shards, each running this pipeline in parallel.

#### Real-world industry applications

::: industry
**Wikipedia's CirrusSearch.** Wikimedia runs on-wiki search for Wikipedia and its sister projects with CirrusSearch, a MediaWiki extension backed by Elasticsearch. Pages are indexed with per-language analysis chains, and ranking combines text relevance with signals such as incoming links and page popularity, with rescoring profiles configurable per wiki [MediaWiki: CirrusSearch].
*Evidence: Primary* — [MediaWiki: CirrusSearch]
:::

#### Failure scenarios

**Table 16.7 — Ranking failure scenarios.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| Accessories outrank the product searched for | Text match ignores intent; short bodies win | Click-through and relevance judgments | Boost title; add category signals | Offline evaluation set (NDCG) |
| Scores jump between identical requests | Different replicas have different deleted-doc counts, so different statistics | Compare `explain` across replicas | Use preference strings for session stickiness | Accept small variance; merge away deletes |
| Keyword stuffing by sellers | Unbounded tf in a custom scorer | Manual review, anomaly scores | Switch to BM25; cap field length | BM25 saturation; quality signals |

#### Common misconceptions

::: mistake
**Mistake — "A BM25 score of 12 means a better match than a score of 6 on another query."** BM25 scores depend on the query's terms, their IDF and the collection statistics. They rank documents *within* one query and have no absolute meaning; never threshold them globally or compare them across queries or indexes. Normalize, or use rank positions, when fusing result lists (§16.11).
:::

## 16.6 Index construction and segment merging

### 16.6.1 Why indexes are built from immutable segments

::: definition
**Definition — Segment.** A self-contained, immutable mini-index (its own dictionary, postings, stored fields, norms and doc values) covering a subset of documents. A Lucene index is a set of segments plus a **commit point** file (`segments_N`) listing which segments are live; a search runs over every live segment and combines the results.
:::

#### First-principles explanation

Compressed, sorted postings lists are excellent to read and terrible to update: inserting docID 5,001 into the middle of a delta-encoded list means rewriting the list. So search engines do what log-structured databases do (§13.7–§13.8): never modify data in place. New documents accumulate in memory; periodically the buffer is written out as a new small segment; small segments are later **merged** into larger ones in the background. This is the LSM-tree pattern, with segments in the role of SSTables. Manning et al. describe the batch ancestors of this design, blocked sort-based indexing and single-pass in-memory indexing, which build partial indexes that fit in memory and merge them [Manning et al. 2008, ch. 4].

Immutability buys a great deal. Segments can be cached by the operating system without invalidation, read without locks while new segments are written, copied for backup or replication as plain files, and compressed aggressively because they are written once.

#### How it works internally

1. **Buffer.** The index writer analyzes incoming documents into an in-memory buffer. Documents in the buffer are *not* searchable.
2. **Refresh (flush to a segment).** The buffer is written as a new segment and a new searcher is opened that includes it. In Lucene terms this is opening a near-real-time reader; Elasticsearch calls it a **refresh** and by default does it every second (§16.8.4). The segment may sit only in the operating system's page cache: it is searchable but not yet durable.
3. **Commit.** Periodically, segment files are fsynced and a new `segments_N` file is written atomically. Only committed segments survive a crash without replay; Elasticsearch covers the gap with its translog (§16.8.3).
4. **Merge.** A background merge scheduler picks groups of segments, merges their postings into one new segment (dropping deleted documents), then swaps it in and deletes the old files once no reader uses them.

**Figure 16.5 — Lifecycle of a Lucene segment.**

```mermaid
stateDiagram-v2
  [*] --> Buffered: index document
  Buffered --> Searchable: refresh writes segment
  Searchable --> Committed: commit fsyncs files
  Searchable --> Merging: selected by merge policy
  Committed --> Merging: selected by merge policy
  Merging --> Deleted: merged segment replaces it
  Deleted --> [*]: files removed when unreferenced
```

**Reading the diagram.** A document enters the in-memory buffer (not yet visible). A refresh writes the buffer out as a segment that searches can see, a cheap operation because it need not wait for the disk. A commit fsyncs segment files and records them in the commit point, making them crash-durable; this is the expensive storage boundary. Either a searchable or a committed segment can be chosen for merging; once the merged segment is in place, the originals are marked deleted and their files removed when the last reader using them closes. All transitions are asynchronous background work relative to queries. Failure points: a crash loses searchable-but-uncommitted segments (recovered from the translog in Elasticsearch); a merge that runs out of disk fails and must be retried. Merging is throttled so it does not starve queries of I/O.

### 16.6.2 Deletes and updates as tombstones

Immutable segments cannot remove a document. Instead Lucene records deletions in a per-segment **live-docs bitset** (one bit per document) written as a separate small file: a **tombstone**. Searches skip documents whose bit is cleared. An **update** is a delete of the old version plus an add of the new one, which lands in a new segment. The space and the CPU spent iterating past deleted postings are reclaimed only when the segment is merged.

Two consequences matter in practice. First, deleted documents still count in term statistics until merged away, so an index with heavy updates can rank slightly differently from a freshly built one. Second, update-heavy workloads (prices and stock levels changing many times a day) generate many deletes, so they need either periodic merging or a design that keeps volatile fields out of the text index.

### 16.6.3 Merge policy

A **merge policy** decides which segments to merge. Lucene's default, `TieredMergePolicy`, groups segments into size tiers, allows about 10 segments per tier, merges up to 10 similar-sized segments at a time, favors merges that reclaim many deletes, and by default stops producing segments larger than about 5 GB [Lucene Docs: TieredMergePolicy]. The analysis is the same as size-tiered compaction in LSM stores (§13.9): each byte is rewritten once per tier it climbs.

::: formula
**Write amplification of tiered merging**

$$W \approx 1 + \log_m \frac{S_{\max}}{S_{\text{flush}}}$$

| Symbol | Meaning | Units |
|---|---|---|
| $W$ | Bytes written to disk per byte of new index data | dimensionless |
| $m$ | Merge factor: segments merged together per tier | count |
| $S_{\max}$ | Maximum merged segment size | bytes |
| $S_{\text{flush}}$ | Typical size of a newly flushed segment | bytes |
:::

::: example
**Worked example — merge cost at a 1-second refresh.** An index receives 2,000 documents/s; each adds about 1 KB to the index; refresh every 1 s gives $S_{\text{flush}} = 2$ MB. $S_{\max} = 5$ GB, $m = 10$.

1. $S_{\max}/S_{\text{flush}} = 5{,}000 / 2 = 2{,}500$.
2. $\log_{10} 2{,}500 = 3.40$, so $W \approx 4.4$.
3. Write bandwidth: $2{,}000 \times 1\ \text{KB} \times 4.4 = 8.8$ MB/s, plus the translog.
4. With a 30-second refresh, $S_{\text{flush}} = 60$ MB, ratio 83, $\log_{10} 83 = 1.92$, $W \approx 2.9$: one-third less merge I/O.

**Interpretation.** Frequent refreshes create many tiny segments that are rewritten several times. **Engineering implication.** For bulk loads and write-heavy indexes, lengthen or disable refresh (§16.10.1). For read-only indexes (yesterday's logs), **force-merge** to one segment once: queries then search one dictionary instead of dozens.
:::

The following simulation of an idealized tiered policy confirms the formula: with three tiers above the flush size and $m = 10$, every unit of data is written exactly four times.

```python
"""Simulate a simplified tiered merge policy and measure write amplification:
every refresh flushes one small segment; whenever `merge_factor` segments of the same tier
exist they are merged into one segment of the next tier, until the size cap is reached."""
import math

def simulate(flushes, merge_factor=10, max_tier=3):
    tiers = [0] * (max_tier + 1)      # number of live segments in each tier
    written = 0                       # units written: flushes + merge output
    for _ in range(flushes):
        tiers[0] += 1
        written += 1                  # the flush itself writes one unit
        t = 0
        while t < max_tier and tiers[t] == merge_factor:
            tiers[t] = 0
            tiers[t + 1] += 1
            written += merge_factor ** (t + 1)    # merged segment size in units
            t += 1
    return written / flushes, sum(tiers)

if __name__ == "__main__":
    for flushes in (1_000, 100_000):
        wa, live = simulate(flushes)
        print(f"flushes={flushes:>7,}  write amplification={wa:.2f}  live segments={live}")
    print("predicted 1 + log10(max/min) =", 1 + math.log10(10 ** 3))
```

Output:

```text
flushes=  1,000  write amplification=4.00  live segments=1
flushes=100,000  write amplification=4.00  live segments=100
predicted 1 + log10(max/min) = 4.0
```

What to notice: once segments reach the cap they stop merging, so the number of live segments grows linearly with data (100 capped segments after 100,000 flushes); that is why large indexes are split into shards and time-based indexes rather than grown without bound.

::: mistake
**Mistake — "Deleting documents frees disk space immediately."** A delete sets a bit. Disk is reclaimed only when a merge rewrites the segment, and a merge temporarily needs space for both old and new segments. Clusters that are nearly full can fail to merge, accumulate deletes, and degrade; keep at least 15–20% free disk on data nodes and watch Elasticsearch's disk watermarks.
:::

## 16.7 Distributed search

### 16.7.1 Document partitioning versus term partitioning

When an index outgrows one node, or one node cannot serve the query rate, the index is partitioned. Search engines use the word **shard** for a partition (§14.6); this chapter uses the two interchangeably. There are two ways to cut an inverted index [Manning et al. 2008, §20.3].

- **Document partitioning** (local index): each shard holds *all* terms for a subset of documents, a complete small index. Every query goes to every shard, and a coordinator merges the per-shard top-*k* lists.
- **Term partitioning** (global index): each shard holds the *complete* postings lists for a subset of terms. A query visits only the shards owning its terms, but a multi-term query must ship long postings lists between nodes to intersect or score them.

**Figure 16.6 — Document partitioning versus term partitioning.**

```mermaid
flowchart TB
  subgraph DP[Document partitioning]
    C1([Query: noise headphones]) -->|fan out to all| S1[Shard A<br/>docs 1 to 4M<br/>all terms]
    C1 -->|fan out to all| S2[Shard B<br/>docs 4M to 8M<br/>all terms]
    S1 -->|local top-k| M1[Merge top-k]
    S2 -->|local top-k| M1
  end
  subgraph TP[Term partitioning]
    C2([Query: noise headphones]) -->|terms a to m| T1[Shard X<br/>headphone postings<br/>all docs]
    C2 -->|terms n to z| T2[Shard Y<br/>noise postings<br/>all docs]
    T1 -->|full postings list| J[Intersect and score]
    T2 -->|full postings list| J
  end
```

**Reading the diagram.** In the upper subgraph the query fans out synchronously to every document shard; each shard runs the complete pipeline of Figure 16.4 on its own documents and returns only its top *k* (a few kilobytes), which a coordinator merges. In the lower subgraph the query goes only to the shards that own its terms, but each returns an entire postings list, potentially megabytes, which must be intersected and scored centrally. Each shard is its own storage boundary. Failure points: under document partitioning a slow or dead shard affects every query (mitigated by replicas); under term partitioning a hot term overloads one shard, and a dead shard makes every query containing its terms incomplete. Document partitioning scales by adding shards and replicas; term partitioning scales poorly for multi-term queries because network transfer grows with postings length.

**Table 16.8 — Document versus term partitioning.**

| | Document partitioning | Term partitioning |
|---|---|---|
| What it is | Each shard indexes a subset of documents | Each shard owns all postings of a subset of terms |
| Query fan-out | All shards | Only shards owning query terms |
| Network per query | Small (top-*k* per shard) | Large (full postings lists) |
| Load balance | Even (random document assignment) | Skewed (Zipfian term popularity) |
| Indexing a document | Writes to one shard | Writes to many shards (one per term) |
| Tail latency | Max of $S$ shard latencies | Fewer shards, but long transfers |
| Used by | Lucene-based engines, Google (as published), Earlybird | Research systems; rarely in production |
| Choose when | Almost always | Very high query rate of single-term lookups |

Document partitioning wins in practice because it is simple, balanced and fault-tolerant [Dean 2009].

### 16.7.2 Replicas

Each shard is copied to $r$ **replicas** on different nodes (and availability zones). Replicas serve two purposes: **availability** (a shard survives node loss) and **query throughput** (any copy can answer a query). They do not speed up indexing, since every copy must index every write. A rough sizing rule: if each query costs $c$ CPU-seconds on each of $S$ shards and the peak rate is $\lambda$ queries per second, the cluster needs $\lambda \cdot S \cdot c / U$ cores at target utilization $U$. For example, 2,000 queries/s × 10 shards × 4 ms ÷ 0.5 = 160 cores; with 16-core nodes that is 10 nodes, so each of the 10 shards needs enough copies to place work on all of them (for example 1 primary + 1 replica across 10 nodes gives 20 shard copies, two per node).

### 16.7.3 Scatter–gather and tail latency

A document-partitioned query is a **scatter–gather**: a coordinator scatters the query to one copy of each of $S$ shards and gathers their answers. The response time is the *maximum* of $S$ shard latencies, so the fan-out amplification of §4.8.4 applies directly.

::: formula
**Scatter–gather tail latency**

$$P(\text{query fast}) = p^{S} \qquad q_{\text{shard}} = q_{\text{query}}^{1/S}$$

| Symbol | Meaning | Units |
|---|---|---|
| $p$ | Probability one shard answers within threshold $T$ | dimensionless |
| $S$ | Number of shards the query waits for | count |
| $P(\text{query fast})$ | Probability all $S$ shards answer within $T$ | dimensionless |
| $q_{\text{query}}$ | Target percentile for the whole query (e.g. 0.99) | dimensionless |
| $q_{\text{shard}}$ | Percentile each shard must meet at $T$ | dimensionless |
:::

::: example
**Worked example — 20 and 100 shards.** Each shard's latency is log-normal with median 8 ms and p99 25.6 ms (simulated below). Assume independence.

1. $S = 20$: $P(\text{all} \leq 25.6\ \text{ms}) = 0.99^{20} = 0.818$; 18% of queries wait longer than the shard p99.
2. For the *query* p99 to be 25.6 ms, each shard needs $0.99^{1/20} = 0.99950$, its p99.95 at 25.6 ms.
3. $S = 100$: $0.99^{100} = 0.366$. The query median becomes the shard's $0.5^{1/100} = $ p99.3, which is 27.4 ms, more than three times the shard median, and the query p99 is about 51 ms.

**Interpretation.** Adding shards makes every shard's work smaller but makes the query wait for the unluckiest of more shards. **Engineering implication.** Use the fewest shards that meet size and throughput needs (§16.8.2), and use tail-tolerant techniques: **hedged requests** to a second replica after a delay [Dean and Barroso 2013], **adaptive replica selection** that routes to the replica with the best recent latency and queue length (on by default in Elasticsearch since 7.0, based on the C3 algorithm [Suresh et al. 2015]), and per-shard **timeouts with partial results**, accepting slightly incomplete answers rather than slow ones.
:::

```python
"""Scatter-gather tail latency: a query waits for the slowest of S shards.
Monte Carlo check of P(all fast) = p**S, and the latency percentiles of max(S shard latencies)."""
import math
import random

def shard_latency_ms(rng):
    # Log-normal per-shard latency: median 8 ms, a heavy-ish right tail (p99 ~ 25.6 ms).
    return 8.0 * math.exp(rng.gauss(0.0, 0.5))

def percentile(sorted_vals, q):
    return sorted_vals[min(len(sorted_vals) - 1, int(q * len(sorted_vals)))]

if __name__ == "__main__":
    rng = random.Random(42)
    trials = 20_000
    single = sorted(shard_latency_ms(rng) for _ in range(200_000))
    t99 = percentile(single, 0.99)
    print(f"one shard: p50={percentile(single, 0.50):.1f} ms  p99={t99:.1f} ms")
    print(" S   P(all<shard p99) sim  0.99**S   query p50   query p99")
    for S in (1, 10, 50, 100, 200):
        maxes = sorted(max(shard_latency_ms(rng) for _ in range(S)) for _ in range(trials))
        fast = sum(m <= t99 for m in maxes) / trials
        print(f"{S:>3}   {fast:>18.3f}  {0.99 ** S:>7.3f}   {percentile(maxes, 0.5):>6.1f} ms"
              f"   {percentile(maxes, 0.99):>6.1f} ms")
```

Output:

```text
one shard: p50=8.0 ms  p99=25.6 ms
 S   P(all<shard p99) sim  0.99**S   query p50   query p99
  1                0.991    0.990      8.0 ms     25.2 ms
 10                0.904    0.904     16.9 ms     37.7 ms
 50                0.614    0.605     24.0 ms     46.9 ms
100                0.367    0.366     27.4 ms     51.1 ms
200                0.136    0.134     30.9 ms     56.3 ms
```

What to notice: the simulation matches $0.99^S$; the query *median* at 100 shards (27.4 ms) is worse than a single shard's p99. Real shard latencies are also correlated (garbage-collection pauses, merges, a noisy neighbor), which makes the tail worse than the independent model.

### 16.7.4 Two-phase query-then-fetch

Shipping full documents from every shard would waste bandwidth, since most are discarded during the merge. Elasticsearch therefore runs a search in two phases [Elastic Docs: search_type].

**Figure 16.7 — Query-then-fetch across three shards.**

```mermaid
sequenceDiagram
  participant C as Client
  participant CO as Coordinating node
  participant A as Shard A copy
  participant B as Shard B copy
  participant D as Shard C copy
  C->>CO: search q, from 0, size 10
  par Query phase
    CO->>A: query q, top 10
    CO->>B: query q, top 10
    CO->>D: query q, top 10
  end
  A-->>CO: 10 docIDs and scores
  B-->>CO: 10 docIDs and scores
  D-->>CO: 10 docIDs and scores
  CO->>CO: merge 30 entries, keep global top 10
  par Fetch phase
    CO->>A: fetch docs 3 and 17
    CO->>D: fetch docs 5, 8 and others
  end
  A-->>CO: stored fields and highlights
  D-->>CO: stored fields and highlights
  CO-->>C: 10 ranked results
```

**Reading the diagram.** The client sends one request to any node, which acts as **coordinating node**. In the **query phase** it sends the query in parallel to one copy of every shard; each returns only docIDs and scores for its local top 10. The coordinator merges the 30 entries into a global top 10. In the **fetch phase** it asks only the shards that own those 10 documents for stored fields (`_source`) and highlighted snippets; shard B contributed nothing to the top 10, so it is not contacted. All calls are synchronous RPCs over the cluster transport protocol; each shard copy is a storage boundary. Failure points: a slow shard delays the query phase for everyone (§16.7.3); a shard copy that fails between phases forces a retry on another replica. The design scales because the expensive document payload is read for only $k$ documents, not $S \times k$.

::: formula
**Deep pagination cost at the coordinator**

$$E = S \cdot (\textit{from} + \textit{size})$$

| Symbol | Meaning | Units |
|---|---|---|
| $S$ | Shards queried | count |
| $\textit{from}$ | Offset of the first requested result | results |
| $\textit{size}$ | Results per page | results |
| $E$ | Entries every query phase must return and the coordinator must merge | entries |
:::

::: example
**Worked example — page 500.** $S = 20$ shards, 20 results per page.

1. Page 1: $E = 20 \times (0 + 20) = 400$ entries.
2. Page 500: $\textit{from} = 499 \times 20 = 9{,}980$, so $E = 20 \times 10{,}000 = 200{,}000$ entries, 500× more, and each shard must also keep a heap of 10,000.

**Interpretation.** Deep pages cost in proportion to their depth. **Engineering implication.** Elasticsearch rejects requests with $\textit{from} + \textit{size}$ above `index.max_result_window`, 10,000 by default. Use `search_after` with a sort tiebreaker (and a point-in-time snapshot) for deep scrolling, and the scroll or point-in-time APIs for exports.
:::

### 16.7.5 Global versus local IDF

Each shard computes BM25 with its own $N$, $n_t$ and avgdl. When documents are spread uniformly at random, local statistics are close to global ones. When they are not, scores from different shards are not comparable.

::: example
**Worked example — skewed term distribution.** Two shards hold 1,000,000 documents each. Custom routing by seller put most "anc" listings on shard B: shard A has 10 documents containing *anc*, shard B has 1,000.

1. Local IDF on A: $\ln(1 + 999{,}990.5 / 10.5) = 11.46$.
2. Local IDF on B: $\ln(1 + 999{,}000.5 / 1{,}000.5) = 6.91$.
3. Global IDF ($N = 2{,}000{,}000$, $n = 1{,}010$): $\ln(1 + 1{,}998{,}990.5 / 1{,}010.5) = 7.59$.

**Interpretation.** An *anc* match on shard A scores 66% higher than an identical match on shard B, purely because of where documents live, so shard A's weak matches crowd out shard B's strong ones. **Engineering implication.** Elasticsearch's default `query_then_fetch` uses local statistics. `dfs_query_then_fetch` adds a preliminary round trip that collects term statistics from all shards and scores with global values, at the cost of extra latency [Elastic Docs: search_type]. Prefer random document routing so local statistics converge; use DFS for small or skewed indexes and in relevance tests.
:::

**Routing** is the other side of the trade-off. By default Elasticsearch places a document on a shard by hashing its ID. A custom routing key (tenant ID, seller ID) places all of one tenant's documents on one shard, so a tenant-scoped query hits one shard instead of $S$, removing fan-out at the cost of skew and the IDF effect above.

#### Real-world industry applications

::: industry
**Twitter Earlybird.** Twitter's real-time search engine kept recent tweets in in-memory inverted indexes partitioned by document across many Earlybird servers, with a front-end (Blender) scattering each query and merging results. Indexing used a single writer and many concurrent readers per index, coordinated with memory barriers rather than locks, so that tweets became searchable within about 10 seconds of creation while queries averaged about 50 ms at billions of queries per day (2012 figures) [Busch et al. 2012].
*Evidence: Primary* — [Busch et al. 2012]
:::

::: industry
**Google web search serving.** Jeff Dean's 2009 retrospective describes Google's serving system as document-partitioned index shards, each replicated, behind root and intermediate servers that fan out queries and merge results, and recounts the move to serving the index from memory across many machines around 2001 [Dean 2009].
*Evidence: Primary* — [Dean 2009]
:::

## 16.8 Elasticsearch and OpenSearch architecture

Elasticsearch wraps Lucene in a distributed system: a JSON-over-HTTP API, cluster membership, shard placement, replication and recovery. OpenSearch is a fork of Elasticsearch 7.10.2 created in 2021 after Elastic changed its license; the two share the architecture described here, though they have diverged in features since [OpenSearch Docs].

### 16.8.1 Cluster, nodes and roles

::: definition
**Definition — Elasticsearch cluster.** A set of nodes that share one cluster state (index definitions, mappings and the location of every shard copy). An **index** is a logical collection of documents divided into **primary shards**; each primary has zero or more **replica shards**; every shard is one Lucene index.
:::

Nodes take one or more **roles** [Elastic Docs: node roles]: **master-eligible** nodes elect one elected master that owns and publishes the cluster state (a quorum-based protocol since 7.0, so three master-eligible nodes tolerate the loss of one); **data** nodes hold shards and execute queries and indexing (subdivided into hot, warm, cold and frozen tiers for time-based data); **ingest** nodes run preprocessing pipelines; and **coordinating-only** nodes route requests and merge results.

**Figure 16.8 — A three-zone Elasticsearch cluster with two primaries and one replica each.**

```mermaid
flowchart TB
  C([Search API service]) -->|HTTPS REST| CO[Coordinating nodes]
  subgraph Zone A
    M1[Master-eligible 1]
    D1[(Data node 1<br/>P0, R1)]
  end
  subgraph Zone B
    M2[Master-eligible 2<br/>elected master]
    D2[(Data node 2<br/>P1)]
  end
  subgraph Zone C
    M3[Master-eligible 3]
    D3[(Data node 3<br/>R0)]
  end
  CO -->|transport RPC| D1
  CO -->|transport RPC| D2
  CO -->|transport RPC| D3
  M2 -.->|publish cluster state| D1
  M2 -.->|publish cluster state| D3
  M2 -.->|publish cluster state| M1
  M2 -.->|publish cluster state| M3
```

**Reading the diagram.** Clients call coordinating nodes over HTTPS; coordinating nodes talk to data nodes over Elasticsearch's binary transport protocol (synchronous RPCs, solid arrows). The index has two primary shards, P0 and P1, and one replica of each, R0 and R1; the allocator never places a primary and its replica on the same node and, with allocation awareness configured, not in the same zone. The elected master publishes cluster-state updates asynchronously (dotted arrows) to every node; it does not sit on the data path. Storage boundaries are the data nodes' local disks. Failure points: losing data node 2 promotes R1 to primary and starts rebuilding a replica elsewhere; losing one master-eligible node leaves a quorum of two; losing a whole zone still leaves one copy of each shard. Scaling: add data nodes (shards rebalance automatically), add replicas for query throughput, and add coordinating nodes for heavy aggregations.

### 16.8.2 Shards, routing and sizing

A document goes to shard $\text{hash}(\textit{routing}) \bmod N_{\text{primaries}}$, where routing defaults to the document ID and the hash is Murmur3 [Elastic Docs: _routing]. Because the formula depends on the number of primaries, that number is fixed when the index is created; changing it requires the split or shrink APIs (by integer factors) or a reindex. Replica count can be changed at any time. Since Elasticsearch 7.0 a new index has one primary and one replica by default.

Elastic's sizing guidance (as of 2025) is to aim for shards of roughly 10–50 GB and fewer than about 200 million documents each [Elastic Docs: size your shards]. Too-large shards recover slowly after node failure; too many small shards waste per-shard memory and inflate fan-out (§16.7.3). For the 440 GB catalog of §16.3.5 (about 220 GB of primary data), five primaries of roughly 44 GB fit the guidance. For logs and events, use **time-based indexes** with rollover and lifecycle policies, so old indexes can be force-merged, moved to cheaper tiers and deleted whole.

### 16.8.3 The write path: primary–backup replication and the translog

Elasticsearch uses primary–backup replication, modeled on Microsoft's PacificA protocol [Elastic Docs: data replication model].

**Figure 16.9 — Indexing one document with one replica.**

```mermaid
sequenceDiagram
  participant C as Client
  participant CO as Coordinating node
  participant P as Primary shard
  participant R as Replica shard
  C->>CO: index doc 42
  CO->>CO: shard = hash of routing mod primaries
  CO->>P: forward request
  P->>P: validate, assign seq no, add to Lucene buffer
  P->>P: append to translog, fsync
  P->>R: replicate operation with seq no
  R->>R: add to Lucene buffer, append translog, fsync
  R-->>P: ack
  P-->>CO: success on all in-sync copies
  CO-->>C: 201 Created
  Note over P,R: searchable only after the next refresh
```

**Reading the diagram.** The coordinating node computes the shard and forwards the request to the node holding that shard's primary. The primary validates the document, assigns a sequence number (used to bring replicas back in sync after failures), indexes it into Lucene's in-memory buffer and appends it to the **translog**, a per-shard write-ahead log (§13.5) that by default is fsynced before the request is acknowledged (`index.translog.durability: request`). The primary then forwards the operation to all **in-sync** replicas in parallel and acknowledges only when they have all responded. Every arrow is synchronous; the disk boundary is the translog fsync on each copy. Failure points: a replica that fails to respond is reported to the master and removed from the in-sync set rather than blocking writes; a primary failure promotes an in-sync replica. The acknowledged document is durable but not yet visible to search; visibility comes at the next refresh. Indexing throughput scales with primaries, not replicas.

**Table 16.9 — Refresh, flush and merge in Elasticsearch.**

| Operation | What it does | Default trigger | Makes data | Cost |
|---|---|---|---|---|
| Index (ack) | Buffer + translog fsync | Each request | Durable, not searchable | One fsync per request or bulk |
| Refresh | Write buffer as segment, reopen searcher | Every 1 s if the index was searched in the last 30 s | Searchable | New small segment; merge load |
| Flush | Lucene commit (fsync segments), trim translog | Translog size threshold | Durable without replay | Heavy fsync |
| Merge | Combine segments, drop deletes | Merge policy | Smaller, faster index | Background I/O and CPU |

This split is what **near-real-time** means: a write is durable at acknowledgement (thanks to the translog) and searchable about one refresh interval later, without paying for a Lucene commit on every write [Elastic Docs: near real-time search]. A client that must read its own write can pass `refresh=wait_for`, which blocks the response until the next scheduled refresh.

### 16.8.4 Read path and memory

Queries rely on three caches: the operating system **page cache** holding segment files (the most important; leave about half of RAM outside the JVM heap for it), the **shard request cache** for aggregation results, and the **node query cache** for filter bitsets. Elastic recommends a heap of at most half of RAM and below the roughly 31 GB compressed-object-pointer limit [Elastic Docs: heap size]. **Doc values**, column-oriented on-disk structures built at index time, serve sorting and aggregations without loading fields into the heap.

**Table 16.10 — Elasticsearch, OpenSearch and Solr compared (as of 2025).**

| | Elasticsearch | OpenSearch | Apache Solr |
|---|---|---|---|
| What it is | Lucene-based distributed engine by Elastic | Community fork of Elasticsearch 7.10.2 (Linux Foundation) | Apache Lucene project's search server |
| Coordination | Built-in quorum-based cluster coordination | Inherited from Elasticsearch | ZooKeeper (SolrCloud) |
| Replication | Document replication; stateless serverless offering | Document or segment replication | Replica types NRT, TLOG, PULL |
| Advantages | Feature velocity, ecosystem | Open-source license, AWS managed service | Mature, flexible configuration |
| Disadvantages | Licensing changes over time | Features lag or differ from Elasticsearch | Smaller operational ecosystem today |
| Choose when | You want the reference product and its tooling | You want Apache-licensed software or AWS OpenSearch Service | Existing Solr expertise or ZooKeeper-based operations |

OpenSearch's **segment replication** copies segment files from primary to replicas instead of re-indexing each document on every replica, trading replica freshness for lower replica CPU [OpenSearch Docs: segment replication].

#### Failure scenarios

**Table 16.11 — Distributed search and cluster failure scenarios.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| Cluster status red | All copies of a primary lost | Cluster health API | Restore shard from snapshot; reindex from source | Replicas across zones; snapshots |
| Mapping explosion | Dynamic mapping of arbitrary JSON keys creates thousands of fields | Field count; cluster-state size | Reindex with strict mapping | `dynamic: strict`; field limits |
| Hot shard | Custom routing on a skewed key | Per-shard latency and CPU | Reroute; split shard | Random routing; routing partitions |
| Long GC pauses, node drops out | Heap too large or full | GC logs; node-left events | Reduce heap pressure; restart | Heap ≤ 50% RAM; circuit breakers |
| Stale results | Indexing pipeline lag | Freshness metric (§16.10.3) | Scale consumers | Alert on consumer lag |

::: mistake
**Mistake — "Elasticsearch can be our primary database."** It is durable per shard and replicated, but it has no multi-document transactions, near-real-time rather than immediate visibility, and mapping changes often require reindexing. Treat it as a derived, rebuildable view of a system of record (§16.10.4).
:::

## 16.9 Typeahead and autocomplete

### 16.9.1 Requirements and the latency budget

::: definition
**Definition — Autocomplete (typeahead).** A service that, given the prefix a user has typed so far, returns a short ranked list (typically 5–10) of likely completions, usually popular past queries or entity names, on every keystroke or after a short pause.
:::

#### First-principles explanation

Autocomplete is a conversation with someone who finishes your sentences. It is only helpful if the suggestion arrives before you type the next letter: people type a character every 150–300 ms, and Nielsen's classic guideline is that about 0.1 s feels instantaneous [Nielsen 1993]. So the whole round trip, not just the server, must fit in roughly 100 ms. That rules out running a full search per keystroke and pushes design toward precomputation: the answer for every popular prefix is computed offline and looked up, not searched.

**Table 16.12 — End-to-end latency budget for one suggestion request.**

| Stage | Budget | Notes |
|---|---|---|
| Client event handling | ≤ 5 ms | Plus an optional 30–50 ms debounce, outside the budget |
| Network round trip | 30–50 ms | Reused HTTP/2 or HTTP/3 connection; nearby edge |
| Load balancer and gateway | 2–5 ms | No per-request authentication call |
| Suggestion lookup | ≤ 5 ms at p99 | In-memory trie or FST; no disk |
| Serialization and render | ~16 ms | One frame at 60 Hz |
| **Total** | **≈ 55–80 ms** | Leaves headroom under 100 ms |

::: formula
**Autocomplete load and precomputed-index memory**

$$\lambda_{\text{ac}} = \lambda_{\text{search}} \cdot c \cdot f \qquad M_{\text{top-}k} \approx P \cdot k \cdot b$$

| Symbol | Meaning | Units |
|---|---|---|
| $\lambda_{\text{search}}$ | Searches started per second | searches/s |
| $c$ | Characters typed per search before selecting or submitting | characters |
| $f$ | Fraction of keystrokes that send a request (after debounce and client caching) | dimensionless |
| $\lambda_{\text{ac}}$ | Suggestion request rate | requests/s |
| $P$ | Number of trie nodes (distinct prefixes) with stored suggestions | nodes |
| $k$ | Suggestions stored per prefix | count |
| $b$ | Bytes per stored suggestion reference | bytes |
| $M_{\text{top-}k}$ | Memory for the precomputed lists | bytes |
:::

::: example
**Worked example — sizing typeahead for the store.** 50 million searches/day, peak-to-average ratio 2, $c = 8$, $f = 0.5$. The suggestion corpus is 10 million distinct past queries, giving an assumed $P = 6 \times 10^7$ trie nodes after prefix sharing; $k = 10$, $b = 4$ bytes (a query ID).

1. Average search rate: $5 \times 10^7 / 86{,}400 = 579$ searches/s; peak $\approx 1{,}157$/s.
2. Peak suggestion rate: $1{,}157 \times 8 \times 0.5 \approx 4{,}630$ requests/s, four times the search rate.
3. Memory for top-10 lists: $6 \times 10^7 \times 10 \times 4 = 2.4 \times 10^9$ bytes = 2.4 GB, plus the trie nodes themselves and the query strings (10 M × ~20 bytes = 200 MB).

**Interpretation.** Autocomplete usually generates more requests than search itself, but each is a memory lookup. **Engineering implication.** A few replicated in-memory nodes handle this load. Memory, not CPU, is the constraint, so cap precomputation at short prefixes (for example up to 10 characters), drop rare queries, and cache the responses for the most popular one- and two-character prefixes at the CDN or in the client.
:::

### 16.9.2 Tries with precomputed top-*k*

A **trie** (§17.11) stores strings as paths from the root, one character per edge; all strings with a given prefix live under one node. Finding that node takes $O(\ell)$ steps for a prefix of length $\ell$. The naive next step, walking the whole subtree to find the most popular completions, can touch millions of nodes for a one-letter prefix. The fix is to **store the top-*k* completions at every node**, computed bottom-up offline: a node's list is the best $k$ among its own query (if one ends there) and its children's lists.

**Figure 16.10 — A trie with top-2 completions stored at each node.**

```mermaid
flowchart TB
  R((root)) -->|h| H["h<br/>top: headphones 9200,<br/>hdmi cable 5300"]
  H -->|e| HE["he<br/>top: headphones 9200,<br/>headphones wireless 4100"]
  H -->|d| HD["hd<br/>top: hdmi cable 5300"]
  H -->|a| HA["ha<br/>top: hair dryer 4800,<br/>hard drive 3900"]
  HE -->|a| HEA["hea<br/>top: headphones 9200,<br/>headphones wireless 4100"]
  HEA -->|t| HEAT["heat<br/>top: heated blanket 2100"]
```

**Reading the diagram.** Each node is a prefix; edges are labeled with the next character. Each node stores its precomputed top-2 list with popularity counts from the query log. A lookup for "hea" follows three edges from the root and returns the list stored at that node with no further traversal. "heated blanket" lives under "heat" and appears in the lists of "he" and "hea" only when $k \geq 3$, because two headphone queries outrank it. The structure is read-only in memory; it is rebuilt offline and swapped in atomically. Failure points: an outdated build (stale trends) and memory exhaustion as the corpus grows. It scales by replication, and by partitioning on the first character or two of the prefix if one node cannot hold it.

```python
"""Trie-based autocomplete with the top-k completions precomputed at every node.
Lookup cost is O(len(prefix)) and independent of how many queries share the prefix."""
import heapq

class Node:
    __slots__ = ("children", "count", "top")
    def __init__(self):
        self.children = {}      # char -> Node
        self.count = 0          # popularity if a query ends here, else 0
        self.top = []           # precomputed [(count, query)] best-first, length <= k

class Autocomplete:
    def __init__(self, k=3):
        self.root, self.k, self.nodes = Node(), k, 1

    def insert(self, query, count):
        node = self.root
        for ch in query:
            if ch not in node.children:
                node.children[ch] = Node()
                self.nodes += 1
            node = node.children[ch]
        node.count += count

    def build_top_k(self, node=None, prefix=""):
        """Post-order pass: a node's top-k = best k of (itself, children's top-k lists)."""
        node = node or self.root
        candidates = [(node.count, prefix)] if node.count else []
        for ch, child in node.children.items():
            self.build_top_k(child, prefix + ch)
            candidates.extend(child.top)
        node.top = heapq.nlargest(self.k, candidates, key=lambda c: c[0])

    def suggest(self, prefix):
        node = self.root
        for ch in prefix.lower():
            node = node.children.get(ch)
            if node is None:
                return []
        return [q for _, q in node.top]

    def suggest_by_dfs(self, prefix):
        """Without precomputation: walk the whole subtree. Returns (suggestions, nodes visited)."""
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return [], 0
        found, stack, visited = [], [(node, prefix)], 0
        while stack:
            n, p = stack.pop()
            visited += 1
            if n.count:
                found.append((n.count, p))
            stack.extend((c, p + ch) for ch, c in n.children.items())
        best = heapq.nlargest(self.k, found, key=lambda c: c[0])
        return [q for _, q in best], visited

QUERY_LOG = {   # query -> times searched in the last 7 days (illustrative)
    "headphones": 9200, "headphones wireless": 4100, "headphone stand": 800,
    "headphones for kids": 1500, "head torch": 650, "heated blanket": 2100,
    "hdmi cable": 5300, "hard drive": 3900, "hair dryer": 4800, "hammock": 300,
}

if __name__ == "__main__":
    ac = Autocomplete(k=3)
    for q, c in QUERY_LOG.items():
        ac.insert(q, c)
    ac.build_top_k()
    for prefix in ("h", "he", "hea", "head", "headphones ", "x"):
        print(f"{prefix!r:>15} -> {ac.suggest(prefix)}")
    dfs, visited = ac.suggest_by_dfs("h")
    assert dfs == ac.suggest("h")
    print(f"trie nodes={ac.nodes}; DFS for 'h' visits {visited} nodes, precomputed lookup reads 1 node")
```

Output:

```text
            'h' -> ['headphones', 'hdmi cable', 'hair dryer']
           'he' -> ['headphones', 'headphones wireless', 'heated blanket']
          'hea' -> ['headphones', 'headphones wireless', 'heated blanket']
         'head' -> ['headphones', 'headphones wireless', 'headphones for kids']
  'headphones ' -> ['headphones wireless', 'headphones for kids']
            'x' -> []
trie nodes=82; DFS for 'h' visits 81 nodes, precomputed lookup reads 1 node
```

What to notice: the build pass is one post-order traversal costing $O(\text{nodes} \cdot k \log k)$, done offline; the online lookup reads $\ell$ nodes regardless of corpus size; and a ten-query log already needs 82 nodes, which is why production systems compress the trie.

### 16.9.3 Finite-state transducers in Lucene

A trie shares common *prefixes* only. A **finite-state transducer (FST)** is a minimal automaton that shares both prefixes and suffixes ("-phones", "-ing") and attaches an output, such as a weight or an ordinal, to each accepted string. Minimal acyclic automata can be built incrementally from sorted input in linear time [Daciuk et al. 2000]. Lucene uses FSTs for its term-dictionary index, and Elasticsearch's **completion suggester** (the `completion` field type) stores weighted suggestions in a per-segment FST held in memory, giving top-*k* lookups in microseconds with optional fuzzy matching and context filters [Elastic Docs: completion suggester]. Because the FST lives inside segments, suggestions update through normal indexing and refresh.

**Table 16.13 — Autocomplete approaches.**

| Approach | How it works | Advantages | Disadvantages | Choose when |
|---|---|---|---|---|
| Trie with top-*k* per node | Offline build from query logs | Fastest; full control of ranking | Custom service; rebuilds | Very high traffic; query-log suggestions |
| FST completion suggester | Weighted FST per segment | Built in; compact; fuzzy | Prefix-only; weights static per document | Entity names in Elasticsearch |
| Edge n-gram field | Index every prefix as a term | Matches inner words, full query features | Index 3–10× larger; slower | Suggestions need filters and scoring |
| `search_as_you_type` field | Managed shingles and edge n-grams | Easy, infix-friendly | Same costs as edge n-grams | Small to medium catalogs |

### 16.9.4 Serving architecture

**Figure 16.11 — Autocomplete: offline build and online serving.**

```mermaid
flowchart LR
  subgraph Offline
    LOG[[Query log stream]] -.->|hourly batch| AGG[Aggregate and filter<br/>counts, decay, blocklist]
    AGG -.->|build| BLD[Trie or FST builder]
    BLD -.->|versioned snapshot| OBJ[(Object storage)]
  end
  subgraph Online
    U([User typing]) -->|HTTPS prefix| CDN{{CDN cache<br/>short prefixes}}
    CDN -->|miss| SVC[Suggest service<br/>in-memory index]
    OBJ -.->|load and swap| SVC
  end
  U -.->|selected or submitted query| LOG
```

**Reading the diagram.** The offline subgraph runs asynchronously (dotted arrows): query logs are aggregated with time decay so trends surface, filtered against a blocklist of offensive or unsafe completions, built into a trie or FST, and published as a versioned snapshot to object storage. Online, the user's prefix goes over HTTPS to a CDN that caches responses for popular short prefixes; misses reach stateless suggest-service replicas that hold the whole structure in memory and swap in new snapshots atomically. The user's eventual query flows back into the log, closing the loop. Storage boundaries are the log, object storage and each replica's memory. Failure points: a bad snapshot (roll back to the previous version), a poisoned log (rate-limit and filter per user), and stale caches during breaking news (short TTLs). Scaling: add replicas; partition by prefix if memory runs out; personalize by blending global suggestions with the user's own recent queries at request time.

## 16.10 Near-real-time indexing

### 16.10.1 The refresh interval trade-off

::: definition
**Definition — Near-real-time (NRT) search.** A search system in which newly written documents become searchable after a short, bounded delay (typically one second to a minute) rather than immediately, because making them visible requires creating a new segment and reopening the searcher.
:::

Every refresh creates a segment and a new searcher, and invalidates per-segment caches for the new data. Refreshing more often gives fresher results but more tiny segments, more merging (§16.6.3) and lower indexing throughput.

**Table 16.14 — Choosing a refresh interval.**

| Setting | Freshness | Indexing throughput | Merge load | Typical use |
|---|---|---|---|---|
| 1 s (default) | ~1 s | Lowest | Highest ($W \approx 4.4$ in §16.6.3) | Product, user-facing content |
| 30 s | ~30 s | Higher | Lower ($W \approx 2.9$) | Logs, metrics, analytics |
| `-1` (disabled) during bulk load, replicas 0 | None until re-enabled | Highest | Lowest | Initial load or full reindex |
| `refresh=wait_for` on a request | Caller waits for next refresh | Unchanged | Unchanged | Read-your-writes for one client |

Never call an explicit refresh after every write: it turns each document into its own segment and can collapse indexing throughput.

### 16.10.2 The indexing pipeline: CDC and Kafka

The source of truth is usually a relational database. Writing to the database *and* to the search index from application code (**dual writes**) loses updates whenever one write succeeds and the other fails, and can apply concurrent updates in different orders to the two stores [Kleppmann 2017, ch. 11]. The robust pattern is to derive the index from the database's own change log.

**Figure 16.12 — Near-real-time indexing pipeline with CDC and Kafka.**

```mermaid
flowchart LR
  APP[Catalog service] -->|SQL transaction| DB[(PostgreSQL)]
  DB -.->|WAL via logical decoding| CDC[Debezium CDC]
  CDC -.->|keyed by product ID| K[[Kafka topic<br/>product changes]]
  K -.->|consume in order<br/>per partition| IDXR[Indexer service]
  IDXR -->|lookup prices, stock| ENR[(Enrichment stores)]
  IDXR -->|bulk API,<br/>external version| ALIAS{{Alias products}}
  ALIAS --> V2[(Index products_v2)]
  K -.->|replay from offset 0| REB[Rebuild job]
  REB -.->|bulk load| V3[(Index products_v3)]
```

**Reading the diagram.** The catalog service writes only to PostgreSQL, synchronously. Debezium reads the write-ahead log through logical decoding and publishes each committed change to Kafka asynchronously, keyed by product ID so that all changes to one product land in one partition, in order. The indexer consumes partitions, enriches each event into a complete search document (prices, stock, review counts from other stores), and writes in bulk through an **alias**, a stable name pointing at the current physical index. Each write carries an external version (for example the source log sequence number), so a replayed or reordered older event is rejected and the pipeline stays idempotent under at-least-once delivery (§22.15). Deletes arrive as delete events and become delete requests. Storage boundaries: the database, the Kafka log, the enrichment stores and the index. Failure points: indexer lag (search becomes stale, never wrong), poison events (send to a dead-letter topic), and Kafka retention shorter than a rebuild. Scaling: more Kafka partitions and indexer consumers. The lower path shows a full **rebuild**: a job replays the topic (or a snapshot plus the topic) into `products_v3` with refresh disabled; when it catches up, the alias is switched atomically from v2 to v3, a zero-downtime reindex used for analyzer or mapping changes.

### 16.10.3 Freshness budget

::: formula
**End-to-end freshness latency**

$$T_{\text{fresh}} \approx T_{\text{cdc}} + T_{\text{queue}} + T_{\text{batch}} + T_{\text{index}} + T_{\text{refresh}}$$

| Symbol | Meaning | Units |
|---|---|---|
| $T_{\text{cdc}}$ | Commit to event published in Kafka | s |
| $T_{\text{queue}}$ | Time the event waits for the indexer (consumer lag) | s |
| $T_{\text{batch}}$ | Wait for a bulk request to fill or its timer to fire | s |
| $T_{\text{index}}$ | Bulk request execution on primary and replicas | s |
| $T_{\text{refresh}}$ | Wait for the next refresh: uniform in $[0, I]$, mean $I/2$ | s |
| $T_{\text{fresh}}$ | Commit in source database to searchable | s |
:::

::: example
**Worked example — how fresh is a price change?** $T_{\text{cdc}} = 0.2$ s, $T_{\text{queue}} = 0.3$ s at normal load, bulk requests flush every 1 s (mean wait 0.5 s, worst 1 s), $T_{\text{index}} = 0.1$ s, refresh interval $I = 1$ s (mean 0.5 s, worst 1 s).

1. Mean: $0.2 + 0.3 + 0.5 + 0.1 + 0.5 = 1.6$ s.
2. Worst case without backlog: $0.2 + 0.3 + 1 + 0.1 + 1 = 2.6$ s.
3. With $I = 30$ s: mean $1.1 + 15 = 16.1$ s, worst $31.6$ s.
4. During a backlog of 600,000 events drained at 5,000 events/s: $T_{\text{queue}}$ grows by 120 s.

**Interpretation.** At default settings the pipeline, not Lucene, dominates freshness, and backlog dominates everything. **Engineering implication.** Publish freshness as a service-level objective (for example 99% of changes searchable within 5 s), measure it end to end by writing canary documents and timing when they become searchable, and alert on consumer lag.
:::

::: mistake
**Mistake — "Kafka gives us exactly-once, so the index is always consistent."** Consumers see events at least once and may restart from older offsets; enrichment lookups may read newer data than the event. Make every index write idempotent with external versions, design documents to be fully rebuilt from current source state, and reconcile periodically by comparing counts or checksums between source and index.
:::

## 16.11 Beyond lexical matching: a bridge to semantic and hybrid search

BM25 matches *words*. It cannot know that "ANC earbuds" and "noise cancelling in-ear headphones" describe the same thing unless synonyms are configured by hand, and the listing in §16.5.4 ranked earbuds above headphones because it understands nothing. **Semantic (dense) retrieval** encodes queries and documents as embedding vectors with a neural model and retrieves nearest neighbors by cosine similarity (§4.9.2), using approximate nearest neighbor (ANN) indexes such as HNSW. It captures meaning but can miss exact identifiers (part numbers, error codes) that BM25 matches perfectly.

**Hybrid retrieval** runs both and fuses the lists. Because BM25 scores and cosine similarities live on different scales (§16.5 misconception), fusion usually uses ranks: **reciprocal rank fusion** adds $1/(60 + \text{rank})$ from each list [Cormack et al. 2009]. A cross-encoder reranker may then reorder the top few dozen. Lucene, Elasticsearch and OpenSearch now include vector fields and ANN search alongside inverted indexes, so one cluster can serve both (as of 2025).

**Figure 16.13 — Hybrid retrieval (preview of Chapters 74–75).**

```mermaid
flowchart LR
  Q([Query]) --> BM[BM25 over<br/>inverted index]
  Q --> EMB[Embedding model]
  EMB --> ANN[ANN search over<br/>vector index]
  BM -->|top 100 by score| RRF[Reciprocal rank fusion]
  ANN -->|top 100 by similarity| RRF
  RRF -->|top 50| RER[Cross-encoder reranker]
  RER --> OUT([Top 10 results])
```

**Reading the diagram.** The query takes two synchronous paths in parallel: lexical retrieval over the inverted index of this chapter, and an embedding model followed by ANN search over a vector index. Each returns its top 100 candidates; rank fusion merges them without comparing raw scores, and an optional reranker spends expensive model inference on only the top 50. The two indexes are separate storage boundaries that must be kept in step by the same indexing pipeline (§16.10.2), with embeddings computed at indexing time. Failure points: the embedding model adds latency and a GPU or CPU dependency on the query path; if it fails, falling back to BM25 alone keeps search available. Chapter 74 covers vector indexes and Chapter 75 covers hybrid retrieval, fusion and reranking in depth.

