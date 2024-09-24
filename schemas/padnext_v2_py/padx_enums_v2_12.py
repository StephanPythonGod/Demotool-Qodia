from decimal import Decimal
from enum import Enum

__NAMESPACE__ = "http://padinfo.de/ns/pad"


class BehandlungsartEnum(Enum):
    """
    Kennzeichen aus der PAD (300,10)

    :cvar VALUE_0: ambulant
    :cvar VALUE_1: Stationäre Behandlung
    :cvar VALUE_2: Stationäre Mitbehandlung
    :cvar VALUE_3: Vorstationäe Behandlung
    :cvar VALUE_4: Nachstationäre Behandlung
    :cvar VALUE_5: Konsiliarbehandlung
    """

    VALUE_0 = 0
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3
    VALUE_4 = 4
    VALUE_5 = 5


class BelegartEnum(Enum):
    MATERIALPASS = "Materialpass"
    MEHRKOSTENAUFSTELLUNG = "Mehrkostenaufstellung"
    FREMDLABOR = "Fremdlabor"
    EIGENLABOR = "Eigenlabor"
    MATERIAL = "Material"
    HKP = "HKP"
    SONSTIGES = "sonstiges"


class BerechnungskennzeichenEnum(Enum):
    """
    :cvar K: Keine Berechnung der Leistung
    :cvar H: Nur das Honorar der Leistung wird berechnet
    :cvar B: Nur Besondere Kosten werden berechnet
    """

    K = "K"
    H = "H"
    B = "B"


class BesondererpersonenkreisEnum(Enum):
    VALUE_4 = Decimal("4")
    VALUE_6 = Decimal("6")
    VALUE_7 = Decimal("7")
    VALUE_8 = Decimal("8")
    VALUE_9 = Decimal("9")


class DmpkennzeichenEnum(Enum):
    """
    :cvar VALUE_1: Diabetes mellitus Typ 2
    :cvar VALUE_2: Brustkrebs
    :cvar VALUE_3: Koronare Herzkrankheit
    :cvar VALUE_4: Diabetes mellitus Typ 1
    :cvar VALUE_5: Chronisch obstruktive Atemwegserkrankung (COPD)
    :cvar VALUE_6: Asthme bronchiale
    :cvar VALUE_9:
    """

    VALUE_1 = Decimal("1")
    VALUE_2 = Decimal("2")
    VALUE_3 = Decimal("3")
    VALUE_4 = Decimal("4")
    VALUE_5 = Decimal("5")
    VALUE_6 = Decimal("6")
    VALUE_9 = Decimal("9")


class DiagnoseartEnum(Enum):
    """
    :cvar H: Hauptdiagnose
    :cvar N: Nebendiagnose
    :cvar P: Primärdiagnose
    :cvar S: Sekundärdiagnose
    """

    H = "H"
    N = "N"
    P = "P"
    S = "S"


class DiagnosesicherheitEnum(Enum):
    """
    Kennzeichen für die Angabe wie sicher die Diagnose zu werten ist.

    :cvar G: Gesicherte Diagnose
    :cvar V: Verdachtsdiagnose
    :cvar Z: Zustand nach
    :cvar A: Ausgeschlossene Erkrankung
    """

    G = "G"
    V = "V"
    Z = "Z"
    A = "A"


class DiagnosesystemEnum(Enum):
    """
    Angabe des Systems in dem die Diagnose kodiert ist.

    :cvar ICD_10: Diagnose ist angegeben im Format ICD-10 (International
        Statistical Classification of Diseases and Related Health
        Problems).
    :cvar ICPC_2: Diagnose ist angegeben im Format ICPC-2 (International
        Classification in Primary Care v2).
    """

    ICD_10 = "ICD-10"
    ICPC_2 = "ICPC-2"


