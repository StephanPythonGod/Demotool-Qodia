import os
import uuid
import zipfile
from pathlib import Path
from typing import List

from streamlit.proto.Common_pb2 import FileURLs
from streamlit.runtime.uploaded_file_manager import UploadedFile, UploadedFileRec


# Helper function to extract .zip file and return the list of files in the directory
def extract_zip(zip_path: Path, destination: Path) -> list:
    """
    Extracts the contents of a zip file to a specified destination directory.

    Args:
        zip_path (Path): The path to the zip file to be extracted.
        destination (Path): The path to the directory where the contents will be extracted.

    Returns:
        list: A list of filenames in the destination directory after extraction.
    """
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(destination)
    return os.listdir(destination)


def list_files_by_extension(folder_path: Path, extensions: List[str]) -> List[Path]:
    """
    Returns all files in the folder that match the given extensions.

    Args:
        folder_path (Path): Path to the folder to search.
        extensions (List[str]): List of file extensions to filter by.

    Returns:
        List[Path]: List of Paths to files with the given extensions.
    """
    all_files = os.listdir(folder_path)
    return [folder_path / f for f in all_files if f.endswith(tuple(extensions))]


def load_file_from_path(file_path: Path) -> UploadedFile:
    """
    Load a file from a given path and return it as an UploadedFile object.

    Args:
        file_path (Path): The path to the file.

    Returns:
        UploadedFile: An UploadedFile object containing the file data.

    Raises:
        ValueError: If the file type is not supported.
    """
    supported_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"}
    if file_path.suffix.lower() not in supported_extensions:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    with open(file_path, "rb") as file:
        file_contents = file.read()

    file_type = file_path.suffix.lower()
    if file_type in {".png", ".jpg", ".jpeg", ".tiff", ".tif"}:
        mime_type = f"image/{file_type[1:]}"
    elif file_type == ".pdf":
        mime_type = "application/pdf"
    else:
        raise ValueError(f"Unexpected file type: {file_type}")

    # Create an UploadedFileRec object
    file_id = str(uuid.uuid4())
    uploaded_file_rec = UploadedFileRec(
        file_id=file_id, name=file_path.name, type=mime_type, data=file_contents
    )

    # Create a FileURLs object (with dummy URLs as we don't have actual URLs)
    file_urls = FileURLs(file_id=file_id, upload_url="", delete_url="")

    # Create and return the UploadedFile object
    return UploadedFile(uploaded_file_rec, file_urls)


def create_uploaded_file_from_binary(
    binary_data: bytes, file_name: str, mime_type: str
) -> UploadedFile:
    """
    Create an UploadedFile object from binary data, file name, and MIME type.

    Args:
        binary_data (bytes): The binary data of the file.
        file_name (str): The name of the file.
        mime_type (str): The MIME type of the file.

    Returns:
        UploadedFile: An UploadedFile object containing the file data.
    """
    file_id = str(uuid.uuid4())
    uploaded_file_rec = UploadedFileRec(
        file_id=file_id, name=file_name, type=mime_type, data=binary_data
    )
    file_urls = FileURLs(file_id=file_id, upload_url="", delete_url="")
    return UploadedFile(uploaded_file_rec, file_urls)
