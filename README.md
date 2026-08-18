# santosha

**AES-encrypted steganography disguised as classical Latin prose.**

Santosha encodes arbitrary data — text, files, SSH keys — into authentic-looking Cicero-style Latin text using a Markov chain syllable model. The output is indistinguishable from real Latin at a glance. Decoding requires both the stego text and the correct passphrase.

```
"Moque for!gibus. Erit facitenuisset pericurum possunt. Tatio, de qua nino si
 doctribus catutenus orti aculosocietas belli ficiis deficia percit, eodem est
 etiam una et anino primus suis..."
```
*This is "simple message", encrypted and encoded.*

---

## How it works

```
plaintext → compress → AES-128-GCM → binary → Markov Latin encoding → stego text
stego text → syllable decode → binary → AES decrypt → decompress → plaintext
```

The Markov matrix is trained on Cicero's *De Officiis*. Each bit of the encrypted payload steers syllable selection through the transition model, producing grammatically plausible Latin that carries no statistically detectable signal.

A short header embedded at the start of the output encodes the exact bit count, allowing lossless recovery.

---

## Installation

```bash
pip install cryptography syllabreak zstandard
```

Or use the prebuilt standalone executable (no Python required).

---

## Usage

### Encode
```bash
# From text
python main.py -e -m "your secret message" -o output.txt

# From file
python main.py -e -m secret.pdf -o output.txt

# SSH Ed25519 private key
python main.py -e -m ~/.ssh/id_ed25519 --ssh -o output.txt
```

### Decode
```bash
python main.py -d -m output.txt

# SSH key reconstruction
python main.py -d -m output.txt --ssh
```

Passphrase is always prompted interactively (masked). Pass `-p` for non-interactive use, though this is not recommended.

> **Always use `-o` for file output.** Shell redirection (`>`) on Windows/PowerShell writes UTF-16 with BOM, which corrupts the stego payload.

---

## Options

| Flag | Description |
|---|---|
| `-e` | Encode mode |
| `-d` | Decode mode |
| `-m` | Input: file path or raw text |
| `-o` | Output file (direct write, UTF-8) |
| `-p` | Passphrase (CLI, use with care) |
| `--ssh` | Ed25519 raw key mode |

---

## Build standalone executable

```bash
pyinstaller --noconfirm --clean --onefile --icon=santo.ico \
  --collect-data syllabreak --name santosha main.py
```

---

## Project structure

```
main.py           CLI entry point
encode_decode.py  Markov syllable encoder/decoder
markov_mark.py    Markov chain model & matrix
cryptor.py        AES-128-GCM encrypt/decrypt
compressor.py     Smart compression (zstandard)
main_matrix.py    Compiled syllable transition matrix
cicero.txt        Training corpus
```

---

## Security notes

- Encryption: AES-128-GCM (authenticated). Wrong passphrase → hard failure, no partial decryption.
- Compression is applied before encryption to reduce payload size and increase entropy uniformity.
- The stego text reveals nothing about payload length or content without the passphrase.
- This is a research/personal tool. It has not been audited.

---

## License

MIT