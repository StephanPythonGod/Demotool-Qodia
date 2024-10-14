import os
import zipfile
from io import StringIO
from pathlib import Path
from typing import List, Union

import streamlit as st
import xmlschema
from streamlit.runtime.uploaded_file_manager import UploadedFile

from schemas.padnext_v2_py.padx_adl_v2_12 import (
    Rechnungen,  # Replace this with the appropriate import
)
from schemas.padnext_v2_py.padx_auf_v2_12 import (  # Replace this with the appropriate import
    Auftrag,
    DateiTyp,
    VerschluesselungVerfahren,
)
from schemas.padnext_v2_py.padx_basis_v2_12 import (  # Replace this with the appropriate import
    GozifferTyp,
    HumanmedizinTyp,
)
from utils.helpers.encrpyter import (
    calculate_sha1,
    compress_files,
    decrypt_file,
    encrypt_file,
    load_private_key,
    load_public_key,
)
from utils.helpers.files import extract_zip
from utils.helpers.logger import logger
from utils.helpers.transform import (
    format_erstellungsdatum,
    format_kundennummer,
    format_transfernummer,
    transform_df_to_goziffertyp,
)
from utils.helpers.xml import (
    process_xml,
    read_xml_file,
    read_xml_to_object,
    write_object_to_xml,
)
from utils.utils import validate_filenames_match

# Paths to the schema files
SCHEMA_DIR = "schemas/padnext_v2"

# Load the XSD schemas
AUF_XSD_PATH = f"{SCHEMA_DIR}/padx_auf_v2.12.xsd"
PADX_XSD_PATH = f"{SCHEMA_DIR}/padx_adl_v2.12.xsd"


def generate_file_name(auftrag: Auftrag) -> str:
    return f"{format_kundennummer(auftrag.absender.logisch.kundennr)}_{format_erstellungsdatum(auftrag.erstellungsdatum)}_{auftrag.nachrichtentyp.value._value_}_{format_transfernummer(auftrag.transfernr)}"


def generate_pad(df):
    # Generate PAD positions
    goziffern = transform_df_to_goziffertyp(df)
    positionen_obj = create_positionen_object(goziffern)
    output_path = "./data/pad_positionen.xml"
    output_path = write_object_to_xml(positionen_obj, output_path=output_path)
    with open(output_path, "r", encoding="iso-8859-15") as f:
        xml_object = f.read()
    return xml_object


def generate_padnext(df):
    with st.spinner("Generiere PADnext Datei..."):
        # Generate PADnext file based on uploaded PADnext file
        goziffern = transform_df_to_goziffertyp(df)
        positionen_obj = create_positionen_object(goziffern)
        pad_data_ready = update_padnext_positionen(
            padnext_folder=st.session_state.pad_data_path, positionen=positionen_obj
        )
        if isinstance(pad_data_ready, Path):
            return pad_data_ready
        else:
            return False


# Validation Functions
def validate_auf(xml_content: str) -> str:
    """
    Validate the given _auf.xml content against the corresponding XSD schema.

    Args:
        xml_content (str): The XML content as a string.

    Returns:
        str: A detailed report of validation errors, or "Valid" if the XML is valid.
    """
    schema = xmlschema.XMLSchema(AUF_XSD_PATH)
    try:
        schema.validate(StringIO(xml_content))
        return True
    except xmlschema.XMLSchemaValidationError as e:
        logger.error(f"Validation Error in validating pad auf file:\n{e}")
        return False


def validate_padx(xml_content: str) -> str:
    """
    Validate the given _padx.xml content against the corresponding XSD schema.

    Args:
        xml_content (str): The XML content as a string.

    Returns:
        str: A detailed report of validation errors, or "Valid" if the XML is valid.
    """
    schema = xmlschema.XMLSchema(PADX_XSD_PATH)
    try:
        schema.validate(StringIO(xml_content))
        return True
    except xmlschema.XMLSchemaValidationError as e:
        logger.error(f"Validation Error in validating pad padx file:\n{e}")
        return True


def validate_all_files_present(auftrag, extraction_path: Path):
    for datei in auftrag.datei:
        file_path = extraction_path / datei.name
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")


