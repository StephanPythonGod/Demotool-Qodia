import streamlit as st
import pandas as pd
from annotated_text import annotated_text
from utils import find_zitat_in_text, ziffer_from_options, ocr_pdf_to_text, generate_pdf_from_df, format_ziffer_to_4digits, analyze, analyze_add_data, read_in_goa, test_api, transform_auswertungsobjekt_to_resultobjekt
from streamlit_cookies_controller import CookieController
from datetime import datetime, timedelta
import json

st.set_page_config(
    page_title="Qodia",
    page_icon="🔍🤖📚",
    layout="wide",  # Set the page layout to wide
    initial_sidebar_state="collapsed"
)

# Initialize CookieController
controller = CookieController()

# Function to get a cookie value
def get_cookie(cookie_name):
    return controller.get(cookie_name)

# Function to set a cookie value
def set_cookie(cookie_name, value):
    expires = datetime.now() + timedelta(days=180)
    controller.set(cookie_name, value, expires=expires)

# Function to load settings from cookies
def load_settings_from_cookies():
    settings = {
        "api_url": get_cookie("api_url") or "https://qodia-api-staging-gateway-2qn1roat.nw.gateway.dev",
        "api_key": get_cookie("api_key") or "AIzaSyDQAAPcTJECYfwwFV9QDm9HeHAME99PbQo",
        "category": get_cookie("category") or "Hernien-OP"
    }

    st.session_state.api_url = settings["api_url"]
    st.session_state.api_key = settings["api_key"]
    st.session_state.category = settings["category"]

    return settings

# Function to save settings to cookies
def save_settings_to_cookies():
    set_cookie("api_url", st.session_state.api_url)
    set_cookie("api_key", st.session_state.api_key)
    set_cookie("category", st.session_state.category)

# Load initial settings from cookies
load_settings_from_cookies()

# Set session state
if 'stage' not in st.session_state:
    st.session_state.stage = 'analyze'

if "text" not in st.session_state:
    st.session_state.text = ""

if "annotated_text_object" not in st.session_state:
    st.session_state.annotated_text_object = []

if "ziffer_to_edit" not in st.session_state:
    st.session_state.ziffer_to_edit = None

if 'pdf_ready' not in st.session_state:
    st.session_state.pdf_ready = False
    st.session_state.pdf_data = None

if "api_url" not in st.session_state:
    st.session_state.api_url = "https://qodia-api-staging-gateway-2qn1roat.nw.gateway.dev"

if "api_key" not in st.session_state:
    st.session_state.api_key = "AIzaSyDQAAPcTJECYfwwFV9QDm9HeHAME99PbQo"

if "selected_ziffer" not in st.session_state:
    st.session_state.selected_ziffer = None

if "category" not in st.session_state:
    st.session_state.category = "Hernien-OP"

if 'df' not in st.session_state:
    data = {
            'Ziffer': [],
            'Häufigkeit': [],
            'Intensität': [],
            'Beschreibung': [],
            "Zitat": [],
            "Begründung": []
        }

    st.session_state.df = pd.DataFrame(data)

    st.session_state.df = st.session_state.df.astype({'Häufigkeit': 'int', 'Intensität': 'int'}, errors='ignore')


def annotate_text_update():
    st.session_state.annotated_text_object = [st.session_state.text]

    zitate_to_find = [(row['Zitat'], row['Ziffer']) for index, row in st.session_state.df.iterrows()]

    st.session_state.annotated_text_object = find_zitat_in_text(zitate_to_find, st.session_state.annotated_text_object)

    # Update st.session_state.df to be in the order as the labels are in the annotated_text_object

    ziffer_order = []

    for i in st.session_state.annotated_text_object:
        if isinstance(i, tuple):
            ziffer_order.append(i[1])
        
    ziffer_order = list(dict.fromkeys(ziffer_order))

    # Order the dataframe according to the order of the ziffer in the text, if a ziffer is not in the text, it will be at the end

    ziffer_order_dict = {ziffer: order for order, ziffer in enumerate(ziffer_order)}

    st.session_state.df['order'] = st.session_state.df['Ziffer'].map(ziffer_order_dict)

    # Fill NaN values with a large number to ensure these rows go to the end when sorted
    st.session_state.df['order'].fillna(9999, inplace=True)

    # Sort the DataFrame by the 'order' column
    st.session_state.df.sort_values('order', inplace=True)

    # Drop the 'order' column as it's no longer needed
    st.session_state.df.drop('order', axis=1, inplace=True)

    st.session_state.df = st.session_state.df.reset_index(drop=True)

