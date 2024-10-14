# Qodia - Kodierungstool

Willkommen beim **Qodia - Kodierungstool**, einer Streamlit-Anwendung, die eine einfache und benutzerfreundliche Möglichkeit bietet, mit der Qodia - Kodierungs-API zu interagieren und diese über eine grafische Benutzeroberfläche zu testen. Die Anwendung wurde entwickelt, um die Analyse und Kodierung von Texten zu vereinfachen und bietet verschiedene nützliche Funktionen.

## Inhaltsverzeichnis

- [Installation](#installation)
- [Funktionen](#funktionen)
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

## Lizenz

Dieses Projekt steht unter der **MIT Lizenz**. Siehe die [LICENSE](LICENSE)-Datei für weitere Details.

## Kontakt

Bei Fragen oder Vorschlägen kontaktieren Sie bitte **Stephan Lenert** unter [stephan.lenert@qodia.de](mailto:stephan.lenert@qodia.de).
