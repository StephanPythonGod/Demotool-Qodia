import hashlib
import os
import zipfile
from xml.etree import ElementTree as ET

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from xsdata.formats.dataclass.parsers import XmlParser

from schemas.padnext_v2_py.padx_auf_v2_12 import Auftrag
from utils.helpers.padnext import write_object_to_xml
from utils.helpers.transform import (
    format_erstellungsdatum,
    format_kundennummer,
    format_transfernummer,
)

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


def padnext_encrypt(input_folder, output_folder):
    # Load the public key
    with open("ssl/public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(), backend=default_backend()
        )

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Parse the _auf.xml file
    auf_file = next(f for f in os.listdir(input_folder) if f.endswith("_auf.xml"))
    parser = XmlParser()

    try:
        with open(os.path.join(input_folder, auf_file), "rb") as f:
            xml_content = f.read()

        # Decode the content explicitly
        xml_string = xml_content.decode("iso-8859-15")
        print(f"Successfully read XML file: {auf_file}")
        print(f"XML content length: {len(xml_string)} characters")

        # Check if the XML is well-formed
        try:
            ET.fromstring(xml_string)
            print("XML is well-formed")
        except ET.ParseError as pe:
            print(f"XML is not well-formed: {pe}")
            # Optionally, print the problematic part of the XML
            print(xml_string[max(0, pe.position[0] - 100) : pe.position[0] + 100])

        # Use FromString method with explicit encoding
        auftrag: Auftrag = parser.from_string(xml_string, Auftrag)
        print("Successfully parsed XML content")
    except UnicodeDecodeError as ude:
        print(f"Error decoding XML file: {ude}")
        raise
    except Exception as e:
        print(f"Error reading or parsing XML file: {e}")
        raise

    # Check for missing 'datei' fields
    if len(auftrag.datei) == 0:
        print("Warning: No 'datei' fields found in _auf.xml")

    # Update file information and compress files
    files_to_encrypt = []
    for datei in auftrag.datei:
        file_path = os.path.join(input_folder, datei.name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Update the _padx.xml file

        if file_path.endswith("_padx.xml"):
            # Change the name of the file in the path to follow the format
            print(
                f"Erstellungsdatum: {format_erstellungsdatum(auftrag.erstellungsdatum)}"
            )
            new_file_name = os.path.join(
                input_folder,
                f"{format_kundennummer(auftrag.absender.logisch.kundennr)}_{format_erstellungsdatum(auftrag.erstellungsdatum)}_{auftrag.nachrichtentyp.value._value_}_{format_transfernummer(auftrag.transfernr)}_padx.xml",
            )

            # Rename the file
            os.rename(file_path, new_file_name)

            # Update the file path
            file_path = new_file_name

            datei.name = os.path.basename(file_path)

        file_size = os.path.getsize(file_path)
        checksum = calculate_sha1(file_path)

        datei.dateilaenge.laenge = file_size
        datei.dateilaenge.pruefsumme = checksum

        files_to_encrypt.append(file_path)

    print("Files to encrypt:")
    print(files_to_encrypt)

    # Compress files
    compressed_file = os.path.join(
        output_folder,
        f"{format_kundennummer(auftrag.absender.logisch.kundennr)}_{format_erstellungsdatum(auftrag.erstellungsdatum)}_{auftrag.nachrichtentyp.value._value_}_{format_transfernummer(auftrag.transfernr)}_dat_padx.zip",
    )
    compress_files(files_to_encrypt, compressed_file)

    # Encrypt the compressed file
    encrypted_file = f"{compressed_file}.p7m"
    encrypt_file(compressed_file, encrypted_file, public_key)

    # Update the _auf.xml file
    auf_file = f"{format_kundennummer(auftrag.absender.logisch.kundennr)}_{format_erstellungsdatum(auftrag.erstellungsdatum)}_{auftrag.nachrichtentyp.value._value_}_{format_transfernummer(auftrag.transfernr)}_auf.xml"
    write_object_to_xml(auftrag, os.path.join(output_folder, auf_file))

    # Create the final padx.zip
    final_zip = os.path.join(
        output_folder,
        f"{format_kundennummer(auftrag.absender.logisch.kundennr)}_{format_erstellungsdatum(auftrag.erstellungsdatum)}_{auftrag.nachrichtentyp.value._value_}_{format_transfernummer(auftrag.transfernr)}_padx.zip",
    )
    with zipfile.ZipFile(final_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(os.path.join(output_folder, auf_file), auf_file)
        zipf.write(encrypted_file, os.path.basename(encrypted_file))

    # Clean up temporary files
    os.remove(compressed_file)
    os.remove(encrypted_file)
    os.remove(os.path.join(output_folder, auf_file))

    print(f"Encryption complete. Output file: {final_zip}")


if __name__ == "__main__":
    input_folder = "tests/padnext/test - own"
    output_folder = "tests/padnext/test - own - encrypted"
    padnext_encrypt(input_folder, output_folder)