def test_settings():
    # Test the API settings
    return test_api()

def load_external_results(external_results):
    external_results.seek(0)
    data_json = external_results.read().decode('utf-8')  # Decode the bytes to a string
    text = json.loads(data_json)['text']
    data_json = json.loads(data_json)  # Load the JSON from the string
    data_json = data_json['result']  # Access the 'result' key
    data = transform_auswertungsobjekt_to_resultobjekt(data_json)
    print(data)
    data = analyze_add_data(data)

    st.session_state.df = pd.DataFrame(data)
    st.session_state.text = text

    annotate_text_update()
    st.session_state.update(stage="result")


with st.sidebar:
    st.session_state.api_url = st.text_input("API URL", value=st.session_state.api_url, help="Hier kann die URL der API geändert werden, die für die Analyse des Textes verwendet wird.").strip()
    st.session_state.api_key = st.text_input("API Key", value=st.session_state.api_key, help="Hier kann der API Key geändert werden, der für die Authentifizierung bei der API verwendet wird.").strip()
    st.session_state.category = st.selectbox("Kategorie", options=["Hernien-OP", "Knie-OP", "Zahn-OP"], index=["Hernien-OP", "Knie-OP", "Zahn-OP"].index(st.session_state.category), help="Hier kann die Kategorie der Leistungsziffern geändert werden, die für die Analyse des Textes verwendet wird.")
    
    if st.button("Save Settings"):
        with st.spinner("🔍 Teste API Einstellungen..."):
            working = test_settings = test_settings()
            if working:
                save_settings_to_cookies()
    
    # external_results = st.file_uploader("Ergebnisse hochladen", type=["json"], help="Hier können Ergebnisse hochgeladen werden, die in das System importiert werden sollen.")
    # if external_results is not None:
    #     load_external_results(external_results)



def check_if_default_credentials():
    if st.session_state.api_key == "AIzaSyDQAAPcTJECYfwwFV9QDm9HeHAME99PbQo":
        st.warning("Bitte ändern Sie die Standard-API-Schlüssel-Einstellungen, um die Anwendung zu testen. Dieser Testlauf wird noch funktionieren, aber bitte fügen Sie Ihren Organisations-API-Schlüssel ein, um die Anwendung zu verwenden. Details hierzu finden Sie in der Dokumentation.", icon="⚠️")

def perform_ocr(file):
    check_if_default_credentials()
    # Extracts text from the uploaded file using OCR
    with st.spinner("🔍 Extrahiere Text mittels OCR..."):
        text = ocr_pdf_to_text(file)
        if text == None:
            return False
        else:
            st.session_state.text = text
            return True

def update_ziffer(new_ziffer):
    # Update the data in the result stage after editing

    # Check if a new ziffer is being added
    if st.session_state.ziffer_to_edit is None:
        new_row = pd.DataFrame(new_ziffer, index=[0])
        new_row = new_row.apply(pd.to_numeric, errors='ignore', downcast='integer')
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
    else:
        new_ziffer = {k: pd.to_numeric(v, errors='ignore', downcast='integer') if isinstance(v, (int, float)) else v for k, v in new_ziffer.items()}
        st.session_state.df.iloc[st.session_state.ziffer_to_edit] = new_ziffer
    
    annotate_text_update()

    st.session_state.update(stage="result")

def set_selected_ziffer(index):
    st.session_state.selected_ziffer = index

def delte_ziffer(index):
    st.session_state.df.drop(index, inplace=True)
    st.session_state.selected_ziffer = None
    st.session_state.df.reset_index(drop=True, inplace=True)
    annotate_text_update()
    st.rerun()

def reset():
    # Reset the app to the initial state
    st.session_state.stage = 'analyze'
    st.session_state.text = ""
    st.session_state.annotated_text_object = []
    st.session_state.df = pd.DataFrame()

def analyze_text():
    check_if_default_credentials()

    with st.spinner("🤖 Analysiere den Bericht ..."):

        data = analyze(st.session_state.text) 

    if data is None:
        pass
    else:
        
        data = analyze_add_data(data)

        st.session_state.df = pd.DataFrame(data)

        annotate_text_update()
        st.session_state.update(stage="result")


def generate_pdf(df):
    # Generate a PDF with the recognized GOÄ codes
    pdf_file_path = generate_pdf_from_df(st.session_state.df)

    # Read the generated PDF file and convert it to bytes
    with open(pdf_file_path, "rb") as file:
        pdf_data = file.read()
    return pdf_data
    


