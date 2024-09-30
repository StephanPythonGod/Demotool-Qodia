import hashlib
import os
import zipfile

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from schemas.padnext_v2_py.padx_auf_v2_12 import Auftrag
from utils.helpers.padnext import read_xml_to_object

# Add the project root to the Python path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# sys.path.insert(0, project_root)


def calculate_sha1(filename):
    sha1 = hashlib.sha1()
    with open(filename, "rb") as f:
        while True:
            data = f.read(65536)  # Read in 64kb chunks
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


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


def padnext_decrypt(input_file, output_folder):
    # Load the private key
    with open("ssl/private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Extract the padx.zip
    with zipfile.ZipFile(input_file, "r") as zip_ref:
        zip_ref.extractall(output_folder)

    # Find the _auf.xml file
    auf_file = next(f for f in os.listdir(output_folder) if f.endswith("_auf.xml"))

    # Parse the _auf.xml file
    auftrag: Auftrag = read_xml_to_object(
        os.path.join(output_folder, auf_file), Auftrag
    )

    # Check for missing 'datei' fields
    if len(auftrag.datei) == 0:
        print("Warning: No 'datei' fields found in _auf.xml")

    # Find the encrypted .p7m file
    encrypted_file = next(f for f in os.listdir(output_folder) if f.endswith(".p7m"))
    encrypted_path = os.path.join(output_folder, encrypted_file)

    # Decrypt the .p7m file
    decrypted_zip = os.path.join(output_folder, "decrypted.zip")
    decrypt_file(encrypted_path, decrypted_zip, private_key)

    # Extract the decrypted zip file
    with zipfile.ZipFile(decrypted_zip, "r") as zip_ref:
        zip_ref.extractall(output_folder)

    # Verify file integrity
    for datei in auftrag.datei:
        file_path = os.path.join(output_folder, datei.name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        checksum = calculate_sha1(file_path)

        if file_size != datei.dateilaenge.laenge:
            raise ValueError(
                f"File size mismatch for {datei.name}: expected {datei.dateilaenge.laenge}, got {file_size}"
            )

        if checksum != datei.dateilaenge.pruefsumme:
            raise ValueError(
                f"Checksum mismatch for {datei.name}: expected {datei.dateilaenge.pruefsumme}, got {checksum}"
            )

    # Clean up temporary files
    os.remove(encrypted_path)
    os.remove(decrypted_zip)

    print(f"Decryption complete. Output folder: {output_folder}")


if __name__ == "__main__":
    input_file = "/Users/lenert/Development/Demotool/tests/padnext/encrypted_output/00666666_20170824_ADL_100004_padx.zip"
    output_folder = "tests/padnext/decrypted_output"
    padnext_decrypt(input_file, output_folder)
