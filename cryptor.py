import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# Paramètres de sécurité
ITERATIONS = 600_000  # Recommandation OWASP pour PBKDF2-HMAC-SHA256
SALT_SIZE = 16        # 16 octets (128 bits) de sel aléatoire
NONCE_SIZE = 12       # 12 octets (96 bits) de nonce pour AES-GCM
KEY_SIZE = 16         # 16 octets = 128 bits pour AES-128


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Dérive une clé AES-128 (16 octets) à partir d'une passphrase avec PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(passphrase.encode("utf-8"))


def encrypt_aes128(data: bytes, passphrase: str) -> bytes:
    """Chiffre les octets avec AES-128-GCM.
    
    Structure produite : [16 octets Sel] + [12 octets Nonce] + [Ciphertext + Tag]
    """
    # 1. Génération du sel et dérivation de la clé
    salt = os.urandom(SALT_SIZE)
    key = derive_key(passphrase, salt)

    # 2. Génération du nonce et chiffrement
    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, associated_data=None)

    # 3. Concaténation des briques en un unique flux de bytes
    return salt + nonce + ciphertext


def decrypt_aes128(encrypted_payload: bytes, passphrase: str) -> bytes:
    """Déchiffre un payload AES-128-GCM en utilisant la passphrase."""
    # 1. Extraction des métadonnées
    salt = encrypted_payload[:SALT_SIZE]
    nonce = encrypted_payload[SALT_SIZE : SALT_SIZE + NONCE_SIZE]
    ciphertext = encrypted_payload[SALT_SIZE + NONCE_SIZE :]

    # 2. Dérivation de la clé identique
    key = derive_key(passphrase, salt)

    # 3. Déchiffrement et vérification de l'intégrité (Tag GCM)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data=None)




############################################################
# SSH RELATED ONLY
############################################################


from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_ssh_private_key,
)


def extract_raw_ed25519(pem_data: bytes) -> bytes:
    """Extraie les 32 octets bruts d'une clé privée Ed25519 OpenSSH/PEM."""
    key = load_ssh_private_key(pem_data, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError(
            "Seules les clés Ed25519 sont supportées pour la réduction brute."
        )

    # Renvoie exactement 32 octets
    return key.private_bytes(
        encoding=Encoding.Raw,
        format=PrivateFormat.Raw,
        encryption_algorithm=NoEncryption(),
    )


def reconstruct_pem_ed25519(raw_bytes: bytes) -> str:
    """Reconstruit une clé privée OpenSSH au format PEM à partir des 32 octets bruts."""
    if len(raw_bytes) != 32:
        raise ValueError(f"Taille de clé invalide : {len(raw_bytes)} (32 octets attendus)")

    key = Ed25519PrivateKey.from_private_bytes(raw_bytes)
    pem_bytes = key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.OpenSSH,
        encryption_algorithm=NoEncryption(),
    )
    return pem_bytes.decode("utf-8")