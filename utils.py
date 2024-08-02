import pandas as pd 
import streamlit as st
from jinja2 import Environment, FileSystemLoader
import time
import http.client
import json
import requests

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

def resolve_overlaps(list_of_indices, text_string):
    list_of_indices_new = []
    overlaps_found = False

    for i in range(len(list_of_indices)):
        zitat_1_start, zitat_1_end = list_of_indices[i][0][0], list_of_indices[i][0][1]
        for j in range(i+1, len(list_of_indices)):
            zitat_2_start, zitat_2_end = list_of_indices[j][0][0], list_of_indices[j][0][1]
            if zitat_1_end > zitat_2_start and zitat_1_start < zitat_2_end:
                overlaps_found = True
                overlapping_indices = (zitat_2_start, zitat_1_end)
                overlapping_zitat = text_string[overlapping_indices[0]:overlapping_indices[1]]
                overlapping_label = set(flatten(list_of_indices[i][1]) + flatten(list_of_indices[j][1]))
                list_of_indices_new.append((overlapping_indices, overlapping_label, overlapping_zitat))
                zitat_1_end = zitat_2_start - 1
                list_of_indices[i] = ((zitat_1_start, zitat_1_end), list_of_indices[i][1], text_string[zitat_1_start:zitat_1_end])
                zitat_2_start = zitat_1_end + 1
                list_of_indices[j] = ((zitat_2_start, zitat_2_end), list_of_indices[j][1], text_string[zitat_2_start:zitat_2_end])
        list_of_indices_new.append(list_of_indices[i])
    
    list_of_indices_new = [zitat for zitat in list_of_indices_new if zitat[2]]
    return list_of_indices_new

def split_labels(label):
    return label.split(" & ")

def clean_newline(text):
    return text.replace(" ", "\n")

def remove_cleaned_newline(text):
    return text

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
    text_string = ''.join([item[0] if isinstance(item, tuple) else item for item in annotated_text])

    list_of_indices = []
    list_of_zitate_to_find = [(clean_zitat(z[0]), z[1]) for z in zitate_to_find]

    # Flatten the list of zitate to find
    list_of_zitate_to_find = [(z, zitat_label) for zitate, zitat_label in list_of_zitate_to_find for z in zitate]

    for zitat, zitat_label in list_of_zitate_to_find:
        first_word = zitat.split()[0]
        start_positions = [i for i in range(len(text_string)) if text_string.startswith(first_word, i)]

        for start in start_positions:
            substring = text_string[start:start + len(zitat)]
            match = fuzz.partial_ratio(zitat, substring)
            if match >= 50:
                list_of_indices.append(((start, start + len(zitat)), zitat_label, text_string[start:start + len(zitat)]))
                break

    # list_of_indices_new = resolve_overlaps(list_of_indices, text_string)
    # Sort the list of indices by the start position
    list_of_indices_new = list_of_indices
    list_of_indices_new.sort(key=lambda x: x[0][0])

    # Add all the text before the first quote
    if list_of_indices_new:
        zitat_start, zitat_end = list_of_indices_new[0][0][0], list_of_indices_new[0][0][1]
        updated_annotated_text.append(remove_cleaned_newline(text_string[0:zitat_start ]))

    # enumerate through the list of indices
    for index in range(len(list_of_indices_new)):
        zitat_start, zitat_end = list_of_indices[index][0][0], list_of_indices[index][0][1]
        next_zitat_start = list_of_indices[index + 1][0][0] if index + 1 < len(list_of_indices) else len(text_string)
        next_zitat_end = list_of_indices[index + 1][0][1] if index + 1 < len(list_of_indices) else len(text_string)

        # Add the current quote
        updated_annotated_text.append((list_of_indices[index][2], list_of_indices[index][1]))

        # Check if the next quote is overlapping with the current one
        if zitat_end > next_zitat_start:
            continue
        else:
            # Add any remaining text between the current and next quote
            updated_annotated_text.append(remove_cleaned_newline(text_string[zitat_end :next_zitat_start ]))

    # Add any remaining text after the last quote
    if next_zitat_end < len(text_string):
        updated_annotated_text.append(remove_cleaned_newline(text_string[next_zitat_end:]))

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

