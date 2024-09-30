import hashlib
import os
import zipfile

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from utils.helpers.logger import logger


def calculate_sha1(filename):
    sha1 = hashlib.sha1()
    with open(filename, "rb") as f:
        while True:
            data = f.read(65536)  # Read in 64kb chunks
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def compress_files(files, output_zip):
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))


def encrypt_file(input_file, output_file, public_key):
    with open(input_file, "rb") as f:
        data = f.read()

    # Generate a random AES key
    aes_key = os.urandom(32)

    # Encrypt the AES key with the public key
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Generate a random IV
    iv = os.urandom(16)

    # Encrypt the data with AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()

    # Write the encrypted data to the output file
    with open(output_file, "wb") as f:
        f.write(len(encrypted_key).to_bytes(4, byteorder="big"))
        f.write(encrypted_key)
        f.write(iv)
        f.write(encrypted_data)


def load_private_key(serial_number: str = None):
    # Load the private key
    with open("ssl/private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )
    return private_key


def load_certificate(serial_number: str = None):
    # Load the certificate
    with open("ssl/certificate.pem", "rb") as cert_file:
        cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
    return cert


def load_public_key(serial_number: str = None):
    """Load the public key for encryption."""
    try:
        with open("ssl/public_key.pem", "rb") as key_file:
            return serialization.load_pem_public_key(
                key_file.read(), backend=default_backend()
            )
    except Exception as e:
        logger.error(f"Error loading public key: {e}")
        raise


def decrypt_file(input_file, output_file, private_key):
    with open(input_file, "rb") as f:
        # Read the encrypted key length
        key_length = int.from_bytes(f.read(4), byteorder="big")

        # Read and decrypt the AES key
        encrypted_key = f.read(key_length)
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Read the IV
        iv = f.read(16)

        # Read the encrypted data
        encrypted_data = f.read()

    # Decrypt the data with AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Write the decrypted data to the output file
    with open(output_file, "wb") as f:
        f.write(decrypted_data)
