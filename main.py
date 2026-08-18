import argparse
import getpass
import os
import sys


from markov_mark import *
from encode_decode import *
from compressor import *
from cryptor import *


def in_message(message, passphrase, verbose = False):
    # 2. Compression
    raw_bytes = message.encode("utf-8")
    compressed_bytes = smart_compress(raw_bytes)
    
    # 3. Chiffrement
    encrypted_payload = encrypt_aes128(compressed_bytes, passphrase)
    encoded_latin = encode_chain(no1char(bytes2bin(encrypted_payload)), False)
    
    if verbose:
        print("Encoded latin:\n", encoded_latin)
        print("Taille encoded latin (bytes):", len(encoded_latin))

        print("Taille initiale (bytes)   :", len(raw_bytes))
        print("Taille compressée (bytes) :", len(compressed_bytes))
        print("Taille chiffrée (bytes)   :", len(encrypted_payload)) 

    return encoded_latin


def verifier(latin_message, passphrase):
    try:
        result = out_message(latin_message, passphrase)
        # print(result)
        return result is not None and len(result) > 0
    except Exception:
        return False


def out_message(latin_message, passphrase):

    # --- DÉCHIFFREMENT ---
    encrypted_payload = bin2bytes(decoder(decode_chain(latin_message), int(decoder_header(latin_message),2)))
    decrypted_compressed = decrypt_aes128(encrypted_payload, passphrase)
    decompressed_bytes = smart_decompress(decrypted_compressed)
    final_message = decompressed_bytes.decode("utf-8")
    
    return final_message

# zen = "Monis, quam!flammaximam misque sunt omni minem conferre. Catur, quem agros ferta obscemus, concidunt amissi id esset, gravideconiugi, in eiusmodi possit, ut id sophorum veniat et fortis intellerit, ut et mutanta tecum habere persobrinobitranquilliqui losocietate ferri si nos studiosum sit silio cernatu propoteneque eoque et "
""" alpha = in_message("simple message", "carmen")
print("This is before all the steps:",alpha)
omega = out_message(alpha, "carmen")
print("This is after all the steps:", omega)
print("----------------------------------------") """

 



def resolve_input(input_arg: str | None) -> bytes:
    """Détecte dynamiquement si l'entrée est un fichier, du texte brut ou un pipe STDIN."""
    if input_arg:
        if os.path.isfile(input_arg):
            with open(input_arg, "rb") as f:
                return f.read()
        return input_arg.encode("utf-8")
    elif not sys.stdin.isatty():
        return sys.stdin.read().encode("utf-8")
    else:
        raise ValueError("Aucune donnée d'entrée fournie.")


def get_passphrase(cli_pass: str | None) -> str:
    """Récupère le mot de passe silencieusement sans laisser de trace dans l'historique shell."""
    if cli_pass:
        return cli_pass
    # getpass lit sur /dev/tty (Linux) ou CON (Windows), totalement indépendant des pipes
    return getpass.getpass("Passphrase AES (masquée) : ")


def main():
    parser = argparse.ArgumentParser(description="Stéganographie Markov-AES & SSH Zero-Disk")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--encode", action="store_true", help="Mode Encodage")
    group.add_argument("-d", "--decode", action="store_true", help="Mode Décodage")

    parser.add_argument("-m", "--message", help="Fichier source OU texte brut (si omis, lit STDIN)")
    parser.add_argument("-p", "--passphrase", help="Passphrase (déconseillé en CLI, utiliser le prompt masqué)")
    parser.add_argument("--ssh", action="store_true", help="Activer le mode Clé SSH Ed25519 brute")
    parser.add_argument("-o", "--output", help="Fichier de sortie (écriture directe, bypass toute redirection shell)")

    args = parser.parse_args()

    try:
        raw_input = resolve_input(args.message)
        pwd = get_passphrase(args.passphrase)

        if args.encode:
            # 1. Préparation des bytes (Clé SSH Brute ou Texte/Fichier)
            if args.ssh:
                payload_bytes = extract_raw_ed25519(raw_input)
                sys.stderr.write("[+] Clé Ed25519 réduite à 32 octets bruts.\n")
            else:
                payload_bytes = raw_input

            # 2. Compression & Chiffrement
            compressed = smart_compress(payload_bytes)
            encrypted = encrypt_aes128(compressed, pwd)

            # 3. Encodage Stégo Markov
            bits = no1char(bytes2bin(encrypted))
            result = encode_chain(bits, False)
            # print("This is the verifier:",verifier(result, pwd))
            if args.output:
                with open(args.output, "w", encoding="ASCII", newline="\n") as f:
                    f.write(result)
                sys.stderr.write(f"[+] Écrit dans {args.output}\n")
            else:
                sys.stdout.write(result + "\n")

        elif args.decode:
            # 1. Décodage Stégo Markov -> AES -> Décompression
            # 'utf-8-sig' absorbe le BOM PowerShell automatiquement SANS altérer le texte
            if raw_input.startswith(b"\xff\xfe") or raw_input.startswith(b"\xfe\xff"):
                latin_str = raw_input.decode("utf-16").strip()
            else:
                latin_str = raw_input.decode("utf-8-sig").strip()
            # latin_str = raw_input.decode("utf-16").replace("\r\n", "\n").replace("\r", "").strip()
            nbits = int(decoder_header(latin_str), 2)
            bits_str = decoder(decode_chain(latin_str), nbits, False)

            encrypted_payload = bin2bytes(bits_str)
            decrypted_compressed = decrypt_aes128(encrypted_payload, pwd)
            decompressed_bytes = smart_decompress(decrypted_compressed)

            # 2. Reconstitution (Clé SSH PEM ou Texte)
            if args.ssh:
                final_output = reconstruct_pem_ed25519(decompressed_bytes)
            else:
                final_output = decompressed_bytes.decode("utf-8")

            # Sortie propre sur STDOUT (prêt pour SSH ou redirection)
            sys.stdout.write(final_output)

    except Exception as e:
        sys.stderr.write(f"\n[ERREUR] : {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()