def handle_padnext_upload(file_upload: UploadedFile) -> Path:
    """
    Processes the uploaded .zip file for Padnext, handling both encrypted and unencrypted
    cases and validating contents. The process includes the following steps:

    1. Extract the uploaded .zip file.
    2. Identify and validate the _auf.xml file, which contains metadata and encryption information.
    3. Depending on the encryption method (none or PKCS7), either extract or decrypt
       the _dat_padx.zip file.
    4. Validate the _padx.xml file and ensure consistency with _auf.xml.
    5. Ensure that all files listed in _auf.xml are present in the extracted folder.

    Args:
        file_upload (UploadedFile): A file-like object representing the uploaded .zip file.

    Returns:
        Path: The path to the extracted directory containing all relevant files.

    Raises:
        ValueError: If validation of _auf.xml or _padx.xml fails, or if there's a mismatch between
                    the filenames or missing files in the extracted folder.
        FileNotFoundError: If any expected file listed in _auf.xml is missing.
        Exception: For unsupported or invalid encryption methods.
    """

    # Step 1: Setup a temporary directory for extraction
    temp_dir = Path("temp")

    # Clean the temp directory if it exists
    if temp_dir.exists() and temp_dir.is_dir():
        for item in temp_dir.iterdir():
            if item.is_dir():
                for sub_item in item.iterdir():
                    sub_item.unlink()
                item.rmdir()
            else:
                item.unlink()

    # Create the temp directory
    temp_dir.mkdir(exist_ok=True)

    # Save the uploaded .zip file to the temp directory
    uploaded_zip_path = temp_dir / file_upload.name
    with open(uploaded_zip_path, "wb") as f:
        f.write(file_upload.getvalue())

    # Step 2: Extract the uploaded .zip file
    extracted_files = extract_zip(uploaded_zip_path, temp_dir)

    # Step 3: Process _auf.xml
    auf_file = next(f for f in extracted_files if f.endswith("_auf.xml"))
    auf_xml_path = temp_dir / auf_file
    auf_xml_content = process_xml(
        auf_xml_path, validate_auf, "Validation failed for _auf.xml file."
    )

    # Step 4: Deserialize XML to Auftrag object
    auftrag: Auftrag = read_xml_to_object(auf_xml_path, Auftrag)

    # Step 5: Handle different encryption methods
    if auftrag.verschluesselung.verfahren == VerschluesselungVerfahren.VALUE_0:
        # No encryption
        padx_zip_file = next(f for f in extracted_files if f.endswith("_dat_padx.zip"))
        padx_zip_path = temp_dir / padx_zip_file
        extracted_files = extract_zip(padx_zip_path, temp_dir)

    elif auftrag.verschluesselung.verfahren == VerschluesselungVerfahren.VALUE_1:
        # PKCS7 encryption: Decrypt .p7m file
        padx_p7m_file = next(
            f for f in extracted_files if f.endswith("_dat_padx.zip.p7m")
        )
        padx_p7m_path = temp_dir / padx_p7m_file
        private_key = load_private_key()

        decrypted_zip = temp_dir / "decrypted.zip"
        decrypt_file(padx_p7m_path, decrypted_zip, private_key)

        # Extract the decrypted zip file
        extracted_files = extract_zip(decrypted_zip, temp_dir)

    else:
        raise ValueError("Invalid encryption method specified in _auf.xml file.")

    # Step 6: Process _padx.xml and validate its contents
    padx_file = next(f for f in extracted_files if f.endswith("_padx.xml"))
    padx_xml_path = temp_dir / padx_file
    padx_xml_content = process_xml(
        padx_xml_path, validate_padx, "Validation failed for _padx.xml file."
    )

    # Step 7: Validate filenames match
    validate_filenames_match(auf_xml_path, padx_xml_path)

    # Step 8: Validate _auf and _padx schemas
    if not validate_auf(auf_xml_content):
        raise ValueError("Validation failed for _auf.xml file.")

    if not validate_padx(padx_xml_content):
        raise ValueError("Validation failed for _padx.xml file.")

    # Step 9: Validate if all files listed in _auf.xml are present
    validate_all_files_present(auftrag, temp_dir)

    # Step 10: Return the path to the extracted folder
    return temp_dir


