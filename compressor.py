import zlib
from encode_decode import text2bin

test = text2bin("NO MORE LIKE THAT BECAUSE OF IT, AND WE KNOW NO MORE LIKE THAT ARE FROM HATE AND LOVE TO EACH OTHER")

def bin2bytes(bits):
    """On pack les bits dans bytes"""
    mod_bits = bits
    if mod_bits[0:2] == "0b": mod_bits = bits[2:]
    # print(mod_bits)
    byte_array = bytes(int(mod_bits[i: i + 8], 2) for i in range(0, len(mod_bits), 8))
    return byte_array

def bytes2bin(data: bytes) -> str:
    """Convertit un objet bytes en chaîne de bits commençant par '0b'."""
    return "0b" + "".join(f"{byte:08b}" for byte in data)


packed = (bin2bytes(test))

def smart_compress(data: bytes) -> bytes:
    """Compresse au maximum avec Zlib (niveau 9).

    Ne conserve la compression que si elle réduit réellement la taille.
    """
    # Compression Zlib niveau 9 (maximum)
    compressed = zlib.compress(data, level=9)

    # Si le gain est présent, on garde la compression
    if len(compressed) < len(data):
        # print("COMPRESSION")
        return b"\x01" + compressed  # Flag 0x01 = Données Zlib
    else:
        # print("PAS DE COMPRESSION")
        return b"\x00" + data  # Flag 0x00 = Données Brutes


def smart_decompress(data: bytes) -> bytes:
    """Décompresse selon le flag d'en-tête (0x01 ou 0x00)."""
    flag = data[0:1]
    payload = data[1:]

    if flag == b"\x01":
        return zlib.decompress(payload)
    elif flag == b"\x00":
        return payload
    else:
        raise ValueError("Format de compression inconnu ou corrompu.")
    
cp = smart_compress(packed)