def post_process_text(text):
    # Split text into lines
    lines = text.split('\n')
    
    # Combine lines into paragraphs based on the absence of empty lines
    paragraphs = []
    current_paragraph = []
    
    for line in lines:
        # If the line is not empty, add it to the current paragraph
        if line.strip():
            current_paragraph.append(line.strip())
        else:
            # If the line is empty, it means the end of a paragraph
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
    
    # Add the last paragraph if there's any
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    # Join paragraphs with a double newline to separate them
    return '\n\n'.join(paragraphs)

def format_ziffer_to_4digits(ziffer):
    ziffer_parts = ziffer.split(' ')[1]
    numeric_part = ''.join(filter(str.isdigit, ziffer_parts))
    alpha_part = ''.join(filter(str.isalpha, ziffer_parts))

    try:
        result = f"{int(numeric_part):04d}{alpha_part}"
    except ValueError:
        result = ziffer_parts
    return result

def ocr_pdf_to_text(file):
    """Call API /process_document and return the text."""
    print("Performing OCR on the PDF...")

    url = f"{st.session_state.api_url}/process_document"

    payload = {
        'ocr_processor': 'google_document_ai',
        'process_type': 'ocr',
        'category': st.session_state.category,
    }

    headers = {
        'x-api-key': st.session_state.api_key
    }

    # Read the UploadedFile as bytes
    file_bytes = file.read()
    files = {"file": ("file.pdf", file_bytes, "application/pdf")}

    try: 
        response = requests.post(url, headers=headers, data=payload, files=files)
    except Exception as e:
        st.error(f"""Ein Fehler ist aufgetreten beim Aufrufen der API für OCR. Bitte überprüfen Sie die URL und den API Key und speichern Sie die Einstellungen erneut.
                 
                 Fehlerdetails: {e}""")

    response_content = response.json()

    print("Done performing OCR on the PDF. Response status: ", response.status_code)

    if response.status_code != 200:
        st.error(f"""Ein Fehler ist beim Aufrufen der API für OCR aufgetreten. Überprüfen Sie die API-Einstellungen und speichern Sie die Einstellungen erneut.

                API-Fehler: 
                Status Code: {response.status_code} 
                Nachricht: {response.text}
                Anfrage-ID (Kann von Qodia verwendet werden, um den Fehler zu finden): {response.headers.get("request_id", "")}
                """)
        return None
    else:
        return response_content["result"]["ocr_text"]