def create_positionen_object(goziffer_objects: List[GozifferTyp]) -> None:
    """
    Serializes a list of GozifferTyp objects into an XML with the desired structure and writes it to the specified file.

    Args:
        goziffer_objects (List[GozifferTyp]): List of GozifferTyp objects to be serialized.
        file_path (str): Path to the output XML file. Defaults to "./data/pad_goziffer_positionen.xml".

    Returns:
        None
    """
    if not goziffer_objects:
        return

    # Create HumanmedizinTyp.Positionen element
    positionen_elem = HumanmedizinTyp.Positionen()
    positionen_elem.goziffer = goziffer_objects
    positionen_elem.posanzahl = len(goziffer_objects)

    return positionen_elem


def add_positionen_to_rechungen(
    rechnungen: Rechnungen, positionen: HumanmedizinTyp.Positionen
) -> Rechnungen:
    """
    Adds a HumanmedizinTyp.Positionen object to an existing Rechnungen object.

    Args:
        rechnungen (Rechnungen): The Rechnungen object to which the Positionen object should be added.
        positionen (HumanmedizinTyp.Positionen): The Positionen object to be added.

    Returns:
        Rechnungen: The updated Rechnungen object.
    """

    rechnungen.rechnung[0].abrechnungsfall[0].humanmedizin.positionen = positionen

    return rechnungen


def update_padnext_positionen(
    padnext_folder: Path, positionen: HumanmedizinTyp.Positionen, encrypt: bool = False
) -> Union[Path, None]:
    """
    Updates the existing _padx.xml file in the specified folder with the provided Positionen object and zips and decrypts the padnext folder.

    Args:
        padnext_folder (Path): Path to the folder containing the _padx.xml file.
        positionen (HumanmedizinTyp.Positionen): The Positionen object to be added to the _padx.xml file.
        encrypt (bool): Flag to determine whether the files should be encrypted. Default is False (no encryption).

    Returns:
        Union[Path, None]: The path to the final PADnext .zip file or None if an error occurred.
    """

    # Step 1: Load the existing _padx.xml file
    padx_file = next(f for f in os.listdir(padnext_folder) if f.endswith("_padx.xml"))
    padx_xml_path = padnext_folder / padx_file

    # Step 2: Deserialize the _padx.xml file to a Rechnungen object
    rechnungen: Rechnungen = read_xml_to_object(padx_xml_path, Rechnungen)

    # Step 3: Add the Positionen object to the Rechnungen object
    rechnungen = add_positionen_to_rechungen(rechnungen, positionen)

    # Step 4: Write the updated Rechnungen object back to the _padx.xml file
    write_object_to_xml(rechnungen, padx_xml_path)

    # Step 5: Create PADnext .zip file
    final_zip_path = padnext_encrypt(padnext_folder, padnext_folder, encrypt=encrypt)

    return final_zip_path


