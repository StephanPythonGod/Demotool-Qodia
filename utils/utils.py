import re
from typing import Any, List, Tuple, Union

from fuzzywuzzy import fuzz


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
) -> List[Union[Tuple[str, str], str]]:
    """
    Finds and annotates 'zitate' in a given annotated text by matching it to the original text.

    Args:
        zitate_to_find (List[Tuple[str, str]]): List of tuples containing zitate and their associated labels.
        annotated_text (List[Union[Tuple[str, str], str]]): The original annotated text with zitate in it.

    Returns:
        List[Union[Tuple[str, str], str]]: The annotated text with zitate identified and labeled.
    """
    updated_annotated_text = []

    original_text = "".join(
        [item[0] if isinstance(item, tuple) else item for item in annotated_text]
    )

    cleaned_text = original_text.replace("\n", " ")

    list_of_indices = []
    list_of_zitate_to_find = [(clean_zitat(z[0]), z[1]) for z in zitate_to_find]

    list_of_zitate_to_find = [
        (z, zitat_label)
        for zitate, zitat_label in list_of_zitate_to_find
        for z in zitate
    ]

    for zitat, zitat_label in list_of_zitate_to_find:
        cleaned_zitat = zitat.replace("\n", " ")

        # Check if the zitat is an exact match
        start = original_text.find(zitat)
        if start != -1:
            end = start + len(zitat)
            list_of_indices.append(((start, end), zitat_label, zitat))

        # Search a bit more flexible
        else:
            potential_matches = list(
                re.finditer(
                    re.escape(cleaned_zitat[:6])
                    + ".*?"
                    + re.escape(cleaned_zitat[-6:]),
                    cleaned_text,
                    re.DOTALL,
                )
            )

            best_match = None
            best_ratio = 0

            for match in potential_matches:
                substring = cleaned_text[match.start() : match.end()]
                ratio = fuzz.ratio(cleaned_zitat, substring)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = match

            if best_match and best_ratio >= 90:
                original_match_text = original_text[
                    best_match.start() : best_match.end()
                ]
                list_of_indices.append(
                    (
                        (best_match.start(), best_match.end()),
                        zitat_label,
                        original_match_text,
                    )
                )

    list_of_indices.sort(key=lambda x: x[0][0])

    if list_of_indices:
        zitat_start = list_of_indices[0][0][0]
        updated_annotated_text.append(original_text[:zitat_start])

    for i, (indices, label, zitat_text) in enumerate(list_of_indices):
        updated_annotated_text.append((zitat_text, label))

        if i < len(list_of_indices) - 1:
            next_start = list_of_indices[i + 1][0][0]
            updated_annotated_text.append(original_text[indices[1] : next_start])

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
