# Qodia - Kodierungstool

Willkommen beim **Qodia - Kodierungstool**, einer Streamlit-Anwendung, die eine einfache und benutzerfreundliche Möglichkeit bietet, mit der Qodia - Kodierungs-API zu interagieren und diese über eine grafische Benutzeroberfläche zu testen. Die Anwendung wurde entwickelt, um die Analyse und Kodierung von Texten zu vereinfachen und bietet verschiedene nützliche Funktionen.

## Inhaltsverzeichnis

- [Installation](#installation)
- [Funktionen](#funktionen)
- [Troubleshooting](#troubleshooting)
- [Lizenz](#lizenz)
- [Kontakt](#kontakt)

## Installation

Für die Installation des Projekts muss eine [Docker-Compose](/compose.yaml) Orchestrierung aufgesetzt werden. Diese besteht einerseits aus einem [Qodia-Kodierungstool](/Dockerfile) Container, der die Streamlit Anwendung hostet, und andererseits aus einem [Nginx](/Dockerfile-nginx) Container, der notwendig ist, um das Qodia-Kodierungstool im eigenen Netwerk via HTTPS anzusprechen.

Um die Docker-Compose Orchestrierung aufzusetzen, klonen Sie das Repository und führen Sie den folgenden Befehl aus:

```bash
bash ./scripts/setup.sh
```

Bei erfolgreicher Installation können Sie die Anwendung über den folgenden Link erreichen: [https://localhost](https://localhost)

## Funktionen

- **Interaktion mit der Qodia API**: Nutzen Sie die API zur OCR-Verarbeitung und Textanalyse.
- **Ergebnisse anzeigen**: Zeigt die Ergebnisse der API-Verarbeitung übersichtlich in der Anwendung an.
- **Lokale Anonymisierung**: Ermöglicht die Anonymisierung von Texten lokal auf Ihrem Gerät.
- **Datei-Upload**: Laden Sie PDFs, PNGs oder JPGs hoch, um sie zu verarbeiten.
- **Screenshots einfügen**: Fügen Sie Text und Bilder direkt aus der Zwischenablage ein.

## TroubleShooting

Wenn Sie Probleme bei Docker auf Windows haben in Bezug auf Memory Limits (Exit Code 137). Dann sollte das Memory Limit für WSL2 angepasst werden. Dies kann in der `.wslconfig` Datei angepasst werden. Hier ein Beispiel:

```bash
# Navigate to the user's profile folder
cd $env:USERPROFILE

# Create the .wslconfig file if it doesn't exist and add memory, processor, and swap settings
Add-Content -Path ".wslconfig" -Value "[wsl2]"
Add-Content -Path ".wslconfig" -Value "memory=5GB"     # Limit memory to 4GB (adjust as needed)
Add-Content -Path ".wslconfig" -Value "processors=2"   # Limit to 2 processors (adjust as needed)
Add-Content -Path ".wslconfig" -Value "swap=4GB"       # Enable 4GB of swap space
Add-Content -Path ".wslconfig" -Value "swapFile=C:\\Users\\$env:USERNAME\\wsl_swap.vhdx" # Set swap file path
```

## Lizenz

Dieses Projekt steht unter der **MIT Lizenz**. Siehe die [LICENSE](LICENSE)-Datei für weitere Details.

## Kontakt

Bei Fragen oder Vorschlägen kontaktieren Sie bitte **Stephan Lenert** unter [stephan.lenert@qodia.de](mailto:stephan.lenert@qodia.de).
