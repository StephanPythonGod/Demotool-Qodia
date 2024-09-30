from pathlib import Path

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig


def read_xml_file(filepath: str, encoding: str = "ISO-8859-15") -> str:
    """
    Reads an XML file using the specified encoding.

    Args:
        filepath (str): Path to the XML file.
        encoding (str): The encoding of the XML file (default is 'ISO-8859-15').

    Returns:
        str: The XML content as a string.
    """
    with open(filepath, "r", encoding=encoding) as file:
        return file.read()


def read_xml_to_object(file_path: str, dataclass_type):
    """
    Parses an XML file and converts it into a Python object of the specified dataclass type.

    Args:
        file_path (str): Path to the XML file.
        dataclass_type: The dataclass type to which the XML should be converted.

    Returns:
        object: An instance of the specified dataclass type populated with data from the XML file.
    """
    parser = XmlParser()

    # Read XML into a Python object
    with open(file_path, "r", encoding="iso-8859-15") as f:
        xml_object = parser.from_string(f.read(), dataclass_type)

    return xml_object


def write_object_to_xml(obj, output_path: str):
    """
    Serializes a Python object to an XML file with pre-processing to replace non-encodable characters.

    Args:
        obj: The Python object to serialize.
        output_path (str): Path where the XML file will be written.

    Returns:
        str: The path to the written XML file.
    """
    # Create a serializer configuration for pretty printing
    config = SerializerConfig(pretty_print=True)

    # Create the serializer with the configuration
    serializer = XmlSerializer(config=config)

    # Serialize the object to an XML string
    xml_str = serializer.render(obj)

    # Optionally replace specific problematic characters with suitable replacements
    xml_str = xml_str.replace("–", "-")  # Replace en dash with hyphen
    # Add more replacements as needed

    # Encode to iso-8859-15 with 'replace' to substitute unencodable characters
    encoded_xml_str = xml_str.encode("iso-8859-15", errors="replace").decode(
        "iso-8859-15"
    )

    # Write the processed XML to file
    with open(output_path, "w", encoding="iso-8859-15") as f:
        f.write(encoded_xml_str)

    return output_path


def process_xml(xml_path: Path, validator_func, error_message: str):
    """
    Processes an XML file by reading its content and validating it using a provided function.

    Args:
        xml_path (Path): Path to the XML file.
        validator_func (function): A function that takes the XML content as input and returns a boolean indicating its validity.
        error_message (str): The error message to raise if validation fails.

    Returns:
        str: The XML content as a string.

    Raises:
        ValueError: If the XML content does not pass validation.
    """
    xml_content = read_xml_file(xml_path)
    if not validator_func(xml_content):
        raise ValueError(error_message)
    return xml_content