def main():
    st.title("Qodia")

    if st.session_state.stage != "modal":
        st.header("KI-basierte automatische Kodierung von Leistungen nach GOÄ")

    # Create two columns
    left_column, right_column = st.columns(2)

    if st.session_state.stage == 'analyze':
        # Analyze Stage

        left_outer_column, _, _, _, _ = st.columns([1, 2, 3, 2, 1])

        # Left column
        left_column.subheader("Ärztlicher Bericht:")
        text = left_column.text_area("Text des ärztlichen Berichts", value=st.session_state.text, height=400, placeholder="Hier den Text des ärztlichen Bericht einfügen ...",help="Hier soll der Text des ärztlichen Berichts eingefügt werden. Wenn ein Dokument auf der rechten Seite hochgeladen wird, wird der erkannte Text hier eingefügt und ist dadurch bearbeitbar.")

        st.session_state.text = text

        if left_outer_column.button("Analysieren", disabled=(text == ""), on_click=analyze_text, type="primary"):
            if not st.session_state.df.empty:
                st.rerun()

        # Right column
        right_column.subheader("Dokument Hochladen")
        uploaded_file = right_column.file_uploader("PDF Dokument auswählen", help="Das hochgeladene Dokument wird mittels OCR analysiert und der Text wird im linken Feld angezeigt.", type=["pdf"])

        if uploaded_file is not None and st.session_state.text == "":
            # Perform OCR on the uploaded file
            worked = perform_ocr(uploaded_file)
            if worked:
                st.rerun()

    
    if st.session_state.stage == "result":
        # Result Stage

        left_outer_column, _, _, _, right_outer_column = st.columns([1, 2, 3, 2, 1])

        
        # Left Column: Display the text with highlighting
        with left_column:
            st.subheader("Ärztlicher Bericht:")
            
            # Highlight text based on selected Ziffer
            if "selected_ziffer" in st.session_state and st.session_state.selected_ziffer is not None:
                selected_zitat = st.session_state.df.loc[
                    st.session_state.selected_ziffer, 'Zitat'
                ]

                selected_ziffer = st.session_state.df.loc[
                    st.session_state.selected_ziffer, 'Ziffer'
                ]

                annotated_text(
                    find_zitat_in_text([(selected_zitat, selected_ziffer)], [st.session_state.text])
                )
            else:
                st.write(st.session_state.text)
        # Right column

        # Dataframe with the recognized GOÄ codes

        with right_column:
            st.subheader("Erkannte Leistungsziffern:")

            # Display column headers
            header_cols = right_column.columns([1, 1, 1, 3, 1])
            headers = ['Ziffer', 'Häufigkeit', 'Faktor', "Beschreibung",'Aktionen']
            for col, header in zip(header_cols, headers):
                col.markdown(f"**{header}**")

            # Create a unique identifier for each row
            for index, row in st.session_state.df.iterrows():
                cols = right_column.columns([1, 1, 1, 3, 0.5, 0.5])
                # cols[0].write(row['Ziffer'])
                # cols[0].write(format_ziffer_to_4digits(row['Ziffer']))
                if cols[0].button(format_ziffer_to_4digits(row['Ziffer']), key=f'ziffer_{index}', type="secondary" if st.session_state.selected_ziffer != index else "primary"):
                    if st.session_state.selected_ziffer == index:
                        set_selected_ziffer(None)
                    else:
                        set_selected_ziffer(index)
                    st.rerun()
                # Use HTML and CSS for scrollable text field
                description_html = f"""
                <div style="overflow-x: auto; white-space: nowrap; padding: 5px;">
                    {row['Beschreibung']}
                </div>
                """

                
                cols[1].write(row['Häufigkeit'])
                cols[2].write(row['Intensität'])
                cols[3].markdown(description_html, unsafe_allow_html=True)
                
                # Add a delete button for each row
                if cols[4].button('✏️', key=f'edit_{index}'):
                    st.session_state.ziffer_to_edit = index
                    st.session_state.stage = "modal"
                    st.rerun()
                if cols[5].button('🗑️', key=f'delete_{index}'):
                    delte_ziffer(index)

            _, middle_column_right_column, _ = st.columns([3, 1, 3])

            with middle_column_right_column:
                st.write("")
                # Add a button to add a new row
                if middle_column_right_column.button('➕', use_container_width=True):
                    st.session_state.ziffer_to_edit = None
                    st.session_state.stage = "modal"
                    st.rerun()

        with left_outer_column:
            button = st.button("Zurücksetzen", on_click=reset, type="primary", use_container_width=True)

        with right_outer_column:
            # st.write("")
            # Add a button to generate a PDF
            # button = st.button("PDF generieren", on_click=lambda: generate_pdf, type="primary", use_container_width=True)
                # Create a button that triggers the PDF generation
            if st.button("PDF generieren", type="primary", use_container_width=True):
                with st.spinner("📄 Generiere PDF..."):
                    st.session_state.pdf_data = generate_pdf(st.session_state.df)
                    st.session_state.pdf_ready = True

            # If the PDF is ready, show the download button
            if st.session_state.pdf_ready:
                st.download_button(
                    label="Download PDF",
                    data=st.session_state.pdf_data,
                    file_name="generated_pdf.pdf",
                    mime="application/pdf"
                )

    if st.session_state.stage == "modal":

        ziffer_dataframe = read_in_goa()

        ziffer_options = ziffer_dataframe['Ziffern'].tolist()

        # Get the data for the ziffer to edit
        if st.session_state.get('ziffer_to_edit') is not None:
            ziffer_data = st.session_state.df.iloc[st.session_state.ziffer_to_edit]
        else:
            ziffer_data = {
                'Ziffer': "",
                'Häufigkeit': None,
                'Intensität': None,
                'Beschreibung': None,
                'Zitat': st.session_state.text,
                'Begründung': None
            }


        # Get the index of the selected ziffer
        try:
            ziffer_index = ziffer_from_options(ziffer_options).index(ziffer_data['Ziffer'])
        except:
            ziffer_index = None
        
        st.subheader("Leistungsziffer aktualisieren")

        st.subheader("Ziffer")
        ziffer = st.selectbox("Ziffer auswählen", options=ziffer_options, index=ziffer_index, placeholder="Bitte wählen Sie eine Ziffer aus ...")

        if ziffer:
            beschreibung = "".join(ziffer.split(" - ")[1:])
            ziffer = ziffer.split(" - ")[0]
        else:
            beschreibung = None

        st.subheader("Häufigkeit")
        haufigkeit = st.number_input("Häufigkeit setzen", value=ziffer_data['Häufigkeit'], placeholder="Bitte wählen Sie die Häufigkeit der Leistung ...", min_value=1, max_value=20)

        st.subheader("Faktor")
        intensitat_value = st.number_input("Faktor setzen", value=ziffer_data["Intensität"], placeholder="Bitte wählen Sie die Intensität der Durchführung der Leistung ...", min_value=0.0, max_value=5.0, step=0.1, format="%.1f")
        intensitat = intensitat_value

        st.subheader("Textzitat")
        zitat = st.text_area("Textzitat einfügen", value=ziffer_data["Zitat"], placeholder="Bitte hier das Textzitat einfügen ...", help="Hier soll ein Zitat aus dem ärztlichen Bericht eingefügt werden, welches die Leistungsziffer begründet.")

        st.subheader("Begründung")
        begrundung = st.text_area("Begründung eingeben", value=ziffer_data["Begründung"], placeholder="Bitte hier die Begründung einfügen ...", help="Hier soll die Begründung für die Leistungsziffer eingefügt werden.")

        left_outer_column, _, _, _, right_outer_column = st.columns([1, 2, 3, 2, 1])

        # Validation check for required fields
        all_fields_filled = all([ziffer, haufigkeit, intensitat, beschreibung, zitat])

        new_data = {
            'Ziffer': ziffer,
            'Häufigkeit': haufigkeit,
            'Intensität': intensitat,
            'Beschreibung': beschreibung,
            "Zitat": zitat,
            "Begründung": begrundung if begrundung else None
        }

        with left_outer_column:
            st.button("Abbrechen", on_click=lambda: st.session_state.update(stage="result"), type="primary", use_container_width=True)

        # Disable "Aktualisieren" button if validation criteria aren't met
        if all_fields_filled:
            with right_outer_column:
                if st.button("Aktualisieren", on_click=lambda: update_ziffer(new_data), type="primary", use_container_width=True):
                        st.rerun()
        else:
            with right_outer_column:
                st.button("Aktualisieren", on_click=None, type="primary", use_container_width=True, disabled=True, help="Bitte füllen Sie alle erforderlichen Felder aus.")

if __name__ == '__main__':
    main()