def test_api():
    """Test if the settings for the API are correct."""
    url = f"{st.session_state.api_url}"
    headers = {
        'x-api-key': st.session_state.api_key
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            st.error("Der API-Key ist nicht korrekt. Bitte überprüfen Sie den API-Key und speichern Sie die Einstellungen erneut.")
            return False
        elif response.status_code != 200 or response.status_code != 201:
            st.error(f"""Ein unerwarteter Fehler ist beim Aufrufen der API aufgetreten. Überprüfen Sie die API-Einstellungen und speichern Sie die Einstellungen erneut.
                     
                     Fehlerdetails: 
                     Status Code: {response.status_code}
                     Nachricht: {response.text}
                     Anfrage-ID (Kann von Qodia verwendet werden, um den Fehler zu finden): {response.headers.get('request_id', 'nicht-vorhanden')}
                    """)
            return False
    except Exception as e:
        st.error(f"""Ein Fehler ist beim Aufrufen der API aufgetreten. Bitte überprüfen Sie die URL und den API-Key und speichern Sie die Einstellungen erneut.
                 
                 Fehlerdetails: {e}""")
        return False

    st.success('Die API-Einstellungen sind korrekt. Die URL und der API-Key funktionieren.')
    return True
   

def analyze(text):
    """Analyzes the text and returns the prediction."""
    print("Analyzing text...")

    url = f"{st.session_state.api_url}/process_document"

    payload = {
        'text': text,
        'category': st.session_state.category,
        "process_type": "predict",
    }

    headers = {
        "x-api-key": st.session_state.api_key
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
    except Exception as e:
        st.error(f"""Ein Fehler ist aufgetreten beim Aufrufen der API für die Analyse des Textes. Bitte überprüfen Sie die URL und den API Key und speichern Sie die Einstellungen erneut.
                 
                 Fehlerdetails: {e}""")


    response_content = response.json()

    print("Done analyzing text. Respoonse status: ", response.status_code, response.text)

    if response.status_code != 200:
        request_id = response.headers.get("request_id", "nicht-vorhanden")
        st.error(f"""Ein Fehler ist aufgetreten beim Aufrufen der API für die Analyse des Textes.

                API-Fehler: 
                Status Code: {response.status_code} 
                Nachricht: {response.text}
                Anfrage-ID (Kann von Qodia verwendet werden, um den Fehler zu finden): {request_id}
                """)
        return None
    
    return response_content["result"]["prediction"]

def read_in_goa(path = "./data/GOA_Ziffern.csv", fully=False):
    # Read in the csv file with pandas

    goa = pd.read_csv(path, sep=",", encoding="utf-8")

    if fully:
        return goa
    # use only the columns "GOÄZiffer" and "Beschreibung"
    goa = goa[["GOÄZiffer", "Beschreibung"]]

    goa = goa.dropna()

    # Combine the two columns into a single string using " - " as separator
    goa["Ziffern"] = goa["GOÄZiffer"] + " - " + goa["Beschreibung"]

    return goa

def analyze_add_data(data):
    """Add all necessary data for the frontend.
    
    Format of data:
    [
      {
        "zitat": "string",
        "begrundung": "string",
        "goa_ziffer": "string"
      }
    ]

    Expected format:
    {
        'Ziffer': [],
        'Häufigkeit': [],
        'Intensität': [],
        'Beschreibung': [],
        "Zitat": [],
        "Begründung": []
    }
    """

    data = data.copy()

    new_data = {
        'Ziffer': [],
        'Häufigkeit': [],
        'Intensität': [],
        'Beschreibung': [],
        "Zitat": [],
        "Begründung": []
    }

    goa = read_in_goa(fully=True)

    for data_count in range(len(data)):
        new_data["Ziffer"].append(data[data_count]["goa_ziffer"])

        new_data["Zitat"].append(data[data_count]["zitat"])

        new_data["Begründung"].append(data[data_count]["begrundung"])

        new_data["Häufigkeit"].append(data[data_count]["quantitaet"])

        new_data["Intensität"].append(data[data_count]["faktor"])

        new_data["Beschreibung"].append(goa[goa["GOÄZiffer"] == data[data_count]["goa_ziffer"]]["Beschreibung"].values[0])

    return new_data


def df_to_items(df):
    items = []
    goa = read_in_goa(fully=True)
    
    for idx, row in df.iterrows():
        goa_item = goa[goa["GOÄZiffer"] == row["Ziffer"]]
        
        if goa_item.empty:
            print(f"No matching GOÄZiffer for row index {idx} with Ziffer {row['Ziffer']}")
            continue
        
        intensity = row["Intensität"]
        
        # Convert intensity to string in both formats
        intensity_str_period = f"{intensity:.1f}"  # Format with period
        intensity_str_comma = intensity_str_period.replace('.', ',')  # Format with comma
        
        # Find columns where intensity matches either format
        matching_columns = goa_item.columns[
            goa_item.apply(lambda col: col.astype(str).str.contains(f"({intensity_str_period}|{intensity_str_comma})")).any()
        ]
        
        if matching_columns.empty:
            print(f"No matching intensity {intensity} (as {intensity_str_period} or {intensity_str_comma}) for row index {idx} with Ziffer {row['Ziffer']}")
            continue
        
        column_name = matching_columns[0]

        faktor = intensity

        if column_name == "Einfachfaktor":
            preis = float(goa_item["Einfachsatz"].values[0].replace(',', '.'))
        elif column_name == "Regelhöchstfaktor":
            preis = float(goa_item["Regelhöchstsatz"].values[0].replace(',', '.'))
        elif column_name == "Höchstfaktor":
            preis = float(goa_item["Höchstsatz"].values[0].replace(',', '.'))
        elif faktor < 2:
            preis = float(goa_item["Einfachsatz"].values[0].replace(',', '.'))
        elif faktor < 3:
            preis = float(goa_item["Regelhöchstsatz"].values[0].replace(',', '.'))
        else:
            preis = float(goa_item["Höchstsatz"].values[0].replace(',', '.'))

        print(f"Preis: {preis}, Faktor: {faktor}, Row: {row}")

        item = {
            "ziffer" : row["Ziffer"],
            "Häufigkeit" : row["Häufigkeit"],
            "intensitat" : intensity,
            "beschreibung" : goa_item["Beschreibung"].values[0],
            "Punktzahl": goa_item["Punktzahl"].values[0],
            "preis": preis,
            "faktor": faktor,
            "total": preis * int(row["Häufigkeit"]),
            "auslagen": "",
            "date": ""
        }

        items.append(item)
    
    if not items[0]["date"]:
        items[0]["date"] = "25.05.24"

    return items

def generate_pdf_from_df(df=None):
    data = {
        "customer_name": "Max Mustermann",
        "customer_street": "Musterstraße",
        "customer_street_number": "123",
        "customer_city": "Musterstadt",
        "customer_country": "Deutschland",
        "date_today": time.strftime("%d.%m.%Y"),
        "date_bill": time.strftime("%d.%m.%Y"),
        "diagnosis": "Große subxiphoidale Narbenhernie mit Einklemmung von präperitonealem Fettgewebe und Omentum majus bei Z.n. Sternotomie und aortokoronarer Bypassopertaion und Bio-Aortenklappenimplantation. Kleine primäre epigastrische Bauchwandhernie im mitteleren Epigastrium. KHK, Z. n. Implantation von 10 Koronarstents. Z. n. Myokardinfarkt 1998.",
    }



    items = df_to_items(df)

    data["items"] = items
    data["total"] = sum([item["total"] for item in data["items"]])

    data["discount"] = data["total"] * 0.25
    data["final_price"] = data["total"] - data["discount"]



    # Change all Int and Float values to strings
    for item in data["items"]:
        for key, value in item.items():
            if isinstance(value, (int, float)):
                # Change all Float values to a Euro € string
                if key in ["preis", "total", "discount", "final_price"]:
                    item[key] = f"{value:.2f} €".replace('.', ',')
                else: 
                    item[key] = str(value)
    
    # Change Ziffer format
    for item in data["items"]:
        item["ziffer"] = format_ziffer_to_4digits(item["ziffer"])
        if int(item["Häufigkeit"]) > 1:
            item["ziffer"] = f"{item['Häufigkeit']}x {item['ziffer']}"

    data["total"] = f"{data["total"]:.2f} €".replace('.', ',')
    data["discount"] = f"{data["discount"]:.2f} €".replace('.', ',')
    data["final_price"] = f"{data["final_price"]:.2f} €".replace('.', ',')


    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('./data/template_rechnung.html')

    html_content = template.render(data)

    # Write the HTML content to a file (optional, for inspection)
    with open('./data/rechnung_generiert.html', 'w') as file:
        file.write(html_content)

    # Generate the PDF from the rendered HTML content
    pdf_file = './data/rechnung_generiert.pdf'

    # HTML(string=html_content).write_pdf(pdf_file)
    conn = http.client.HTTPSConnection("yakpdf.p.rapidapi.com")
    
    # transform html_content to string without spacing, line breaks and ”\" before quotes

    # html_content = html_content.replace("\n", "")
    # html_content = str(html_content).replace('"', '\\"')

    payload = {
        "pdf": {
            "format": "A4",
            "printBackground": True,
            "scale": 1,
            "margin": {
                "top": "0cm",
                "right": "0cm",
                "bottom": "0cm",
                "left": "0cm"
            }
        },
        "source": {
            "html": html_content
        },
        "wait": {
            "for": "navigation",
            "timeout": 250,
            "waitUntil": "load"
        }
    }

    payload_str = json.dumps(payload)
    
    headers = {
        'content-type': "application/json",
        'x-rapidapi-key': "18a7c1f0a3mshc09f133b9c99f34p1fab4cjsn3f4de4a18cfa",
        'x-rapidapi-host': "yakpdf.p.rapidapi.com"
        }
    
    payload_bytes = payload_str.encode('utf-8')

    
    conn.request("POST", "/pdf", payload_bytes, headers)
    
    res = conn.getresponse()
    data = res.read()

    # Write data to the PDF file
    with open(pdf_file, 'wb') as file:
        file.write(data)

    return pdf_file