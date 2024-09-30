from pathlib import Path
from typing import Any, List, Tuple, Union

from Levenshtein import distance as levenshtein_distance


def flatten(lst: Union[List[Any], str]) -> List[Any]:
    """
    Recursively flattens a nested list. If the input is a string, returns it as a single-element list.

    Args:
        lst (Union[List[Any], str]): The list to flatten or a string.

    Returns:
        List[Any]: A flattened list or a list containing the input string.
    """
    if isinstance(lst, str):
        return [lst]

    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def clean_zitat(zitat: str) -> List[str]:
    """
    Cleans and splits a zitat string into individual parts, removing unnecessary whitespace and placeholders.

    Args:
        zitat (str): The input zitat string, possibly containing newlines or '[...]' placeholders.

    Returns:
        List[str]: A list of cleaned parts of the zitat.
    """
    lines = zitat.split("\n")
    cleaned_lines = []

    for line in lines:
        parts = line.split("[...]")
        for part in parts:
            cleaned_part = part.strip()
            if cleaned_part:
                cleaned_lines.append(cleaned_part)

    return cleaned_lines


def find_zitat_in_text(
    zitate_to_find: List[Tuple[str, str]],
    annotated_text: List[Union[Tuple[str, str], str]],
    window_size: int = 50,
    distance_threshold: int = 10,
) -> List[Union[Tuple[str, str], str]]:
    """
    Finds and annotates 'zitate' in a given annotated text by matching it to the original text.

    Args:
        zitate_to_find (List[Tuple[str, str]]): List of tuples containing zitate and their associated labels.
        annotated_text (List[Union[Tuple[str, str], str]]): The original annotated text with zitate in it.
        window_size (int): The size of the sliding window in characters for potential matches.
        distance_threshold (int): Maximum Levenshtein distance to consider a match.

    Returns:
        List[Union[Tuple[str, str], str]]: The annotated text with zitate identified and labeled.
    """
    updated_annotated_text = []

    # Join the annotated text to create a single text string
    original_text = "".join(
        [item[0] if isinstance(item, tuple) else item for item in annotated_text]
    )

    # Clean text for matching (remove line breaks, normalize spaces)
    cleaned_text = original_text.replace("\n", " ").replace("  ", " ")

    # Process the quotes to find
    list_of_zitate_to_find = [(clean_zitat(z[0]), z[1]) for z in zitate_to_find]
    list_of_zitate_to_find = [
        (z, zitat_label)
        for zitate, zitat_label in list_of_zitate_to_find
        for z in zitate
    ]

    list_of_indices = []

    # Sliding window with Levenshtein distance for approximate matching
    for zitat, zitat_label in list_of_zitate_to_find:
        cleaned_zitat = zitat.replace("\n", " ").replace("  ", " ")

        # Set up sliding window mechanism
        zitat_len = len(cleaned_zitat)
        best_match = None
        best_distance = float("inf")
        best_match_indices = None

        # Slide over the text in windows of size 'window_size'
        for i in range(len(cleaned_text) - zitat_len + 1):
            window_text = cleaned_text[i : i + zitat_len]

            # Calculate Levenshtein distance between the quote and the window text
            current_distance = levenshtein_distance(cleaned_zitat, window_text)

            if (
                current_distance < best_distance
                and current_distance <= distance_threshold
            ):
                best_distance = current_distance
                best_match = window_text
                best_match_indices = (i, i + zitat_len)

        if best_match:
            start_idx, end_idx = best_match_indices

            # Extend the match to the next blank space if it ends in the middle of a word
            while end_idx < len(cleaned_text) and cleaned_text[end_idx] != " ":
                end_idx += 1

            # Add the match to the list with the adjusted end index
            adjusted_match_text = cleaned_text[start_idx:end_idx]
            list_of_indices.append(
                ((start_idx, end_idx), zitat_label, adjusted_match_text)
            )

    # Sort list of indices by the starting position in the text
    list_of_indices.sort(key=lambda x: x[0][0])

    # Build the annotated text with the found quotes
    if list_of_indices:
        zitat_start = list_of_indices[0][0][0]
        updated_annotated_text.append(original_text[:zitat_start])

    for i, (indices, label, zitat_text) in enumerate(list_of_indices):
        updated_annotated_text.append((zitat_text, label))

        if i < len(list_of_indices) - 1:
            next_start = list_of_indices[i + 1][0][0]
            updated_annotated_text.append(original_text[indices[1] + 1 : next_start])

    if list_of_indices:
        last_end = list_of_indices[-1][0][1]
        if last_end < len(original_text):
            updated_annotated_text.append(original_text[last_end:])

    return updated_annotated_text or annotated_text


def ziffer_from_options(ziffer_option: Union[List[str], str]) -> List[str]:
    """
    Extracts the ziffer (numeric part) from a string or list of strings.

    Args:
        ziffer_option (Union[List[str], str]): A string or list of strings containing ziffer options.

    Returns:
        List[str]: A list of extracted ziffer values.
    """
    if isinstance(ziffer_option, list):
        return [i.split(" - ")[0] for i in ziffer_option]
    elif isinstance(ziffer_option, str):
        return [ziffer_option.split(" - ")[0]]
    return []


def validate_filenames_match(auf_xml_path: Path, padx_xml_path: Path):
    """
    Validates that the filenames of the provided XML paths match after removing specific suffixes.

    This function checks if the filenames (excluding the '_auf' and '_padx' suffixes) of the provided
    `auf_xml_path` and `padx_xml_path` are identical. If they do not match, a ValueError is raised.

    Args:
        auf_xml_path (Path): The path to the '_auf' XML file.
        padx_xml_path (Path): The path to the '_padx' XML file.

    Raises:
        ValueError: If the filenames do not match after removing the '_auf' and '_padx' suffixes.
    """
    if auf_xml_path.stem.replace("_auf", "") != padx_xml_path.stem.replace("_padx", ""):
        raise ValueError("Mismatch between _auf.xml and _padx.xml filenames.")
