from typing import List, Set, Tuple

# Entity types
ENTITIES = [
    "LOCATION",
    "PERSON",
    "ORGANIZATION",
    "DATE_TIME",
    "GENDER_WORD",
    "ID_NUMBER",
    "FINANCIAL_ID",
]

PRESIDIO_EQUIVALENCES = {
    "PER": "PERSON",
    "LOC": "LOCATION",
    "ORG": "ORGANIZATION",
    "DATE_TIME": "DATE_TIME",
    "GENDER_WORD": "GENDER_WORD",
    "ID_NUMBER": "ID_NUMBER",
    "FINANCIAL_ID": "FINANCIAL_ID",
}

CHECK_LABEL_GROUPS: List[Tuple[Set[str], Set[str]]] = [
    ({"LOCATION"}, {"LOC", "LOCATION"}),
    ({"PERSON"}, {"PER", "PERSON"}),
    ({"ORGANIZATION"}, {"ORG"}),
]

# Date-related constants
GERMAN_WEEKDAYS = {
    # Full names
    "montag",
    "dienstag",
    "mittwoch",
    "donnerstag",
    "freitag",
    "samstag",
    "sonntag",
    # Abbreviations
    "mo",
    "di",
    "mi",
    "do",
    "fr",
    "sa",
    "so",
    # With dots
    "mo.",
    "di.",
    "mi.",
    "do.",
    "fr.",
    "sa.",
    "so.",
}

GERMAN_MONTHS = {
    # Full names
    "januar",
    "februar",
    "märz",
    "april",
    "mai",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "dezember",
    # Abbreviations
    "jan",
    "feb",
    "mär",
    "apr",
    "mai",
    "jun",
    "jul",
    "aug",
    "sep",
    "okt",
    "nov",
    "dez",
    # With dots
    "jan.",
    "feb.",
    "mär.",
    "apr.",
    "jun.",
    "jul.",
    "aug.",
    "sep.",
    "okt.",
    "nov.",
    "dez.",
}

DATE_PATTERNS = [
    r"\b\d{1,2}[\.-/]\d{1,2}[\.-/]\d{4}\b",
    r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
    r"\b\d{1,2}[\.-/]\d{1,2}[\.-/]\d{2}\b",
    r"\b\d{2}[-/]\d{1,2}[-/]\d{1,2}\b",
    r"\b\d{1,2}\.\d{1,2}\.\b",
    r"[a-zA-Z]{0,3}\d{1,2}[\.-][a-zA-Z]{0,3}\d{1,2}[\.-][a-zA-Z]{0,3}\d{2,4}",
    r"\d{1,2}[a-zA-Z]{0,3}[\.-][a-zA-Z]{0,3}\d{1,2}[a-zA-Z]{0,3}[\.-][a-zA-Z]{0,3}\d{2,4}",
    r"\b\d{1,2}[\.-/][O0]\d{1,1}[\.-/][O0\d]{2,4}\b",
]

# Gender-related constants
GENDER_WORDS = [
    "frau",
    "frauen",
    "frauens",
    "mann",
    "männer",
    "mannes",
    "männern",
    "herr",
    "herren",
    "herrn",
    "dame",
    "damen",
    "dames",
    "fräulein",
    "fräuleins",
    "mädchen",
    "mädchens",
    "junge",
    "jungen",
    "jungens",
    "jugendlicher",
    "jugendliche",
    "jugendlichen",
    "person",
    "personen",
    "persons",
]

# Financial and phone patterns
FINANCIAL_PATTERNS = [
    r"St-Nr\.?\s*:?\s*[\d/]+",
    r"\b\d{2}/\d{3}/\d{5}\b",
    r"USt-IdNr\.?\s*:?\s*DE\d{9}",
    r"\bDE\d{9}\b",
    r"\bDE\d{2}[\s\d]{20,}\b",
    r"IBAN\s*:?\s*DE\d{2}[\s\d]{20,}",
    r"\b(?:BIC|SWIFT)\s*:?\s*[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b",
    r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b(?=.*?(?:BIC|SWIFT))",
    r"HRB\s*:?\s*\d{1,6}",
    r"\bHRB\s*\d{1,6}\b",
    r"IK-Nr\.?\s*:?\s*\d{9}",
    r"Konto-?Nr\.?\s*:?\s*\d{4,12}",
    r"Kontonummer\s*:?\s*\d{4,12}",
    r"Ref(?:erenz)?[-\.]?Nr\.?\s*:?\s*\d{4,15}",
]

PHONE_PATTERNS = [
    r"\+49[\s-]?[1-9]\d{1,2}[\s-]?\d{1,4}[\s-]?\d{4,8}",
    r"0[1-9]\d{1,4}\/\d{4,8}",
    r"\([0-9]\d{1,4}\)\s*\d{4,8}",
    r"0[1-9]\d{1,4}\s\d{3,4}\s\d{4}",
    r"0[1-9]\d{8,14}",
    r"\d{3,4}[-]\d{4,8}",
    r"01[567]\d[-\s]?\d{3,4}[-\s]?\d{4}",
    r"01[567]\d\s\d{3}\s\d{4}",
    r"0[1-9]\d{1,4}\.\d{4,8}",
    r"\+49\(0\)\d{2,4}[-\s]?\d{4,8}",
    r"040\s*[/\-]?\s*\d{5}[-]?\d{1,4}",
    r"040[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{0,3}",
    r"\d{2,5}\s*[/-]?\s*\d{4,6}[-]?\d{0,4}",
    r"\d{2,5}[-\s/]?\d{2,3}[-\s]?\d{2,3}[-\s]?[O0\d]{2,3}",
]

# Update FINANCIAL_PATTERNS to include phone patterns
FINANCIAL_PATTERNS.extend(PHONE_PATTERNS)

# Whitelist
WHITELIST = {
    "lichtenstein",
    "fcds",
    "n. ilioinguinalis",
    "n. ilioniguinalis",
    "n.",
    "ilioinguinalis",
    "dynamesh",
    "endolap",
    "dynamesh endolap",
    "fk",
    "urursf",
    "lma",
}