class DiagnosetypEnum(Enum):
    """Definition der versch.

    Diagnosetypen im ambulanten und stationären Bereich.

    :cvar VALUE_1: Abrechnungsdiagnose: aktuelle Diagnose, aufgrund
        derer eine Abrechnung erfolgt (ambulant)
    :cvar VALUE_2: Dauerdiagnose: Diagnosen, die schon mehr als drei
        Quartale gültig sind  (ambulant)
    :cvar VALUE_3: Aufnahmediagnose (stationär)
    :cvar VALUE_4: Einweisungsdiagnose (stationär)
    :cvar VALUE_5: Fachabteilungsdiagnose (stationär)
    :cvar VALUE_6: Nachfolgediagnose (stationär)
    :cvar VALUE_7: Entlassungsdiagnose (stationär)
    :cvar VALUE_8: Fachabteilungszusatzdiagnose (stationär)
    :cvar VALUE_9: Überweisungsdiagnose (stationär)
    :cvar VALUE_10: Behandlungsdiagnose (stationär)
    """

    VALUE_1 = "1"
    VALUE_2 = "2"
    VALUE_3 = "3"
    VALUE_4 = "4"
    VALUE_5 = "5"
    VALUE_6 = "6"
    VALUE_7 = "7"
    VALUE_8 = "8"
    VALUE_9 = "9"
    VALUE_10 = "10"


class DokumentformatEnum(Enum):
    """
    :cvar PDF: Portable Document Format (Dokumentenformat von Adobe).
    :cvar JPEG: Joint Photographic Experts Group (verlustbehaftete
        komprimierte Bilddateien).
    :cvar TIFF: Tagged Image File Format (universelles Pixelbild-
        Format).
    """

    PDF = "pdf"
    JPEG = "jpeg"
    TIFF = "tiff"


class DokumenttypEnum(Enum):
    PADNE_XT = "PADneXt"
    PAD = "PAD"
    ANHANG = "Anhang"
    PADDENT = "PADdent"


class GebuehrenordnungEnum(Enum):
    """
    :cvar GOAE: Gebührenordnung für Ärzte
    :cvar UVGOAE: Gebührenordnung für Ärzte für die Leistungs- und
        Kostenabrechnung mit den gesetzlichen Unfallversicherungsträgern
    :cvar EBM: Einheitlicher Bewertungsmaßstab
    :cvar GOZ:
    :cvar BEMA:
    :cvar GEBUEH:
    :cvar BEL:
    :cvar BEB:
    """

    GOAE = "GOAE"
    UVGOAE = "UVGOAE"
    EBM = "EBM"
    GOZ = "GOZ"
    BEMA = "BEMA"
    GEBUEH = "GEBUEH"
    BEL = "BEL"
    BEB = "BEB"


class GeschlechtEnum(Enum):
    M = "m"
    W = "w"
    U = "u"


class KontaktartEnum(Enum):
    TELEFONNR = "telefonnr"
    MOBILNR = "mobilnr"
    FAXNR = "faxnr"
    EMAIL = "email"


class KontakttypEnum(Enum):
    PRIVAT = "privat"
    BERUFLICH = "beruflich"