def padnext_encrypt(
    input_folder, output_folder, encrypt: bool = True
) -> Union[Path, None]:
    """
    Main function to handle encryption process for padnext, including reading,
    validation, modification, compression, optional encryption, and final packaging into a .zip file.

    Args:
        input_folder (str): Path to the input folder containing the _auf.xml and other files.
        output_folder (str): Path to the output folder where the encrypted files (or unencrypted if specified) will be stored.
        encrypt (bool): Flag to determine whether the files should be encrypted. Default is True (encrypt).

    Returns:
        Path: Path to the final .zip file or None if an error occurred or None if an Error occured.
    """

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    try:
        # Locate the _auf.xml file
        auf_file = next(f for f in os.listdir(input_folder) if f.endswith("_auf.xml"))
    except StopIteration:
        logger.error(f"No _auf.xml file found in the input folder: {input_folder}")
        return None

    # Read and validate the _auf.xml file
    xml_content = read_xml_file(os.path.join(input_folder, auf_file))
    if not validate_auf(xml_content):
        logger.error(f"Validation failed for _auf.xml file: {auf_file}")
        st.error("Fehler bei der Validierung der pad auf Datei.")
        return None

    try:
        # Load _auf.xml into an Auftrag object
        auftrag: Auftrag = read_xml_to_object(
            os.path.join(input_folder, auf_file), Auftrag
        )

        # Modify 'verschluesselung' based on the encryption flag
        if encrypt:
            # If encryption is enabled, load the public key
            public_key = None
            # certificate = None
            if encrypt:
                try:
                    # TODO: Load the public key and certificate based on the idcert
                    auftrag.verschluesselung.idcert = (
                        "Noch Offen"  # Certificate ID for encryption
                    )
                    public_key = load_public_key()
                    # certificate = load_certificate()
                except Exception as e:
                    logger.error(f"Error loading public key: {e}")
                    return None

            auftrag.verschluesselung.verfahren = "1"  # Indicating encryption is enabled
        else:
            auftrag.verschluesselung.verfahren = "0"  # No encryption
            auftrag.verschluesselung.idcert = "0"  # No certificate
    except Exception as e:
        logger.error(f"Error in loading and modifying _auf.xml file: {e}")
        return None

    # Check for missing 'datei' fields
    if len(auftrag.datei) == 0:
        logger.warning("Warning: No 'datei' fields found in _auf.xml")

    # Update file information and compress files
    files_to_encrypt = []
    try:
        for datei in auftrag.datei:
            file_path = os.path.join(input_folder, datei.name)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Update the _padx.xml file

            if file_path.endswith("_padx.xml"):
                # Change the name of the file in the path to follow the format
                new_file_name = os.path.join(
                    input_folder, f"{generate_file_name(auftrag=auftrag)}_padx.xml"
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
    except FileNotFoundError:
        # If any file is missing, recreate the datei list in the Auftrag object
        for file in os.listdir(input_folder):
            if file.endswith(".pdf", ".png", ".jpg", ".tiff"):
                datei = DateiTyp()
                datei.name = file
                datei.dateilaenge.laenge = os.path.getsize(
                    os.path.join(input_folder, file)
                )
                datei.dateilaenge.pruefsumme = calculate_sha1(
                    os.path.join(input_folder, file)
                )
                auftrag.datei.append(datei)
                files_to_encrypt.append(os.path.join(input_folder, file))
            elif file.endswith("_padx.xml"):
                new_file_name = os.path.join(
                    input_folder, f"{generate_file_name(auftrag=auftrag)}_padx.xml"
                )

                # Rename the file
                os.rename(os.path.join(input_folder, file), new_file_name)

                # Update the file path
                file_path = new_file_name

                datei = DateiTyp()
                datei.name = os.path.basename(file_path)
                datei.dateilaenge.laenge = os.path.getsize(file_path)
                datei.dateilaenge.pruefsumme = calculate_sha1(file_path)
                auftrag.datei.append(datei)
                files_to_encrypt.append(file_path)

    # Compress files into a .zip archive
    compressed_file = os.path.join(
        output_folder, f"{generate_file_name(auftrag=auftrag)}_dat_padx.zip"
    )
    compress_files(files_to_encrypt, compressed_file)

    logger.info(f"Files to encrypt: {files_to_encrypt}")

    # If encryption is enabled, encrypt the compressed file
    if encrypt:
        encrypted_file = f"{compressed_file}.p7m"
        try:
            encrypt_file(compressed_file, encrypted_file, public_key)
        except Exception as e:
            logger.error(f"Error during file encryption: {e}")
            return None
    else:
        encrypted_file = (
            compressed_file  # No encryption, so just use the compressed file as-is
        )

    # Update the _auf.xml file based on modifications
    auf_file = f"{generate_file_name(auftrag=auftrag)}_auf.xml"
    try:
        write_object_to_xml(auftrag, os.path.join(output_folder, auf_file))
    except Exception as e:
        logger.error(f"Error writing updated _auf.xml file: {e}")
        return

    # Create the final padx.zip with the updated _auf.xml and (optionally) encrypted file
    final_zip = os.path.join(
        output_folder, f"{generate_file_name(auftrag=auftrag)}_padx.zip"
    )
    try:
        with zipfile.ZipFile(final_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(
                os.path.join(output_folder, auf_file), auf_file
            )  # Add modified _auf.xml to zip
            zipf.write(
                encrypted_file, os.path.basename(encrypted_file)
            )  # Add encrypted or unencrypted file to zip
    except Exception as e:
        logger.error(f"Error creating final padx.zip: {e}")
        return None

    # Clean up temporary files if encryption was performed
    try:
        os.remove(compressed_file)
        os.remove(encrypted_file)
        os.remove(os.path.join(output_folder, auf_file))
    except Exception as e:
        logger.warning(f"Error during cleanup of temporary files: {e}")

    logger.info(f"Process complete. Output file: {final_zip}")

    # Return the path to the final .zip file as Path object
    final_zip_path = Path(final_zip)
    return final_zip_path
