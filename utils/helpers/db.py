import pandas as pd


def read_in_goa(path="./data/GOA_Ziffern.csv", fully=False):
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