class LandEnum(Enum):
    """
    Länderkennzeichen.

    :cvar AFG: Afghanistan
    :cvar ET: Ägypten
    :cvar AL: Albanien
    :cvar GBA: Alderney
    :cvar DZ: Algerien
    :cvar AND: Andorra
    :cvar ANG: Angola
    :cvar RA: Argentinien
    :cvar AM: Armenien
    :cvar AZ: Aserbaidschan
    :cvar ETH: Äthiopien
    :cvar AUS: Australien
    :cvar BS: Bahamas
    :cvar BRN: Bahrain
    :cvar BD: Bangladesch
    :cvar BDS: Barbados
    :cvar BY: Belarus (Weißrussland)
    :cvar B: Belgien
    :cvar BH: Belize
    :cvar BJ: Benin
    :cvar BOL: Bolivien
    :cvar BIH: Bosnien und Herzegowina
    :cvar RB: Botsuana
    :cvar BR: Brasilien
    :cvar BRU: Brunei Darussalam
    :cvar BG: Bulgarien
    :cvar BF: Burkina Faso
    :cvar RU: Burundi
    :cvar RCH: Chile
    :cvar RC: China (Taiwan)
    :cvar CR: Costa Rica
    :cvar CI: Côte d’Ivoire
    :cvar DK: Dänemark
    :cvar CD: Demokratische Republik Kongo
    :cvar LAO: Demokratische Volksrepublik Laos
    :cvar D: Deutschland
    :cvar WD: Dominica
    :cvar DOM: Dominikanische Republik
    :cvar DJI: Dschibuti
    :cvar EC: Ecuador
    :cvar ES: El Salvador
    :cvar ER: Eritrea
    :cvar EST: Estland
    :cvar FO: Färöer
    :cvar FJI: Fidschi
    :cvar FIN: Finnland
    :cvar F: Frankreich
    :cvar G: Gabun
    :cvar WAG: Gambia
    :cvar GE: Georgien
    :cvar GH: Ghana
    :cvar GBZ: Gibraltar
    :cvar WG: Grenada
    :cvar GR: Griechenland
    :cvar GCA: Guatemala
    :cvar GBG: Guernsey
    :cvar RG: Guinea
    :cvar GUY: Guyana
    :cvar RH: Haiti
    :cvar HN: Honduras
    :cvar IND: Indien
    :cvar RI: Indonesien
    :cvar MAN: Insel
    :cvar IRQ: Irak
    :cvar IR: Iran
    :cvar IRL: Irland
    :cvar IS: Island
    :cvar IL: Israel
    :cvar I: Italien
    :cvar JA: Jamaika
    :cvar J: Japan
    :cvar YAR: Jemen
    :cvar GBJ: Jersey
    :cvar JOR: Jordanien
    :cvar K: Kambodscha
    :cvar CAM: Kamerun
    :cvar CDN: Kanada
    :cvar KZ: Kasachstan
    :cvar Q: Katar
    :cvar EAK: Kenia
    :cvar KS: Kirgisistan
    :cvar CO: Kolumbien
    :cvar RCB: Kongo
    :cvar KSA: Königreich Saudi-Arabien
    :cvar ROK: Korea (Republik)
    :cvar KOS: Kosovo
    :cvar HR: Kroatien
    :cvar C: Kuba
    :cvar KWT: Kuwait
    :cvar LS: Lesotho
    :cvar LV: Lettland
    :cvar RL: Libanon
    :cvar LB: Liberia
    :cvar FL: Liechtenstein
    :cvar LT: Litauen
    :cvar L: Luxemburg
    :cvar LAR: Lybien
    :cvar RM: Madagaskar
    :cvar MW: Malawi
    :cvar MAL: Malaysia
    :cvar RMM: Mali
    :cvar M: Malta
    :cvar MA: Marokko
    :cvar RIM: Mauretanien
    :cvar MS: Mauritius
    :cvar MK: Mazedonien (ehem. jugosl. Republik)
    :cvar MEX: Mexiko
    :cvar MD: Moldau
    :cvar MC: Monaco
    :cvar MGL: Mongolei
    :cvar MNE: Montenegro
    :cvar MOC: Mosambik
    :cvar MYA: Myanmar
    :cvar NAM: Namibia
    :cvar NAU: Nauru
    :cvar NEP: Nepal
    :cvar NZ: Neuseeland
    :cvar NIC: Nicaragua
    :cvar NA: Niederländ. Antillen
    :cvar NL: Niederlande
    :cvar RN: Niger
    :cvar WAN: Nigeria
    :cvar N: Norwegen
    :cvar OM: Oman
    :cvar A: Österreich
    :cvar PK: Pakistan
    :cvar PA: Panama
    :cvar PNG: Papua-Neugiuinea
    :cvar PY: Paraguay
    :cvar PE: Peru
    :cvar RP: Philippinen
    :cvar PL: Polen
    :cvar P: Portugal
    :cvar RWA: Ruanda
    :cvar RO: Rum?nien
    :cvar RUS: Russische Föderation
    :cvar Z: Sambia
    :cvar WS: Samoa
    :cvar RSM: San Marino
    :cvar EAZ: Sansibar
    :cvar WL: Santa Lucia
    :cvar S: Schweden
    :cvar CH: Schweiz
    :cvar SN: Senegal
    :cvar SRB: Serbien
    :cvar SY: Seyschellen
    :cvar WAL: Sierra Leone
    :cvar ZW: Simbabwe
    :cvar SGP: Singapur
    :cvar SK: Slowakische Republik
    :cvar SLO: Slowenien
    :cvar SO: Somalia
    :cvar E: Spanien
    :cvar CL: Sri-Lanka
    :cvar WV: St. Vincent und die Grenadinen
    :cvar ZA: Südafrika
    :cvar SUD: Sudan
    :cvar SME: Surinam
    :cvar SD: Swasiland
    :cvar SYR: Syrien
    :cvar TJ: Tadschikistan
    :cvar EAT: Tansania
    :cvar THA: Thailand
    :cvar RT: Togo
    :cvar TT: Trinidad und Tobago
    :cvar TD: Tschad
    :cvar CZ: Tschechische Republik
    :cvar TN: Tunesien
    :cvar TR: Türkei
    :cvar TM: Turkmenistan
    :cvar EAU: Uganda
    :cvar UA: Ukraine
    :cvar H: Ungarn
    :cvar ROU: Uruguay
    :cvar UZ: Usbekistan
    :cvar V: Vatikanstadt
    :cvar YV: Venezuela
    :cvar UAE: Vereinigte Arabische Emirate
    :cvar USA: Vereinigte Staaten
    :cvar GB: Vereinigtes Königreich
    :cvar VN: Vietnam
    :cvar RCA: Zentralafrikanische Republik
    :cvar CY: Zypern
    :cvar UNB: Unbekannt
    """

    AFG = "AFG"
    ET = "ET"
    AL = "AL"
    GBA = "GBA"
    DZ = "DZ"
    AND = "AND"
    ANG = "ANG"
    RA = "RA"
    AM = "AM"
    AZ = "AZ"
    ETH = "ETH"
    AUS = "AUS"
    BS = "BS"
    BRN = "BRN"
    BD = "BD"
    BDS = "BDS"
    BY = "BY"
    B = "B"
    BH = "BH"
    BJ = "BJ"
    BOL = "BOL"
    BIH = "BIH"
    RB = "RB"
    BR = "BR"
    BRU = "BRU"
    BG = "BG"
    BF = "BF"
    RU = "RU"
    RCH = "RCH"
    RC = "RC"
    CR = "CR"
    CI = "CI"
    DK = "DK"
    CD = "CD"
    LAO = "LAO"
    D = "D"
    WD = "WD"
    DOM = "DOM"
    DJI = "DJI"
    EC = "EC"
    ES = "ES"
    ER = "ER"
    EST = "EST"
    FO = "FO"
    FJI = "FJI"
    FIN = "FIN"
    F = "F"
    G = "G"
    WAG = "WAG"
    GE = "GE"
    GH = "GH"
    GBZ = "GBZ"
    WG = "WG"
    GR = "GR"
    GCA = "GCA"
    GBG = "GBG"
    RG = "RG"
    GUY = "GUY"
    RH = "RH"
    HN = "HN"
    IND = "IND"
    RI = "RI"
    MAN = "Man"
    IRQ = "IRQ"
    IR = "IR"
    IRL = "IRL"
    IS = "IS"
    IL = "IL"
    I = "I"
    JA = "JA"
    J = "J"
    YAR = "YAR"
    GBJ = "GBJ"
    JOR = "JOR"
    K = "K"
    CAM = "CAM"
    CDN = "CDN"
    KZ = "KZ"
    Q = "Q"
    EAK = "EAK"
    KS = "KS"
    CO = "CO"
    RCB = "RCB"
    KSA = "KSA"
    ROK = "ROK"
    KOS = "KOS"
    HR = "HR"
    C = "C"
    KWT = "KWT"
    LS = "LS"
    LV = "LV"
    RL = "RL"
    LB = "LB"
    FL = "FL"
    LT = "LT"
    L = "L"
    LAR = "LAR"
    RM = "RM"
    MW = "MW"
    MAL = "MAL"
    RMM = "RMM"
    M = "M"
    MA = "MA"
    RIM = "RIM"
    MS = "MS"
    MK = "MK"
    MEX = "MEX"
    MD = "MD"
    MC = "MC"
    MGL = "MGL"
    MNE = "MNE"
    MOC = "MOC"
    MYA = "MYA"
    NAM = "NAM"
    NAU = "NAU"
    NEP = "NEP"
    NZ = "NZ"
    NIC = "NIC"
    NA = "NA"
    NL = "NL"
    RN = "RN"
    WAN = "WAN"
    N = "N"
    OM = "OM"
    A = "A"
    PK = "PK"
    PA = "PA"
    PNG = "PNG"
    PY = "PY"
    PE = "PE"
    RP = "RP"
    PL = "PL"
    P = "P"
    RWA = "RWA"
    RO = "RO"
    RUS = "RUS"
    Z = "Z"
    WS = "WS"
    RSM = "RSM"
    EAZ = "EAZ"
    WL = "WL"
    S = "S"
    CH = "CH"
    SN = "SN"
    SRB = "SRB"
    SY = "SY"
    WAL = "WAL"
    ZW = "ZW"
    SGP = "SGP"
    SK = "SK"
    SLO = "SLO"
    SO = "SO"
    E = "E"
    CL = "CL"
    WV = "WV"
    ZA = "ZA"
    SUD = "SUD"
    SME = "SME"
    SD = "SD"
    SYR = "SYR"
    TJ = "TJ"
    EAT = "EAT"
    THA = "THA"
    RT = "RT"
    TT = "TT"
    TD = "TD"
    CZ = "CZ"
    TN = "TN"
    TR = "TR"
    TM = "TM"
    EAU = "EAU"
    UA = "UA"
    H = "H"
    ROU = "ROU"
    UZ = "UZ"
    V = "V"
    YV = "YV"
    UAE = "UAE"
    USA = "USA"
    GB = "GB"
    VN = "VN"
    RCA = "RCA"
    CY = "CY"
    UNB = "unb"


