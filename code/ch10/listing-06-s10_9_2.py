# Extracted from manuscript/book1-traditional/10-security-fundamentals.md §10.9.2 (listing 6). Edit the manuscript, not this file.
"""Envelope encryption with a simulated KMS (the KEK never leaves the 'KMS')."""
import json
import os
from dataclasses import dataclass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class FakeKMS:
    """Stands in for AWS KMS / Cloud KMS / Vault Transit. Holds KEKs internally."""
    def __init__(self):
        self._keks = {"kek-2026-10": AESGCM.generate_key(bit_length=256)}
        self.current = "kek-2026-10"

    def generate_data_key(self, context: dict) -> tuple[bytes, dict]:
        dek = AESGCM.generate_key(bit_length=256)            # fresh DEK per object
        nonce = os.urandom(12)
        aad = json.dumps(context, sort_keys=True).encode()   # "encryption context"
        wrapped = AESGCM(self._keks[self.current]).encrypt(nonce, dek, aad)
        return dek, {"kek_id": self.current, "nonce": nonce.hex(), "wrapped": wrapped.hex()}

    def decrypt_data_key(self, blob: dict, context: dict) -> bytes:
        aad = json.dumps(context, sort_keys=True).encode()
        return AESGCM(self._keks[blob["kek_id"]]).decrypt(
            bytes.fromhex(blob["nonce"]), bytes.fromhex(blob["wrapped"]), aad)

    def rotate(self) -> None:
        new_id = f"kek-{len(self._keks) + 1}"
        self._keks[new_id] = AESGCM.generate_key(bit_length=256)
        self.current = new_id                                 # old KEKs kept for decrypt

    def rewrap(self, blob: dict, context: dict) -> dict:
        """Re-encrypt a DEK under the current KEK without touching the data."""
        dek = self.decrypt_data_key(blob, context)
        nonce = os.urandom(12)
        aad = json.dumps(context, sort_keys=True).encode()
        return {"kek_id": self.current, "nonce": nonce.hex(),
                "wrapped": AESGCM(self._keks[self.current]).encrypt(nonce, dek, aad).hex()}

@dataclass
class EncryptedObject:
    wrapped_dek: dict
    nonce: bytes
    ciphertext: bytes

def encrypt_object(kms: FakeKMS, plaintext: bytes, context: dict) -> EncryptedObject:
    dek, wrapped = kms.generate_data_key(context)             # 1 KMS call per object
    nonce = os.urandom(12)
    ct = AESGCM(dek).encrypt(nonce, plaintext, None)          # bulk data encrypted locally
    del dek                                                   # drop plaintext DEK ASAP
    return EncryptedObject(wrapped, nonce, ct)

def decrypt_object(kms: FakeKMS, obj: EncryptedObject, context: dict) -> bytes:
    dek = kms.decrypt_data_key(obj.wrapped_dek, context)
    return AESGCM(dek).decrypt(obj.nonce, obj.ciphertext, None)

if __name__ == "__main__":
    kms = FakeKMS()
    ctx = {"tenant": "acme", "object": "invoices/2026-10.pdf"}
    data = os.urandom(5_000_000)                              # 5 MB document
    obj = encrypt_object(kms, data, ctx)
    assert decrypt_object(kms, obj, ctx) == data
    print("round trip OK; wrapped DEK is", len(bytes.fromhex(obj.wrapped_dek["wrapped"])), "bytes")

    kms.rotate()
    obj.wrapped_dek = kms.rewrap(obj.wrapped_dek, ctx)        # rotate KEK: rewrap ~60 bytes,
    assert decrypt_object(kms, obj, ctx) == data              # not re-encrypt 5 MB
    print("after KEK rotation, DEK now wrapped by", obj.wrapped_dek["kek_id"])

    try:
        decrypt_object(kms, obj, {"tenant": "evil", "object": "invoices/2026-10.pdf"})
    except Exception as e:
        print("wrong encryption context ->", type(e).__name__)
