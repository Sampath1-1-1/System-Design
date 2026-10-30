# Extracted from manuscript/book1-traditional/16-search-systems.md §16.9.2 (listing 6). Edit the manuscript, not this file.
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