class LeistungsartkfoEnum(Enum):
    SACHLEISTUNG_KONS_CHIR = "Sachleistung Kons/Chir"
    SACHLEISTUNG_IP = "Sachleistung IP"
    KOSTENERSTATTUNGSLEISTUNG = "Kostenerstattungsleistung"


class LokalisationEnum(Enum):
    """
    :cvar L: links
    :cvar R: rechts
    :cvar B: beidseits
    """

    L = "L"
    R = "R"
    B = "B"


class MahnkennzeichenEnum(Enum):
    NICHT_MAHNEN = "nicht mahnen"
    MAHNEN = "mahnen"
    KEIN_GMV = "kein gmv"


class MinderungssatzEnum(Enum):
    VALUE_0 = Decimal("0")
    VALUE_15 = Decimal("15")
    VALUE_25 = Decimal("25")


class NachrichtentypEnum(Enum):
    ADL = "ADL"
    QADL = "QADL"


class PositionskennzeichenEnum(Enum):
    """
    :cvar M: Auslagen für Medikamente, Arzneimittel
    :cvar L: Auslagen für Material, Verbandsmittel, Radiopharmaka etc.
    :cvar P: Auslagen für Porto, Versandkosten
    """

    M = "M"
    L = "L"
    P = "P"


class RatenvereinbarungEnum(Enum):
    """
    :cvar P: Vereinbarung durch PVS
    :cvar A: Vereinbarung durch Arzt
    """

    P = "P"
    A = "A"


