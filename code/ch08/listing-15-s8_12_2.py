# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.12.2 (listing 15). Edit the manuscript, not this file.
# Relation tuples: (object, relation, subject). A subject is a user or a userset "obj#rel".
TUPLES = {
    ("doc:readme", "owner",  "user:alice"),
    ("doc:readme", "parent", "folder:eng"),          # doc lives in a folder
    ("folder:eng", "viewer", "group:eng#member"),    # eng members can view the folder
    ("group:eng",  "member", "user:bob"),
    ("group:eng",  "member", "group:sre#member"),    # nested group
    ("group:sre",  "member", "user:carol"),
}
# Rewrite rules: an editor is an owner or editor; a viewer is an editor,
# or a viewer of the parent folder.
REWRITES = {"editor": ["owner"], "viewer": ["editor", ("parent", "viewer")]}


def check(obj: str, relation: str, user: str, depth: int = 0) -> bool:
    if depth > 25:                                    # guard against cycles
        return False
    for (o, r, s) in TUPLES:
        if o == obj and r == relation:
            if s == user:                             # direct tuple
                return True
            if "#" in s and check(*s.split("#"), user, depth + 1):   # userset
                return True
    for rule in REWRITES.get(relation, []):
        if isinstance(rule, str):                     # same object, implied relation
            if check(obj, rule, user, depth + 1):
                return True
        else:                                         # follow a pointer, e.g. parent
            via, target_rel = rule
            if any(o == obj and r == via and check(s, target_rel, user, depth + 1)
                   for (o, r, s) in TUPLES):
                return True
    return False


print(check("doc:readme", "viewer", "user:alice"))   # True: owner -> editor -> viewer
print(check("doc:readme", "viewer", "user:carol"))   # True: sre in eng; eng views folder
print(check("doc:readme", "editor", "user:bob"))     # False: bob can only view
