import os
import subprocess
import sys


# Step 1: Create the .env file with user input
def create_env_file():
    """Prompt user for environment variables and write them to a .env file."""
    api_key = input("Enter API Key: ")
    api_url = input("Enter API URL: ")
    rapid_api_key = input("Enter Rapid API Key: ")

    # Create the .env file
    with open(".env", "w") as f:
        f.write("DEPLOYMENT_ENV=local\n")
        f.write(f"API_KEY={api_key}\n")
        f.write(f"API_URL={api_url}\n")
        f.write(f"RAPID_API_KEY={rapid_api_key}\n")

    print(".env file created successfully.")


# Step 2: Download the Flair model to the 'models' directory
def download_flair_model():
    """Download the Flair NER model and save it to the models directory."""
    try:
        from flair.models import SequenceTagger

        model_dir = os.path.join(os.getcwd(), "models")

        # Ensure the models directory exists
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        # Check if the model already exists
        if os.path.exists(os.path.join(model_dir, "flair-ner-german-large.pt")):
            print("Flair NER model already downloaded.")
            return

        # Download the model
        print("Downloading Flair NER model...")
        tagger = SequenceTagger.load("flair/ner-german-large")

        # Save the model in the desired folder
        tagger.save(os.path.join(model_dir, "flair-ner-german-large.pt"))
        print("Flair NER model downloaded successfully to 'models' directory.")

    except Exception as e:
        print(f"Error downloading Flair model: {e}")
        sys.exit(1)


def create_executable():
    print("Creating executable using PyInstaller...")

    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # List of additional data files and folders to include
    additional_data = [
        "--add-data",
        ".env:.",
        "--add-data",
        "utils:utils",
        "--add-data",
        "data:data",
        "--add-data",
        "schemas:schemas",
        "--add-data",
        "models:models",
    ]

    # List of hidden imports
    hidden_imports = [
        "--hidden-import",
        "streamlit",
        "--hidden-import",
        "streamlit_cookies_controller",
        "--hidden-import",
        "fuzzywuzzy",
        "--hidden-import",
        "st_annotated_text",
        "--hidden-import",
        "streamlit_drawable_canvas",
        "--hidden-import",
        "pdf2image",
        "--hidden-import",
        "transformers",
        "--hidden-import",
        "sentencepiece",
        "--hidden-import",
        "spacy",
        "--hidden-import",
        "presidio_anonymizer",
        "--hidden-import",
        "presidio_analyzer",
        "--hidden-import",
        "torch",
        "--hidden-import",
        "pytesseract",
        "--hidden-import",
        "flair",
        "--hidden-import",
        "streamlit_paste_button",
        "--hidden-import",
        "python_levenshtein",
        "--hidden-import",
        "xsdata",
        "--hidden-import",
        "pyopenssl",
        "--hidden-import",
        "cryptography",
        "--hidden-import",
        "xmlschema",
        "--hidden-import",
        "pypdf2",
    ]

    # PyInstaller command
    command = (
        [
            "poetry",
            "run",
            "pyinstaller",
            "--name=qodia-kodierungstool",
            "--onedir",
            "--windowed",
            "--clean",
            "--log-level=DEBUG",
        ]
        + additional_data
        + hidden_imports
        + ["app.py"]
    )

    try:
        # Run PyInstaller
        result = subprocess.run(command, check=True, capture_output=True, text=True)

        print("PyInstaller output:")
        print(result.stdout)

        # Check if the executable was created
        executable_path = os.path.join(
            "dist", "qodia-kodierungstool", "qodia-kodierungstool"
        )
        if os.path.exists(executable_path):
            print(f"Executable created successfully at: {executable_path}")
        else:
            print("Error: Executable file not found in the expected location.")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Error creating executable. Return code: {e.returncode}")
        print("PyInstaller output:")
        print(e.output)
        print("PyInstaller error:")
        print(e.stderr)
        sys.exit(1)


# Main function to execute the steps
def main():
    create_env_file()
    download_flair_model()
    create_executable()


if __name__ == "__main__":
    main()
