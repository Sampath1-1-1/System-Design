# Extracted from manuscript/book1-traditional/10-security-fundamentals.md §10.4.8 (listing 2). Edit the manuscript, not this file.
"""AES-256-GCM with associated data, Ed25519 signatures and X25519 key agreement."""
import os
from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# --- 1. Authenticated symmetric encryption: AES-256-GCM ---
key = AESGCM.generate_key(bit_length=256)
aead = AESGCM(key)
nonce = os.urandom(12)                       # 96-bit nonce; NEVER reuse with same key
aad = b"user_id=42;table=payments"           # authenticated but not encrypted
ct = aead.encrypt(nonce, b"card ending 4242", aad)
print("ciphertext+tag bytes:", len(ct))      # plaintext length + 16-byte tag
print("decrypted:", aead.decrypt(nonce, ct, aad))
try:
    aead.decrypt(nonce, ct, b"user_id=43;table=payments")   # wrong context
except InvalidTag:
    print("AAD mismatch -> InvalidTag (ciphertext cannot be moved to another row)")
tampered = bytearray(ct); tampered[0] ^= 1
try:
    aead.decrypt(nonce, bytes(tampered), aad)
except InvalidTag:
    print("bit flip -> InvalidTag")

# --- 2. Digital signatures: Ed25519 ---
signing_key = Ed25519PrivateKey.generate()
verify_key = signing_key.public_key()
release = b"release v2.4.1 sha256=9f86d08..."
sig = signing_key.sign(release)
print("signature bytes:", len(sig))
verify_key.verify(sig, release)              # raises if invalid
try:
    verify_key.verify(sig, release + b"!")
except InvalidSignature:
    print("modified message -> InvalidSignature")

# --- 3. Key agreement: X25519 + HKDF ---
alice, bob = X25519PrivateKey.generate(), X25519PrivateKey.generate()
shared_a = alice.exchange(bob.public_key())  # only public keys cross the network
shared_b = bob.exchange(alice.public_key())
assert shared_a == shared_b
session_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                   info=b"example-protocol v1 session key").derive(shared_a)
print("both sides derived the same 256-bit session key:", session_key.hex()[:16], "...")