class RechnungssondertypEnum(Enum):
    """
    Kennzeichen aus der PAD (300,13)

    :cvar I: Igelrechnung / Selbstzahlerrechnung
    :cvar P: Praxisgebühr
    """

    I = "I"
    P = "P"


class UnterkunftstationaerEnum(Enum):
    """
    :cvar VALUE_1: Einbett Zimmer
    :cvar VALUE_2: Zweibett Zimmer
    :cvar VALUE_3: Mehrbett Zimmer
    """

    VALUE_1 = "1"
    VALUE_2 = "2"
    VALUE_3 = "3"


class VersichertenartEnum(Enum):
    VALUE_1 = Decimal("1")
    VALUE_3 = Decimal("3")
    VALUE_5 = Decimal("5")
    VALUE_9 = Decimal("9")


class VerwandtschaftskennungEnum(Enum):
    """
    :cvar VALUE_0: Keine Angabe
    :cvar VALUE_1: Behandelter ist identisch mit Versicherten
    :cvar VALUE_2: Ehepartner
    :cvar VALUE_3: Tochter
    :cvar VALUE_4: Sohn
    :cvar VALUE_5: Nicht selbst versichert
    """

    VALUE_0 = Decimal("0")
    VALUE_1 = Decimal("1")
    VALUE_2 = Decimal("2")
    VALUE_3 = Decimal("3")
    VALUE_4 = Decimal("4")
    VALUE_5 = Decimal("5")


class VerwendungszweckanhangEnum(Enum):
    """
    :cvar VALUE_1: Anzeigen
    :cvar VALUE_2: Drucken
    """

    VALUE_1 = Decimal("1")
    VALUE_2 = Decimal("2")


class ZahlungsartEnum(Enum):
    """
    Kennzeichen aus der PAD (300,19)

    :cvar LASTSCHRIFT: Lastschrift
    """

    LASTSCHRIFT = "Lastschrift"
