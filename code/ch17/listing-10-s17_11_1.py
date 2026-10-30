# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.11.1 (listing 10). Edit the manuscript, not this file.
import heapq

class TrieNode:
    __slots__ = ("children", "weight")
    def __init__(self):
        self.children, self.weight = {}, 0              # weight > 0 marks the end of a stored word

class Trie:
    def __init__(self):
        self.root, self.nodes = TrieNode(), 1

    def insert(self, word: str, weight: int) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
                self.nodes += 1
            node = node.children[ch]
        node.weight += weight

    def top_k(self, prefix: str, k: int):
        """Walk to the prefix node (O(len(prefix))), then collect its subtree's k heaviest words."""
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return []
        found, stack = [], [(node, prefix)]
        while stack:
            cur, word = stack.pop()
            if cur.weight:
                found.append((cur.weight, word))
            stack.extend((child, word + ch) for ch, child in cur.children.items())
        return heapq.nlargest(k, found)

t = Trie()
for word, w in [("system", 90), ("systems", 40), ("syscall", 25), ("sync", 60),
                ("synchronous", 30), ("syntax", 20), ("scale", 80), ("schema", 50)]:
    t.insert(word, w)
print(t.top_k("sy", 3))
print(t.top_k("syn", 5))
print("nodes:", t.nodes, "for", sum(len(w) for w in ["system", "systems", "syscall", "sync",
      "synchronous", "syntax", "scale", "schema"]), "characters")
