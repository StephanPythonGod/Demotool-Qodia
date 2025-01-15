import os

from flair.models import SequenceTagger

from utils.helpers.logger import logger

MODEL_LANGUAGES = {
    "de": "flair/ner-german-large",
}

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../../../models")
MODEL_FILE = os.path.join(MODELS_DIR, "flair-ner-german-large.pt")


def download_model_if_needed():
    """Download the Hugging Face NER model if it does not exist locally."""
    if not os.path.exists(MODEL_FILE):
        logger.info("Downloading Hugging Face model...")
        os.makedirs(MODELS_DIR, exist_ok=True)
        model = SequenceTagger.load(MODEL_LANGUAGES["de"])
        model.save(MODEL_FILE)
    else:
        logger.info("Model already exists locally.")


def load_model():
    """Load the Hugging Face NER model from the local file."""
    if os.path.exists(MODEL_FILE):
        logger.info("Loading the local Hugging Face model...")
        model = SequenceTagger.load(MODEL_FILE)
    else:
        logger.info("Model not found locally, downloading...")
        download_model_if_needed()
        model = load_model()
    return model
