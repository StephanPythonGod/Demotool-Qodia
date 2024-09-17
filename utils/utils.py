import json
import re

from fuzzywuzzy import fuzz


def flatten(lst):
    result = []
    if isinstance(lst, str):
        result.append(lst)
        return result
    for i in lst:
        if isinstance(i, list):
            result.extend(flatten(i))
        else:
            result.append(i)
    return result


def clean_zitat(zitat):
    lines = zitat.split("\n")
    cleaned_lines = []
    for line in lines:
        parts = line.split("[...]")
        for part in parts:
            cleaned_part = part.strip()
            if cleaned_part:
                cleaned_lines.append(cleaned_part)
    return cleaned_lines


def find_zitat_in_text(zitate_to_find, annotated_text):
    updated_annotated_text = []
    # Join the text, keeping the original structure
    original_text = "".join(
        [item[0] if isinstance(item, tuple) else item for item in annotated_text]
    )

    # Create a cleaned version for searching
    cleaned_text = original_text.replace("\n", " ")

    list_of_indices = []
    list_of_zitate_to_find = [(clean_zitat(z[0]), z[1]) for z in zitate_to_find]
    # Flatten the list of zitate to find
    list_of_zitate_to_find = [
        (z, zitat_label)
        for zitate, zitat_label in list_of_zitate_to_find
        for z in zitate
    ]

    for zitat, zitat_label in list_of_zitate_to_find:
        # Clean the zitat by replacing newlines with spaces
        cleaned_zitat = zitat.replace("\n", " ")

        start = original_text.find(zitat)
        if start != -1:
            end = start + len(zitat)
            list_of_indices.append(((start, end), zitat_label, zitat))

        else:
            # Use regex to find all potential matches in the cleaned text
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

            if (
                best_match and best_ratio >= 90
            ):  # Increased threshold for better accuracy
                # Get the original text (with newlines) for this match
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

    # Sort the list of indices by the start position
    list_of_indices.sort(key=lambda x: x[0][0])

    # Add all the text before the first quote
    if list_of_indices:
        zitat_start = list_of_indices[0][0][0]
        updated_annotated_text.append(original_text[0:zitat_start])

    # Process quotes and text between them
    for i, (indices, label, zitat_text) in enumerate(list_of_indices):
        # Add the current quote
        updated_annotated_text.append((zitat_text, label))

        # Add text between quotes
        if i < len(list_of_indices) - 1:
            next_start = list_of_indices[i + 1][0][0]
            updated_annotated_text.append(original_text[indices[1] : next_start])

    # Add any remaining text after the last quote
    if list_of_indices:
        last_end = list_of_indices[-1][0][1]
        if last_end < len(original_text):
            updated_annotated_text.append(original_text[last_end:])

    if not updated_annotated_text:
        updated_annotated_text = annotated_text

    return updated_annotated_text


def ziffer_from_options(ziffer_option):
    for i in ziffer_option:
        if isinstance(i, float):
            pass

    if isinstance(ziffer_option, list):
        ziffer = [i.split(" - ")[0] for i in ziffer_option]
    elif isinstance(ziffer_option, str):
        ziffer = ziffer_option.split(" - ")[0]
        ziffer = [ziffer]
    return ziffer


# TODO: Remove this?
def transform_auswertungsobjekt_to_resultobjekt(data_json) -> any:
    """Transform Logged Prediction Result to Customer Facing API Result"""

    # Check if the data_json is a string, if so, parse it to a list
    if isinstance(data_json, str):
        data_json = json.loads(data_json)

    transformed_results = []

    for obj in data_json:
        transformed_results.append(
            {
                "zitat": obj["zitat"][-1],
                "begrundung": obj["begrundung"][-1],
                "goa_ziffer": obj["goa_ziffer"],
                "quantitaet": obj["leistungQuantitaet"],
                "faktor": obj["leistungIntensitaet"],
                "beschreibung": obj["leistungBeschreibung"],
            }
        )

    return transformed_results
