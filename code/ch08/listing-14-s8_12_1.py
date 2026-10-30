# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.12.1 (listing 14). Edit the manuscript, not this file.
ROLE_PERMISSIONS = {
    "viewer": {"doc:read"},
    "editor": {"doc:read", "doc:write"},
    "admin":  {"doc:read", "doc:write", "doc:delete", "user:manage"},
}

def rbac_allows(user_roles: set[str], permission: str) -> bool:
    return any(permission in ROLE_PERMISSIONS.get(r, set()) for r in user_roles)

def abac_allows(sub: dict, action: str, res: dict, ctx: dict) -> bool:
    if action == "read":
        return (sub["department"] == res["department"]
                and sub["clearance"] >= res["classification"]
                and 8 <= ctx["hour_utc"] < 20)          # business hours only
    if action == "write":
        return sub["id"] == res["owner_id"]
    return False
