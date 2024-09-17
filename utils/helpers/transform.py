import streamlit as st

from utils.helpers.db import read_in_goa
from utils.utils import find_zitat_in_text


def annotate_text_update():
    st.session_state.annotated_text_object = [st.session_state.text]

    zitate_to_find = [
        (row["Zitat"], row["Ziffer"]) for index, row in st.session_state.df.iterrows()
    ]

    st.session_state.annotated_text_object = find_zitat_in_text(
        zitate_to_find, st.session_state.annotated_text_object
    )

    # Update st.session_state.df to be in the order as the labels are in the annotated_text_object

    ziffer_order = []

    for i in st.session_state.annotated_text_object:
        if isinstance(i, tuple):
            ziffer_order.append(i[1])

    ziffer_order = list(dict.fromkeys(ziffer_order))

    # Order the dataframe according to the order of the ziffer in the text, if a ziffer is not in the text, it will be at the end

    ziffer_order_dict = {ziffer: order for order, ziffer in enumerate(ziffer_order)}

    st.session_state.df["order"] = st.session_state.df["Ziffer"].map(ziffer_order_dict)

    # Fill NaN values with a large number to ensure these rows go to the end when sorted
    st.session_state.df["order"].fillna(9999, inplace=True)

    # Sort the DataFrame by the 'order' column
    st.session_state.df.sort_values("order", inplace=True)

    # Drop the 'order' column as it's no longer needed
    st.session_state.df.drop("order", axis=1, inplace=True)

    st.session_state.df = st.session_state.df.reset_index(drop=True)


def format_ziffer_to_4digits(ziffer):
    ziffer_parts = ziffer.split(" ", 1)[1]
    numeric_part = "".join(filter(str.isdigit, ziffer_parts))
    alpha_part = "".join(filter(lambda x: not x.isdigit(), ziffer_parts))

    try:
        result = f"{int(numeric_part):04d}{alpha_part}"
    except ValueError:
        result = ziffer_parts
    return result


def df_to_items(df):
    items = []
    goa = read_in_goa(fully=True)

    for idx, row in df.iterrows():
        goa_item = goa[goa["GOÄZiffer"] == row["Ziffer"]]

        analog_ziffer = False

        if goa_item.empty:
            print(
                f"No matching GOÄZiffer for row index {idx} with Ziffer {row['Ziffer']}"
            )
            goa_analog_ziffer = row["Ziffer"].replace(" A", "")
            goa_item = goa[goa["GOÄZiffer"] == goa_analog_ziffer]
            if goa_item.empty:
                print(f"No matching GOÄZiffer for analog Ziffer {goa_analog_ziffer}")
                continue
            else:
                analog_ziffer = True

        intensity = row["Intensität"]

        # Convert intensity to string in both formats
        intensity_str_period = f"{intensity:.1f}"  # Format with period
        intensity_str_comma = intensity_str_period.replace(
            ".", ","
        )  # Format with comma

        # Find columns where intensity matches either format
        matching_columns = goa_item.columns[
            goa_item.apply(
                lambda col: col.astype(str).str.contains(
                    f"(?:{intensity_str_period}|{intensity_str_comma})"
                )
            ).any()
        ]

        if matching_columns.empty:
            matching_columns = ["Regelhöchstfaktor"]

        column_name = matching_columns[0]

        faktor = intensity

        if column_name == "Einfachfaktor":
            preis = float(goa_item["Einfachsatz"].values[0].replace(",", "."))
        elif column_name == "Regelhöchstfaktor":
            preis = float(goa_item["Regelhöchstsatz"].values[0].replace(",", "."))
        elif column_name == "Höchstfaktor":
            preis = float(goa_item["Höchstsatz"].values[0].replace(",", "."))
        elif faktor < 2:
            preis = float(goa_item["Einfachsatz"].values[0].replace(",", "."))
        elif faktor < 3:
            preis = float(goa_item["Regelhöchstsatz"].values[0].replace(",", "."))
        else:
            preis = float(goa_item["Höchstsatz"].values[0].replace(",", "."))

        item = {
            "ziffer": row["Ziffer"],
            "Häufigkeit": row["Häufigkeit"],
            "intensitat": intensity,
            "beschreibung": row["Beschreibung"],
            "Punktzahl": goa_item["Punktzahl"].values[0],
            "preis": preis,
            "faktor": faktor,
            "total": preis * int(row["Häufigkeit"]),
            "auslagen": "",
            "date": "",
            "analog_ziffer": analog_ziffer,
        }

        items.append(item)

    if items:
        if not items[0]["date"]:
            items[0]["date"] = "25.05.24"
    else:
        print("No items were created.")

    return items
