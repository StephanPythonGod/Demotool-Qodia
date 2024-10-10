from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any, List, Optional

from xsdata.models.datatype import XmlDate, XmlTime

from schemas.padnext_v2_py.padx_enums_v2_12 import (
    BehandlungsartEnum,
    BelegartEnum,
    BerechnungskennzeichenEnum,
    BesondererpersonenkreisEnum,
    DiagnoseartEnum,
    DiagnosesicherheitEnum,
    DiagnosesystemEnum,
    DiagnosetypEnum,
    DmpkennzeichenEnum,
    DokumentformatEnum,
    DokumenttypEnum,
    GebuehrenordnungEnum,
    GeschlechtEnum,
    KontaktartEnum,
    KontakttypEnum,
    LandEnum,
    LeistungsartkfoEnum,
    LokalisationEnum,
    MahnkennzeichenEnum,
    MinderungssatzEnum,
    NachrichtentypEnum,
    PositionskennzeichenEnum,
    RatenvereinbarungEnum,
    RechnungssondertypEnum,
    UnterkunftstationaerEnum,
    VersichertenartEnum,
    VerwandtschaftskennungEnum,
    VerwendungszweckanhangEnum,
    ZahlungsartEnum,
)

__NAMESPACE__ = "http://padinfo.de/ns/pad"


class AuslagenTypBerechnung(Enum):
    """
    :cvar K: Keine Berechnung der Leistung
    """

    K = "K"


@dataclass
class BegruendungTyp:
    class Meta:
        name = "Begruendung.Typ"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "min_length": 1,
            "max_length": 4000,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "max_length": 40,
        },
    )


@dataclass
class BehandlungsortTyp:
    """
    :ivar bsnr: Die Betriebsstättennummer ist der Vertragsarztsitz.
    :ivar nbsnr: Die Nebenbetriebsstättennr. gibt weitere Tätigkeitsorte
        an.
    """

    class Meta:
        name = "Behandlungsort.Typ"

    bsnr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 9,
        },
    )
    nbsnr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 9,
        },
    )


@dataclass
class BeteiligungTyp:
    """
    :ivar betrag: Höhe der Beteiligung in Euro.
    :ivar prozent: Höhe der Beteiligung in Prozent.
    :ivar lautverrechnungsstelle:
    :ivar beteiligter:
    """

    class Meta:
        name = "Beteiligung.Typ"

    betrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    prozent: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )
    lautverrechnungsstelle: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    beteiligter: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 20,
        },
    )


@dataclass
class BetragBezeichnungTyp:
    class Meta:
        name = "BetragBezeichnung.Typ"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    bezeichnung: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 80,
        },
    )


@dataclass
class BetragBezeichnungSatzTyp:
    class Meta:
        name = "BetragBezeichnungSatz.Typ"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    bezeichnung: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 40,
        },
    )
    satz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )


@dataclass
class BetragSatzTyp:
    class Meta:
        name = "BetragSatz.Typ"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    satz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )


@dataclass
class DateilaengeTyp:
    """
    :ivar laenge: Angabe in Bytes.
    :ivar pruefsumme: Verwendet wird das SHA-1 Verfahren.
    """

    class Meta:
        name = "Dateilaenge.Typ"

    laenge: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    pruefsumme: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "length": 40,
        },
    )


@dataclass
class FachangabeTyp:
    class Meta:
        name = "Fachangabe.Typ"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    textname: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )


@dataclass
class FehlerTyp:
    """
    :ivar code: Fehlercode.
    :ivar text: Fehlertext.
    :ivar hinweis: Weitere Hinweise.
    """

    class Meta:
        name = "Fehler.Typ"

    code: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    hinweis: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class HonorarTypBerechnung(Enum):
    """
    :cvar K: Keine Berechnung der Leistung
    """

    K = "K"


@dataclass
class KfoplandatenTyp:
    """
    :ivar leistungsquartal: 1
    :ivar leistungsjahr: 2013
    :ivar leerquartal:
    :ivar abschlagsnr: 99
    :ivar planungsdatum:
    :ivar verlaengerungsdatum:
    :ivar behandlungsbeginn:
    :ivar behandlungsende:
    """

    class Meta:
        name = "Kfoplandaten.Typ"

    leistungsquartal: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": 1,
            "max_inclusive": 4,
        },
    )
    leistungsjahr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 4,
        },
    )
    leerquartal: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    abschlagsnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 8,
        },
    )
    planungsdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    verlaengerungsdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandlungsbeginn: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    behandlungsende: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )


@dataclass
class KontoTyp:
    """
    :ivar inhaber: Name des Kontoinhabers.
    :ivar bank: Name der Bank.
    :ivar blz:
    :ivar kontonr:
    :ivar bic:
    :ivar iban:
    :ivar mandatsreferenz:
    """

    class Meta:
        name = "Konto.Typ"

    inhaber: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 27,
            "pattern": r".*[^\s].*",
        },
    )
    bank: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 27,
        },
    )
    blz: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 8,
        },
    )
    kontonr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 10,
        },
    )
    bic: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 11,
        },
    )
    iban: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "length": 22,
        },
    )
    mandatsreferenz: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 40,
        },
    )


@dataclass
class LeistungspositionTyp:
    """
    Basistyp für alle GO Leistungspositionen.

    :ivar leistungserbringerid: Identifizierung des LE für die
        angegebene Leistung (falls abweichend von der übergreifenden
        Angabe).
    :ivar datum: Datum der Leistungserbingung.
    :ivar uhrzeit: Uhrzeit der Leistungserbingung.
    :ivar anzahl:
    :ivar text: Positionstext für erbrachte Leistung.
    :ivar zusatztext: Zusatztext für erbrachte Leistung.
    :ivar positionsnr: Legt die Reihenfolge bei Ausdrudck der Positionen
        fest.
    :ivar id: Optionaler eindeutiger Bezeichner für Position (für
        Gruppierungen und Verweise zw. Positionen).
    :ivar idref: Optionaler Bezeichner zum Setzen einer Referenz zu
        einer anderen Position (id Attribut).
    """

    class Meta:
        name = "Leistungsposition.Typ"

    leistungserbringerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    datum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    uhrzeit: Optional[XmlTime] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    anzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 4,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 4000,
        },
    )
    zusatztext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    positionsnr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )
    idref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )


@dataclass
class Leistungsposition2Typ:
    """
    Basistyp für alle GO Leistungspositionen.

    :ivar leistungserbringerid: Identifizierung des LE für die
        angegebene Leistung (falls abweichend von der übergreifenden
        Angabe).
    :ivar datum: Datum der Leistungserbingung.
    :ivar uhrzeit: Uhrzeit der Leistungserbingung.
    :ivar anzahl:
    :ivar text: Positionstext für erbrachte Leistung.
    :ivar zusatztext: Zusatztext für erbrachte Leistung.
    :ivar positionsnr: Legt die Reihenfolge bei Ausdrudck der Positionen
        fest.
    :ivar id: Optionaler eindeutiger Bezeichner für Position (für
        Gruppierungen und Verweise zw. Positionen).
    :ivar idref: Optionaler Bezeichner zum Setzen einer Referenz zu
        einer anderen Position (id Attribut).
    """

    class Meta:
        name = "Leistungsposition2.Typ"

    leistungserbringerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    datum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    uhrzeit: Optional[XmlTime] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    anzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 4,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 4000,
        },
    )
    zusatztext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    positionsnr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )
    idref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )


@dataclass
class MaterialZifferTyp:
    """
    Ziffer Beleg Material.

    :ivar datum: Datum der Leistungserbingung.
    :ivar menge:
    :ivar einheit:
    :ivar text: Positionstext für erbrachte Leistung.
    :ivar einzelbetrag: Einzelbetrag für Leistung (ohne Minderungen und
        Umsatzsteuer).
    :ivar gesamtbetrag:
    :ivar mwstsatz: Kennzeichen für den Umsatzsteuersatz der Position
        (ist nicht in den anderen Beträgen enthalten).
    :ivar positionsnr: Legt die Reihenfolge bei Ausdrudck der Positionen
        fest.
    """

    class Meta:
        name = "MaterialZiffer.Typ"

    datum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    menge: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    einheit: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 4000,
        },
    )
    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    mwstsatz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )
    positionsnr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class MaterialpassZifferTyp:
    """
    Ziffer Beleg Materialpass.
    """

    class Meta:
        name = "MaterialpassZiffer.Typ"

    bezeichnung: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 100,
        },
    )
    hersteller: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 100,
        },
    )
    seriennr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 100,
        },
    )
    chargennr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 100,
        },
    )
    bestandteile: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 100,
        },
    )
    erklaerung: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 100,
        },
    )


@dataclass
class NachlassTyp:
    class Meta:
        name = "Nachlass.Typ"

    betrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    prozent: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )


@dataclass
class PackstationTyp:
    class Meta:
        name = "Packstation.Typ"

    postnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 10,
            "pattern": r".*[^\s].*",
        },
    )
    packstationnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 10,
            "pattern": r".*[^\s].*",
        },
    )
    plz: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 10,
            "pattern": r".*[^\s].*",
        },
    )
    ort: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 40,
            "pattern": r".*[^\s].*",
        },
    )


@dataclass
class PostfachTyp:
    class Meta:
        name = "Postfach.Typ"

    postfachnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 10,
            "pattern": r".*[^\s].*",
        },
    )
    plz: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 10,
            "pattern": r".*[^\s].*",
        },
    )
    ort: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 40,
            "pattern": r".*[^\s].*",
        },
    )


class ReisekostenTypAbwesenheit(Enum):
    """
    :cvar VALUE_0: Abwesenheit bis zu 8 Stunden.
    :cvar VALUE_1: Abwesenheit von mehr als 8 Stunden.
    """

    VALUE_0 = "0"
    VALUE_1 = "1"


@dataclass
class SummenblockBmgTyp:
    """
    :ivar gozeigenlabor:
    :ivar gozfremdlabor:
    :ivar gozzwischensummehonorar: ohne Umsatzsteuer
    :ivar gozauslagen:
    :ivar gozwegegeld:
    :ivar gozrechnungsbetrag: inkl. Umsatzsteuer
    :ivar gozvorauszahlung:
    :ivar gozminderungsbetrag:
    :ivar gozvorleistung:
    :ivar gozzahlbetrag: Inklusive Umsatzsteuer
    :ivar gozustvoll: Umsatzsteuer bei Verlangensleistung (voll)
    :ivar gozustgemindert: Umsatzsteuer bei verlangensleistung
        (gemindert)
    """

    class Meta:
        name = "SummenblockBmg.Typ"

    gozeigenlabor: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozfremdlabor: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozzwischensummehonorar: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozauslagen: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozwegegeld: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozrechnungsbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozvorauszahlung: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozminderungsbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozvorleistung: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozzahlbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozustvoll: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gozustgemindert: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )


@dataclass
class TeilnehmerTyp:
    """
    :ivar logisch: Angabe des Eigners der Daten.
    :ivar physikalisch: Angabe des Partners, der die Daten tatsächlich
        empfängt bzw. versendet.
    """

    class Meta:
        name = "Teilnehmer.Typ"

    logisch: Optional["TeilnehmerTyp.Logisch"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    physikalisch: Optional["TeilnehmerTyp.Physikalisch"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )

    @dataclass
    class Logisch:
        value: str = field(
            default="",
            metadata={
                "required": True,
                "min_length": 1,
                "max_length": 40,
            },
        )
        kundennr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "total_digits": 20,
            },
        )
        rzid: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "total_digits": 4,
            },
        )
        iknr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "total_digits": 9,
            },
        )

    @dataclass
    class Physikalisch:
        value: str = field(
            default="",
            metadata={
                "required": True,
                "min_length": 1,
                "max_length": 40,
            },
        )
        kundennr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "total_digits": 20,
            },
        )
        rzid: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "total_digits": 4,
            },
        )
        iknr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "total_digits": 9,
            },
        )


@dataclass
class TextzeileTyp:
    """
    Textposition ohne Bezug zu einer Leistungsziffer.

    :ivar text: Positionstext für erbrachte Leistung.
    :ivar id: Optionaler eindeutiger Bezeichner für Position (für
        Gruppierungen und Verweise zw. Positionen).
    :ivar idref: Optionaler Bezeichner zum Setzen einer Referenz zu
        einer anderen Position (id Attribut).
    :ivar positionsnr: Legt die Reihenfolge bei Ausdrudck der Positionen
        fest.
    """

    class Meta:
        name = "Textzeile.Typ"

    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 4000,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )
    idref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )
    positionsnr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


class WegegeldTypRadius(Enum):
    VALUE_2 = 2
    VALUE_5 = 5
    VALUE_10 = 10
    VALUE_25 = 25


class WegegeldTypTageszeit(Enum):
    T = "T"
    N = "N"


@dataclass
class ZeitraumTyp:
    class Meta:
        name = "Zeitraum.Typ"

    startdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    endedatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    anzahltage: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 4,
        },
    )


@dataclass
class AnhangidTyp:
    """
    :ivar id: Eindeutiger Bezeichner für Anhangsdokument (kann ID oder
        Dateiname sein).
    :ivar verwendungszweck:
    :ivar belegart: Eigenlabor, Fremdlabor, Material, Materialpass,
        Mehrkostenaufstellung
    """

    class Meta:
        name = "Anhangid.Typ"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "max_length": 40,
        },
    )
    verwendungszweck: Optional[VerwendungszweckanhangEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    belegart: Optional[BelegartEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass
class AuslagenpositionTyp:
    """
    Basistyp für alle Nicht-GO Leistungspositionen.

    :ivar leistungserbringerid: Identifizierung des LE für die
        angegebene Leistung (falls abweichend von der übergreifenden
        Angabe).
    :ivar datum: Datum der Leistungserbingung.
    :ivar uhrzeit: Uhrzeit der Leistungserbingung.
    :ivar anzahl:
    :ivar text: Positionstext für erbrachte Leistung.
    :ivar zusatztext: Zusatztext für erbrachte Leistung.
    :ivar beteiligung: Angabe von Arztbeteiligungen auf Positionsebene.
    :ivar positionsnr: Legt die Reihenfolge bei Ausdrudck der Positionen
        fest.
    :ivar id: Optionaler eindeutiger Bezeichner für Position (für
        Gruppierungen und Verweise zw. Positionen).
    :ivar idref: Optionaler Bezeichner zum Setzen einer Referenz zu
        einer anderen Position (id Attribut).
    """

    class Meta:
        name = "Auslagenposition.Typ"

    leistungserbringerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    datum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    uhrzeit: Optional[XmlTime] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    anzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 4,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 4000,
        },
    )
    zusatztext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    beteiligung: List[BeteiligungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    positionsnr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )
    idref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )


@dataclass
class AuslandadresseTyp:
    class Meta:
        name = "Auslandadresse.Typ"

    land: Optional[LandEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    plz: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 10,
            "pattern": r".*[^\s].*",
        },
    )
    ort: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 40,
            "pattern": r".*[^\s].*",
        },
    )
    strasse: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 40,
            "pattern": r".*[^\s].*",
        },
    )


@dataclass
class BemaKfozifferTyp(Leistungsposition2Typ):
    """
    KFO Leistungsposition BEMA.

    :ivar anteil: Wird eine Leistung nur zum Teil in Rechnung gestellt,
        wird hier der Anteil angegeben.
    :ivar zahnangabe:
    :ivar leistungsart:
    :ivar edv_nr:
    :ivar punktwert:
    :ivar punktzahl:
    :ivar punktzahlgesamt:
    :ivar einzelbetrag: Einzelbetrag für Leistung (ohne Minderungen und
        Umsatzsteuer).
    :ivar gesamtbetrag:
    :ivar berechnung: Angabe, ob die Leistung nicht berechnet, nur das
        Honorar oder die Sachkosten berechnet werden.
    :ivar go:
    :ivar goversion:
    :ivar ziffer:
    :ivar abzug: z. B. bei Mehrkosten bei Füllungstherapie
    """

    class Meta:
        name = "BemaKFOZiffer.Typ"

    anteil: Optional["BemaKfozifferTyp.Anteil"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zahnangabe: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 100,
        },
    )
    leistungsart: Optional[LeistungsartkfoEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    edv_nr: Optional[int] = field(
        default=None,
        metadata={
            "name": "edv-nr",
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_inclusive": 9999,
        },
    )
    punktwert: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 9,
            "fraction_digits": 7,
        },
    )
    punktzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 5,
        },
    )
    punktzahlgesamt: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 5,
        },
    )
    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    berechnung: Optional[BerechnungskennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    go: GebuehrenordnungEnum = field(
        init=False,
        default=GebuehrenordnungEnum.BEMA,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    goversion: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 10,
        },
    )
    ziffer: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_length": 1,
            "max_length": 8,
        },
    )
    abzug: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass
    class Anteil:
        zaehler: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 1,
            },
        )
        nenner: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 2,
            },
        )


@dataclass
class BemaKfozwSummeTyp:
    """
    KFO Zwischensumme BEMA.

    :ivar text: Text für Zwischensumme
    :ivar leistungsart:
    :ivar punktwert:
    :ivar punktzahlgesamt:
    :ivar gesamtbetrag:
    :ivar positionsnr: Legt die Reihenfolge bei Ausdrudck der Positionen
        fest.
    """

    class Meta:
        name = "BemaKFOZwSumme.Typ"

    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 4000,
        },
    )
    leistungsart: Optional[LeistungsartkfoEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    punktwert: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 9,
            "fraction_digits": 7,
        },
    )
    punktzahlgesamt: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 5,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    positionsnr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class BemaZifferTyp(LeistungspositionTyp):
    """
    Leistungsposition BEMA.

    :ivar anteil: Wird eine Leistung nur zum Teil in Rechnung gestellt,
        wird hier der Anteil angegeben.
    :ivar zahnangabe:
    :ivar punktwert:
    :ivar punktzahl:
    :ivar einzelbetrag: Einzelbetrag für Leistung (ohne Minderungen und
        Umsatzsteuer).
    :ivar gesamtbetrag:
    :ivar berechnung: Angabe, ob die Leistung nicht berechnet, nur das
        Honorar oder die Sachkosten berechnet werden.
    :ivar go:
    :ivar goversion:
    :ivar ziffer:
    :ivar abzug: z. B. bei Mehrkosten bei Füllungstherapie
    """

    class Meta:
        name = "BemaZiffer.Typ"

    anteil: Optional["BemaZifferTyp.Anteil"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zahnangabe: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 100,
        },
    )
    punktwert: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 9,
            "fraction_digits": 7,
        },
    )
    punktzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 5,
        },
    )
    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    berechnung: Optional[BerechnungskennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    go: GebuehrenordnungEnum = field(
        init=False,
        default=GebuehrenordnungEnum.BEMA,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    goversion: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 10,
        },
    )
    ziffer: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_length": 1,
            "max_length": 8,
        },
    )
    abzug: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass
    class Anteil:
        zaehler: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 1,
            },
        )
        nenner: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 2,
            },
        )


@dataclass
class DiagnosecodeTyp:
    class Meta:
        name = "Diagnosecode.Typ"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "min_length": 1,
            "max_length": 15,
        },
    )
    system: Optional[DiagnosesystemEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class DokumenttypTyp:
    """
    :ivar value:
    :ivar format: Angabe eines MIME-Typ (z.B. msword oder pdf).
    """

    class Meta:
        name = "Dokumenttyp.Typ"

    value: Optional[DokumenttypEnum] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    format: Optional[DokumentformatEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass
class EigenlaborKfozifferTyp(Leistungsposition2Typ):
    """
    :ivar einheit:
    :ivar einzelbetrag: Einzelbetrag für Leistung (ohne Minderungen und
        Umsatzsteuer).
    :ivar gesamtbetrag:
    :ivar mwstsatz: Kennzeichen für den Umsatzsteuersatz der Position
        (ist nicht in den anderen Beträgen enthalten).
    :ivar berechnung: Angabe, ob die Leistung nicht berechnet, nur das
        Honorar oder die Sachkosten berechnet werden.
    :ivar go:
    :ivar goversion:
    :ivar ziffer:
    """

    class Meta:
        name = "EigenlaborKFOZiffer.Typ"

    einheit: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    mwstsatz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )
    berechnung: Optional[BerechnungskennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    go: Optional[GebuehrenordnungEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"BEB|BEL",
        },
    )
    goversion: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 10,
        },
    )
    ziffer: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 8,
        },
    )


@dataclass
class FachbereichTyp:
    class Meta:
        name = "Fachbereich.Typ"

    fachgebiet: Optional[FachangabeTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    facharzt: List[FachangabeTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )


@dataclass
class GozzifferTyp(LeistungspositionTyp):
    """
    Leistungsposition GOZ.

    :ivar faktor: Faktor für erbrachte Leistung nach der jeweiligen
        Gebührenordnung.
    :ivar vorgabebetrag: Vorgabe des Einzelbetrages für Leistung (ohne
        Minderungen und Umsatzsteuer).
    :ivar anteil: Wird eine Leistung nur zum Teil in Rechnung gestellt,
        wird hier der Anteil angegeben (z.B. Abrechnung eines halben
        Zuschlags nach Ziffer D GOÄ, wenn die Leistung innerhalb der
        Sprechstunde an Samstagen erbracht wurde).
    :ivar minderungssatz: Minderungssatz, um den das Honorar ggf. zu
        mindern ist (ist nicht in den anderen Beträgen enthalten).
    :ivar zahnangabe:
    :ivar punktwert:
    :ivar punktzahl:
    :ivar einzelbetrag: Einzelbetrag für Leistung (ohne Minderungen und
        Umsatzsteuer).
    :ivar gesamtbetrag:
    :ivar mwstsatz: Kennzeichen für den Umsatzsteuersatz der Position
        (ist nicht in den anderen Beträgen enthalten).
    :ivar begruendungstext:
    :ivar begruendungsrefid:
    :ivar berechnung: Angabe, ob die Leistung nicht berechnet, nur das
        Honorar oder die Sachkosten berechnet werden.
    :ivar abzug: z. B. bei Mehrkosten bei Füllungstherapie
    :ivar go:
    :ivar goversion:
    :ivar analog:
    :ivar ziffer:
    :ivar verlangensleistung:
    """

    class Meta:
        name = "GOZZiffer.Typ"

    faktor: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 8,
            "fraction_digits": 6,
        },
    )
    vorgabebetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    anteil: Optional["GozzifferTyp.Anteil"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    minderungssatz: Optional[MinderungssatzEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zahnangabe: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 100,
        },
    )
    punktwert: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 9,
            "fraction_digits": 7,
        },
    )
    punktzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 5,
        },
    )
    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    mwstsatz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )
    begruendungstext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    begruendungsrefid: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    berechnung: Optional[BerechnungskennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    abzug: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    go: GebuehrenordnungEnum = field(
        init=False,
        default=GebuehrenordnungEnum.GOZ,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    goversion: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 10,
        },
    )
    analog: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 8,
        },
    )
    ziffer: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_length": 1,
            "max_length": 8,
        },
    )
    verlangensleistung: bool = field(
        default=False,
        metadata={
            "type": "Attribute",
        },
    )

    @dataclass
    class Anteil:
        zaehler: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 1,
            },
        )
        nenner: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 2,
            },
        )


@dataclass
class HausadresseTyp:
    """
    :ivar land:
    :ivar zusatz: z.B. co, Etage...
    :ivar plz:
    :ivar ort:
    :ivar strasse:
    :ivar hausnr:
    """

    class Meta:
        name = "Hausadresse.Typ"

    land: Optional[LandEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zusatz: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    plz: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 10,
            "pattern": r".*[^\s].*",
        },
    )
    ort: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 40,
            "pattern": r".*[^\s].*",
        },
    )
    strasse: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 40,
            "pattern": r".*[^\s].*",
        },
    )
    hausnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 10,
        },
    )


@dataclass
class KvkartendatenTyp:
    """
    :ivar kassenname: Name der Krankenkasse (KRK).
    :ivar kassennr: Nummer der Krankenkasse (KRK-Nr.)
    :ivar versichertennr: Krankenversichertennummer
    :ivar versichertenart:
    :ivar bpersonenkreis:
    :ivar dmpteilnahme:
    :ivar kzvnr: Abrechnungsnummer
    :ivar gueltigbis: Datum des Versicherungsende.
    :ivar einlesedatum:
    """

    class Meta:
        name = "KVKartendaten.Typ"

    kassenname: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 2,
            "max_length": 100,
        },
    )
    kassennr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    versichertennr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 12,
        },
    )
    versichertenart: Optional[VersichertenartEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    bpersonenkreis: Optional[BesondererpersonenkreisEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    dmpteilnahme: Optional[DmpkennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    kzvnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 2,
            "max_length": 28,
        },
    )
    gueltigbis: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    einlesedatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )


@dataclass
class KontaktTyp:
    class Meta:
        name = "Kontakt.Typ"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "min_length": 1,
            "max_length": 40,
        },
    )
    typ: Optional[KontakttypEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    art: Optional[KontaktartEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class LaborZifferTyp(Leistungsposition2Typ):
    """
    Ziffer Beleg Eigenlabor.

    :ivar einzelbetrag: Einzelbetrag für Leistung (ohne Minderungen und
        Umsatzsteuer).
    :ivar gesamtbetrag:
    :ivar mwstsatz: Kennzeichen für den Umsatzsteuersatz der Position
        (ist nicht in den anderen Beträgen enthalten).
    :ivar berechnung: Angabe, ob die Leistung nicht berechnet, nur das
        Honorar oder die Sachkosten berechnet werden.
    :ivar go:
    :ivar goversion:
    :ivar ziffer:
    """

    class Meta:
        name = "LaborZiffer.Typ"

    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    mwstsatz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )
    berechnung: Optional[BerechnungskennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    go: Optional[GebuehrenordnungEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"BEB|BEL",
        },
    )
    goversion: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 10,
        },
    )
    ziffer: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 8,
        },
    )


@dataclass
class MaterialpassTyp:
    """
    :ivar anfangstext:
    :ivar endetext:
    :ivar positionen:
    :ivar id: Eindeutiger Bezeichner f?r Rechnung, wird als Referenz zur
        Rechnung im Arztsystem in den Quittungen angegeben.
    :ivar belegdatum:
    :ivar aisrechnungsnr: Individuelle Arzt Rechnungsnummer.
    :ivar aisaktenzeichen:
    """

    class Meta:
        name = "Materialpass.Typ"

    anfangstext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    endetext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    positionen: Optional["MaterialpassTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "max_length": 40,
        },
    )
    belegdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    aisrechnungsnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 14,
        },
    )
    aisaktenzeichen: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )

    @dataclass
    class Positionen:
        materialpass: List[MaterialpassZifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )


@dataclass
class NachrichtentypTyp:
    """
    :ivar value:
    :ivar version: Angabe der Version des Nachrichtentyps.
    """

    class Meta:
        name = "Nachrichtentyp.Typ"

    value: Optional[NachrichtentypEnum] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    version: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "max_length": 5,
        },
    )


@dataclass
class OpsTyp:
    class Meta:
        name = "OPS.Typ"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "min_length": 1,
            "max_length": 11,
        },
    )
    lokalisation: Optional[LokalisationEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass
class PersonTyp:
    class Meta:
        name = "Person.Typ"

    anrede: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 40,
        },
    )
    titel: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 40,
        },
    )
    vorname: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 40,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 40,
        },
    )
    namezusatz: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 40,
        },
    )
    gebname: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 40,
        },
    )
    gebdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    geschlecht: Optional[GeschlechtEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    staat: Optional[LandEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )


@dataclass
class RatenzahlungTyp:
    """
    :ivar vereinbarung:
    :ivar ersterbetrag: Abweichender erster Ratenbetrag.
    :ivar startdatum: Datum der ersten Rate.
    :ivar betrag: Ratenbetrag pro Monat.
    :ivar anzahl: Anzahl der Monatsraten.
    """

    class Meta:
        name = "Ratenzahlung.Typ"

    vereinbarung: Optional[RatenvereinbarungEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    ersterbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    startdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    betrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    anzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 3,
        },
    )


@dataclass
class ReisekostenTyp:
    """
    Reiseentschädigung nach §8 GOÄ.

    :ivar wegstrecke: Angabe der zurückgelegten Kilometer.
    :ivar uebernachtungskosten: Betrag für notwendige Übernachtungen.
    :ivar abwesenheit: Kennzeichen für Abwesenheit in Stunden.
    """

    class Meta:
        name = "Reisekosten.Typ"

    wegstrecke: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 4,
        },
    )
    uebernachtungskosten: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    abwesenheit: Optional[ReisekostenTypAbwesenheit] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "length": 1,
        },
    )


@dataclass
class SummenblockBelegTyp:
    class Meta:
        name = "SummenblockBeleg.Typ"

    belegsumme: List["SummenblockBelegTyp.Belegsumme"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    belegmwstbetrag: List[BetragSatzTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    belegrechnungsbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )

    @dataclass
    class Belegsumme:
        value: Optional[Decimal] = field(
            default=None,
            metadata={
                "required": True,
                "min_inclusive": Decimal("0.00"),
                "total_digits": 9,
                "fraction_digits": 2,
            },
        )
        text: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "min_length": 1,
                "max_length": 40,
            },
        )


@dataclass
class SummenblockBemaTyp:
    class Meta:
        name = "SummenblockBema.Typ"

    summehonorarbema: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summezahlbetrag: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )


@dataclass
class SummenblockEigenanteilTyp:
    class Meta:
        name = "SummenblockEigenanteil.Typ"

    summehonorarbema: List[BetragBezeichnungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_occurs": 1,
        },
    )
    summehonorargoz: List[BetragBezeichnungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summeeigenlabor: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summefremdlabor: List[BetragBezeichnungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summeverbrauchsmaterial: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summeeigenlabormehrkosten: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summefremdlabormehrkosten: List[BetragBezeichnungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summeverbrauchsmaterialmehrkosten: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summegesamt: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summekassenanteil: Optional[BetragBezeichnungSatzTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summeeigenanteil: Optional[BetragBezeichnungSatzTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summezahlbetrag: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summeabzug: Optional["SummenblockEigenanteilTyp.Summeabzug"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summeauslagen: Optional["SummenblockEigenanteilTyp.Summeauslagen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )

    @dataclass
    class Summeabzug(BetragBezeichnungTyp):
        bezeichnung: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "min_length": 1,
                "max_length": 80,
            },
        )

    @dataclass
    class Summeauslagen(BetragBezeichnungTyp):
        bezeichnung: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "min_length": 1,
                "max_length": 80,
            },
        )


@dataclass
class SummenblockEigenanteilKfoTyp:
    class Meta:
        name = "SummenblockEigenanteilKFO.Typ"

    summehonorarbema: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summeeigenlabor: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summefremdlabor: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summeverbrauchsmaterial: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summeversichertenanteil: Optional[BetragBezeichnungSatzTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summekassenanteil: Optional[BetragBezeichnungSatzTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summemehrkosten: List[BetragBezeichnungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    summezahlbetrag: Optional[BetragBezeichnungTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )


@dataclass
class VersicherungTyp:
    """
    :ivar kassenname: Name der Versicherung.
    :ivar iknr: Institutionskennzeichen der Krankenkasse.
    :ivar kvnr: Krankenversichertennummer der KVK bzw. eGK.
    :ivar versichertenart:
    :ivar bpersonenkreis:
    :ivar dmpteilnahme:
    :ivar gueltigab: Beginn des Versicherungsschutzes.
    :ivar gueltigbis: Datum des Versicherungsende.
    :ivar khkennzeichen: Krankenhaus-internes Kennzeichen des
        Versicherten.
    """

    class Meta:
        name = "Versicherung.Typ"

    kassenname: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 2,
            "max_length": 100,
        },
    )
    iknr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 9,
        },
    )
    kvnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 12,
        },
    )
    versichertenart: Optional[VersichertenartEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    bpersonenkreis: Optional[BesondererpersonenkreisEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    dmpteilnahme: Optional[DmpkennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    gueltigab: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    gueltigbis: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    khkennzeichen: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 15,
        },
    )


@dataclass
class WegegeldTyp:
    """
    Wegegeld nach §8 GOÄ/GOZ.

    :ivar radius: Angabe des Radius in km um die Praxisstelle oder
        Wohnort des Arztes.
    :ivar tageszeit: Angabe, ob Besuch am Tag oder bei Nacht erfolgte.
    """

    class Meta:
        name = "Wegegeld.Typ"

    radius: Optional[WegegeldTypRadius] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 2,
        },
    )
    tageszeit: Optional[WegegeldTypTageszeit] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "length": 1,
        },
    )


@dataclass
class ZifferTyp:
    class Meta:
        name = "Ziffer.Typ"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "min_length": 1,
            "max_length": 8,
        },
    )
    go: Optional[GebuehrenordnungEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    goversion: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 10,
        },
    )
    analog: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass
class AmboTyp:
    """
    :ivar ops:
    :ivar doppeluntersuchung: Kennzeichen, wenn in medizinisch
        begründeten Fällen bereits durchgeführte Untersuchungen nochmals
        veranlasst und in Rechnung gestellt werden.
    :ivar einzelverguetung:
    :ivar zusatzebm: Zusatzkennzeichen EBM, nach Schlüssel 19 (§301 Abs.
        3 SGB V)
    """

    class Meta:
        name = "Ambo.Typ"

    ops: Optional[OpsTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    doppeluntersuchung: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    einzelverguetung: Optional["AmboTyp.Einzelverguetung"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zusatzebm: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "length": 3,
        },
    )

    @dataclass
    class Einzelverguetung:
        """
        :ivar value:
        :ivar kennzeichen: Nach Schlüssel 3 (§301 Abs. 3 SGB V).
        """

        value: Optional[Decimal] = field(
            default=None,
            metadata={
                "required": True,
                "min_inclusive": Decimal("0.00"),
                "total_digits": 9,
                "fraction_digits": 2,
            },
        )
        kennzeichen: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "length": 2,
            },
        )


@dataclass
class AnschriftTyp:
    """
    Komplexer Anschriftstyp.
    """

    class Meta:
        name = "Anschrift.Typ"

    hausadresse: Optional[HausadresseTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    postfach: Optional[PostfachTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    packstation: Optional[PackstationTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    grossempfaenger: Optional["AnschriftTyp.Grossempfaenger"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    auslandsadresse: Optional[AuslandadresseTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )

    @dataclass
    class Grossempfaenger:
        plz: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "required": True,
                "min_length": 1,
                "max_length": 10,
                "pattern": r".*[^\s].*",
            },
        )
        ort: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "required": True,
                "min_length": 1,
                "max_length": 40,
                "pattern": r".*[^\s].*",
            },
        )


@dataclass
class Anschrift3Typ:
    class Meta:
        name = "Anschrift3.Typ"

    hausadresse: Optional[HausadresseTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    postfach: Optional[PostfachTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    auslandsadresse: Optional[AuslandadresseTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )


@dataclass
class AuslagenTyp(AuslagenpositionTyp):
    """
    Auslagen nach §10 GOÄ/GOZ.

    :ivar mwstsatz: Kennzeichen für den Umsatzsteuersatz der Position
        (ist nicht in den anderen Beträgen enthalten).
    :ivar einzelbetrag: Vorgabe des Einzelbetrages für Leistung (ohne
        Umsatzsteuer).
    :ivar gesamtbetrag:
    :ivar kennzeichen: Kennzeichen zur Klassifizierung der Position
        (Medikament, Porto, ...).
    :ivar berechnung: Angabe, ob die Leistung nicht berechnet werden
        soll.
    """

    class Meta:
        name = "Auslagen.Typ"

    mwstsatz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )
    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    kennzeichen: Optional[PositionskennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    berechnung: Optional[AuslagenTypBerechnung] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass
class BehandelterTyp(PersonTyp):
    class Meta:
        name = "Behandelter.Typ"

    gebdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    geschlecht: Optional[GeschlechtEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )


@dataclass
class DiagnoseTyp:
    """
    :ivar text: Angabe der Diagnose als Freitext.
    :ivar code: Angabe der Diagnose als codierter Wert.
    :ivar typ: Angabe Diagnosetyp (Behandlung, Überweisung,...).
    :ivar art: Weitere Klassifizierung der Diagnose, z.B. in Haupt- und
        Nebendiagnosen.
    :ivar datum: Das Diagnosedatum gibt an, wann die Krankheit
        diagnostiziert wurde.
    :ivar sicherheit: Kennzeichen für die Angabe wie sicher die Diagnose
        zu werten ist.
    :ivar lokalisation: Angabe einer Lokalisation für die Diagnose
        (rechts, links, beidseitig).
    """

    class Meta:
        name = "Diagnose.Typ"

    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 4000,
        },
    )
    code: Optional[DiagnosecodeTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    typ: Optional[DiagnosetypEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    art: Optional[DiagnoseartEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    datum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    sicherheit: Optional[DiagnosesicherheitEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    lokalisation: Optional[LokalisationEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )


@dataclass
class EigenlaborTyp:
    """
    :ivar anfangstext:
    :ivar endetext:
    :ivar positionen:
    :ivar summenblock:
    :ivar id: Eindeutiger Bezeichner f?r Rechnung, wird als Referenz zur
        Rechnung im Arztsystem in den Quittungen angegeben.
    :ivar belegdatum:
    :ivar belegnr:
    :ivar ustidnr: Umsatzsteuer ID-Nummer
    """

    class Meta:
        name = "Eigenlabor.Typ"

    anfangstext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    endetext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    positionen: Optional["EigenlaborTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summenblock: Optional[SummenblockBelegTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "max_length": 40,
        },
    )
    belegdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    belegnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 15,
        },
    )
    ustidnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 15,
        },
    )

    @dataclass
    class Positionen:
        eigenlabor: List[LaborZifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        material: List[MaterialZifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )


@dataclass
class EmpfaengerPersonTyp(PersonTyp):
    class Meta:
        name = "EmpfaengerPerson.Typ"

    gebname: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    geschlecht: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    staat: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    anrede: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 40,
            "pattern": r"Ohne Anrede|Frau|Herr|Herr / Frau|Familie|An die Angehörigen von",
        },
    )


@dataclass
class EntschaedigungTyp(AuslagenpositionTyp):
    """
    Entschädigung, entweder Wegegeld oder Reiseentschädigung.

    :ivar wegegeld: Angaben nach §8 GOÄ/GOZ zur Entschädigung für
        Besuche.
    :ivar reisekosten: Angaben nach §9 GOÄ oder §8 GOZ Abs.3 zur
        Erstattung von Reiseaufwendungen.
    :ivar anteil: Anteilige Berechnung der Entschädigung, wenn mehrere
        Patienten besucht werden (z.B. Besuch eines Altenheimes).
    :ivar einzelbetrag:
    :ivar gesamtbetrag:
    :ivar go: Angabe der Gebührenordnung, nach der die Entschädigung
        berechnet werden soll.
    :ivar goversion:
    """

    class Meta:
        name = "Entschaedigung.Typ"

    wegegeld: Optional[WegegeldTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    reisekosten: Optional[ReisekostenTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    anteil: Optional["EntschaedigungTyp.Anteil"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    go: Optional[GebuehrenordnungEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"GOAE|GOZ",
        },
    )
    goversion: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 10,
        },
    )

    @dataclass
    class Anteil:
        teiler: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 2,
            },
        )


@dataclass
class HonorarTyp(AuslagenpositionTyp):
    """
    :ivar mwstsatz: Kennzeichen für den Umsatzsteuersatz der Position
        (ist nicht in den anderen Beträgen enthalten).
    :ivar minderungssatz: Minderungssatz, um den das Honorar ggf.
        gemindert wurde (ist nicht in den anderen Beträgen enthalten).
    :ivar einzelbetrag: Vorgabe des Einzelbetrages für Leistung (ohne
        Umsatzsteuer).
    :ivar gesamtbetrag:
    :ivar berechnung: Angabe, ob die Leistung nicht berechnet werden
        soll.
    """

    class Meta:
        name = "Honorar.Typ"

    mwstsatz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )
    minderungssatz: Optional[MinderungssatzEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    berechnung: Optional[HonorarTypBerechnung] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass
class LepersonTyp(PersonTyp):
    class Meta:
        name = "LEPerson.Typ"

    gebname: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    gebdatum: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    geschlecht: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    staat: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )


@dataclass
class MaterialTyp:
    """
    :ivar anfangstext:
    :ivar endetext:
    :ivar positionen:
    :ivar summenblock:
    :ivar id: Eindeutiger Bezeichner f?r Rechnung, wird als Referenz zur
        Rechnung im Arztsystem in den Quittungen angegeben.
    :ivar belegdatum:
    :ivar belegnr:
    :ivar belegaktenzeichen:
    :ivar ustidnr: Umsatzsteuer ID-Nummer
    """

    class Meta:
        name = "Material.Typ"

    anfangstext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    endetext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    positionen: Optional["MaterialTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summenblock: Optional[SummenblockBelegTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "max_length": 40,
        },
    )
    belegdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    belegnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 15,
        },
    )
    belegaktenzeichen: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 40,
        },
    )
    ustidnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 15,
        },
    )

    @dataclass
    class Positionen:
        material: List[MaterialZifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )


@dataclass
class VersicherterTyp(PersonTyp):
    class Meta:
        name = "Versicherter.Typ"


@dataclass
class Anschrift2Typ(AnschriftTyp):
    class Meta:
        name = "Anschrift2.Typ"

    packstation: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    grossempfaenger: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )


@dataclass
class GozifferTyp(LeistungspositionTyp):
    """
    Leistungsposition nach jeweiliger Gebührenordnung.

    :ivar faktor: Faktor für erbrachte Leistung nach der jeweiligen
        Gebührenordnung.
    :ivar einzelbetrag: Einzelbetrag für Leistung (ohne Minderungen und
        Umsatzsteuer).
    :ivar beteiligung:
    :ivar anteil: Wird eine Leistung nur zum Teil in Rechnung gestellt,
        wird hier der Anteil angegeben (z.B. Abrechnung eines halben
        Zuschlags nach Ziffer D GOÄ, wenn die Leistung innerhalb der
        Sprechstunde an Samstagen erbracht wurde).
    :ivar begruendung: Begründungstext für erbrachte Leistung (z.B. bei
        Verwendung von höheren Faktoren als der Regelhöchstsatz).
    :ivar mwstsatz: Kennzeichen für den Umsatzsteuersatz der Position
        (ist nicht in den anderen Beträgen enthalten).
    :ivar minderungssatz: Minderungssatz, um den das Honorar ggf. zu
        mindern ist (ist nicht in den anderen Beträgen enthalten).
    :ivar ambo:
    :ivar punktwert:
    :ivar punktzahl:
    :ivar gesamtbetrag:
    :ivar berechnung: Angabe, ob die Leistung nicht berechnet, nur das
        Honorar oder die Sachkosten berechnet werden.
    :ivar go:
    :ivar goversion:
    :ivar analog:
    :ivar ziffer:
    """

    class Meta:
        name = "GOZiffer.Typ"

    faktor: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 8,
            "fraction_digits": 6,
        },
    )
    einzelbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    beteiligung: List[BeteiligungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    anteil: Optional["GozifferTyp.Anteil"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    begruendung: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    mwstsatz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )
    minderungssatz: Optional[MinderungssatzEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    ambo: Optional[AmboTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    punktwert: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 9,
            "fraction_digits": 7,
        },
    )
    punktzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 5,
        },
    )
    gesamtbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )
    berechnung: Optional[BerechnungskennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    go: Optional[GebuehrenordnungEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"GOAE|UVGOAE|EBM",
        },
    )
    goversion: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 10,
        },
    )
    analog: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 8,
        },
    )
    ziffer: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_length": 1,
            "max_length": 8,
        },
    )

    @dataclass
    class Anteil:
        zaehler: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 1,
            },
        )
        nenner: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 2,
            },
        )


@dataclass
class OrganisationTyp:
    """
    :ivar name:
    :ivar namezusatz: Abteilungsleitung Nicola Meyer
    :ivar anschrift:
    :ivar kontakt:
    :ivar iknr:
    """

    class Meta:
        name = "Organisation.Typ"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 120,
            "pattern": r".*[^\s].*",
        },
    )
    namezusatz: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    anschrift: Optional[AnschriftTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    kontakt: List[KontaktTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    iknr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 9,
        },
    )


@dataclass
class UeberweiserTyp(LepersonTyp):
    class Meta:
        name = "Ueberweiser.Typ"

    gebname: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    gebdatum: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    geschlecht: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    staat: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    anrede: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    titel: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )
    namezusatz: Any = field(
        init=False,
        metadata={
            "type": "Ignore",
        },
    )


@dataclass
class BemaTyp:
    """
    :ivar leistungserbringerid: Angabe des Leistungserbringers für diese
        Behandlung. Gültig für alle Posiionen innerhalb der Rechnung.
        Abweichungen sind in den entspr. Positionen anzugeben.
    :ivar ueberweiser: Angabe eines Überweisers, der u.U. für die
        Abrechnung relevant ist.
    :ivar behandelter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Patienten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar versicherter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Versicherten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar zeitraum: Angabe des Zeitraumes. Bei stationärer Behandlung,
        Angabe des Aufnahme- und Entlassungsdatums.
    :ivar behandlungsart: Angabe, ob es sich um eine ambulante,
        stationäre oder eine weitere Behandlung handelt.
    :ivar kvkartendaten:
    :ivar positionen:
    :ivar summenblock:
    """

    class Meta:
        name = "Bema.Typ"

    leistungserbringerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    ueberweiser: Optional["BemaTyp.Ueberweiser"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandelter: Optional["BemaTyp.Behandelter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    versicherter: Optional["BemaTyp.Versicherter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zeitraum: Optional[ZeitraumTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandlungsart: Optional[BehandlungsartEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    kvkartendaten: Optional[KvkartendatenTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    positionen: Optional["BemaTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summenblock: Optional[SummenblockBemaTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )

    @dataclass
    class Ueberweiser(UeberweiserTyp):
        """
        :ivar lanr: Angabe der Arztnummer.
        """

        lanr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "total_digits": 9,
            },
        )

    @dataclass
    class Behandelter(BehandelterTyp):
        """
        :ivar verwandtschaft: Verwandtschaftsverhältnis zum
            Versicherten.
        :ivar kontakt:
        :ivar aisid: Patientenidentifikation im Arztsystem.
        :ivar idbundesweit: Patientenidentifikation, die bundesweit
            gültig ist.
        """

        verwandtschaft: Optional[VerwandtschaftskennungEnum] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        aisid: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )
        idbundesweit: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )

    @dataclass
    class Versicherter(VersicherterTyp):
        versicherung: Optional[VersicherungTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        anschrift: Optional[Anschrift2Typ] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )

    @dataclass
    class Positionen:
        bema: List[BemaZifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )


@dataclass
class FremdlaborTyp:
    """
    :ivar anschrift:
    :ivar anfangstext:
    :ivar endetext:
    :ivar positionen:
    :ivar summenblock:
    :ivar id: Eindeutiger Bezeichner f?r Rechnung, wird als Referenz zur
        Rechnung im Arztsystem in den Quittungen angegeben.
    :ivar belegdatum:
    :ivar aisrechnungsnr: Individuelle Arzt Rechnungsnummer.
    :ivar aisauftragsnr:
    :ivar aisendbetrag: Rechnungsbetrag, der vom AIS ermittelt wurde.
    """

    class Meta:
        name = "Fremdlabor.Typ"

    anschrift: Optional[Anschrift2Typ] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    anfangstext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    endetext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    positionen: Optional["FremdlaborTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summenblock: Optional[SummenblockBelegTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "max_length": 40,
        },
    )
    belegdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    aisrechnungsnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 14,
        },
    )
    aisauftragsnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )
    aisendbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )

    @dataclass
    class Positionen:
        fremdlabor: List[LaborZifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        material: List[MaterialZifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )


@dataclass
class LeistungserbringerTyp(LepersonTyp):
    """
    :ivar anschrift:
    :ivar kundennr:
    :ivar fachbereich:
    :ivar lanr: Pro Fachgruppe besitzt der Arzt eine lebenslange
        Arztnummer (LANR).
    :ivar betriebsstaette: Über diese Nummer wird der Ort der
        Leistungserbingung angegeben.
    :ivar kzvnr: KZV-Nummer Zahnarzt
    :ivar ustidnr: Umsatzsteueridentifikationsnummer des LE.
    :ivar hba: Heilberufsausweisnummer
    :ivar iknr:
    :ivar id: Eindeutiger Bezeichner für LE, wird als Referenz in den
        Rechnungen angegeben.
    :ivar aisid: Eindeutige Referenz für den Leistungserbringer im
        Arztinformationssystem.
    """

    class Meta:
        name = "Leistungserbringer.Typ"

    anschrift: Optional[Anschrift2Typ] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    kundennr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 20,
        },
    )
    fachbereich: List[FachbereichTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    lanr: List[int] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 9,
        },
    )
    betriebsstaette: Optional[BehandlungsortTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    kzvnr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 10,
        },
    )
    ustidnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 15,
        },
    )
    hba: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    iknr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 9,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "max_length": 40,
        },
    )
    aisid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )


@dataclass
class RechnungsempfaengerTyp:
    """
    Kann eine Person oder eine Organisation sein.
    """

    class Meta:
        name = "Rechnungsempfaenger.Typ"

    person: Optional["RechnungsempfaengerTyp.Person"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    organisation: Optional[OrganisationTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )

    @dataclass
    class Person(EmpfaengerPersonTyp):
        anschrift: Optional[AnschriftTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "required": True,
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )


@dataclass
class RechnungserstellerTyp:
    """
    :ivar name:
    :ivar namezusatz:
    :ivar kundennr:
    :ivar anschrift:
    :ivar iknr:
    :ivar kontakt:
    :ivar ustidnr: Umsatzsteueridentifikationsnummer des
        Rechnungserstellers.
    :ivar glaeubigerid:
    """

    class Meta:
        name = "Rechnungsersteller.Typ"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 40,
        },
    )
    namezusatz: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    kundennr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 20,
        },
    )
    anschrift: Optional[Anschrift2Typ] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    iknr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "total_digits": 9,
        },
    )
    kontakt: List[KontaktTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    ustidnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 15,
        },
    )
    glaeubigerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 40,
        },
    )


@dataclass
class UnfallarbeitgeberTyp:
    """
    :ivar name:
    :ivar anschrift:
    :ivar berufsgruppe: Berufsgruppe des Versicherten
    :ivar einstellungsdatum: Angabe, seit wann der Versicherte beim
        Arbeitgeber angestellt ist.
    """

    class Meta:
        name = "Unfallarbeitgeber.Typ"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "min_length": 1,
            "max_length": 80,
        },
    )
    anschrift: Optional[Anschrift2Typ] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    berufsgruppe: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 30,
        },
    )
    einstellungsdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )


@dataclass
class BmgNormKfoprivatTyp:
    """
    :ivar leistungserbringerid: Angabe des Leistungserbringers für diese
        Behandlung. Gültig für alle Posiionen innerhalb der Rechnung.
        Abweichungen sind in den entspr. Positionen anzugeben.
    :ivar ueberweiser: Angabe eines Überweisers, der u.U. für die
        Abrechnung relevant ist.
    :ivar behandelter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Patienten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar versicherter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Versicherten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar zeitraum: Angabe des Zeitraumes. Bei stationärer Behandlung,
        Angabe des Aufnahme- und Entlassungsdatums.
    :ivar diagnose: Diagnosen können sowohl kodiert als auch als Text
        angegeben werden.
    :ivar kfoplandaten:
    :ivar positionen:
    :ivar summenblock:
    :ivar begruendung:
    :ivar anhangid: Verweis auf Dateianhang innerhalb der Datenlieferung
        (Referenz zur Angabe in Auftragsdatei).
    :ivar beleg:
    """

    class Meta:
        name = "BmgNormKFOPrivat.Typ"

    leistungserbringerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    ueberweiser: Optional["BmgNormKfoprivatTyp.Ueberweiser"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandelter: Optional["BmgNormKfoprivatTyp.Behandelter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    versicherter: Optional["BmgNormKfoprivatTyp.Versicherter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zeitraum: Optional[ZeitraumTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    diagnose: List[DiagnoseTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    kfoplandaten: Optional[KfoplandatenTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    positionen: Optional["BmgNormKfoprivatTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summenblock: Optional[SummenblockBmgTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    begruendung: List[BegruendungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    anhangid: List[AnhangidTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    beleg: List["BmgNormKfoprivatTyp.Beleg"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )

    @dataclass
    class Ueberweiser(UeberweiserTyp):
        """
        :ivar lanr: Angabe der Arztnummer.
        """

        lanr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "total_digits": 9,
            },
        )

    @dataclass
    class Behandelter(BehandelterTyp):
        """
        :ivar verwandtschaft: Verwandtschaftsverhältnis zum
            Versicherten.
        :ivar kontakt:
        :ivar aisid: Patientenidentifikation im Arztsystem.
        :ivar idbundesweit: Patientenidentifikation, die bundesweit
            gültig ist.
        """

        verwandtschaft: Optional[VerwandtschaftskennungEnum] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        aisid: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )
        idbundesweit: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )

    @dataclass
    class Versicherter(VersicherterTyp):
        versicherung: Optional[VersicherungTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        anschrift: Optional[AnschriftTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )

    @dataclass
    class Positionen:
        goziffer: List[GozifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        entschaedigung: List[EntschaedigungTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        auslagen: List[AuslagenTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        sonstigeshonorar: List[HonorarTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        gozziffer: List[GozzifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )

    @dataclass
    class Beleg:
        eigenlabor: Optional[EigenlaborTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        fremdlabor: Optional[FremdlaborTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        material: Optional[MaterialTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        materialpass: Optional[MaterialpassTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )


@dataclass
class BmgNormPrivatTyp:
    """
    :ivar leistungserbringerid: Angabe des Leistungserbringers für diese
        Behandlung. Gültig für alle Posiionen innerhalb der Rechnung.
        Abweichungen sind in den entspr. Positionen anzugeben.
    :ivar ueberweiser: Angabe eines Überweisers, der u.U. für die
        Abrechnung relevant ist.
    :ivar behandelter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Patienten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar versicherter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Versicherten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar zeitraum: Angabe des Zeitraumes. Bei stationärer Behandlung,
        Angabe des Aufnahme- und Entlassungsdatums.
    :ivar minderungssatz: Minderungssatz, um den dieser Abrechnungsfall
        gemindert wird.
    :ivar behandlungsart: Angabe, ob es sich um eine ambulante,
        stationäre oder eine weitere Behandlung handelt.
    :ivar diagnose: Diagnosen können sowohl kodiert als auch als Text
        angegeben werden.
    :ivar positionen:
    :ivar summenblock:
    :ivar begruendung:
    :ivar anhangid: Verweis auf Dateianhang innerhalb der Datenlieferung
        (Referenz zur Angabe in Auftragsdatei).
    :ivar beleg:
    """

    class Meta:
        name = "BmgNormPrivat.Typ"

    leistungserbringerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    ueberweiser: Optional["BmgNormPrivatTyp.Ueberweiser"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandelter: Optional["BmgNormPrivatTyp.Behandelter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    versicherter: Optional["BmgNormPrivatTyp.Versicherter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zeitraum: Optional[ZeitraumTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    minderungssatz: Optional[MinderungssatzEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandlungsart: Optional[BehandlungsartEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    diagnose: List[DiagnoseTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    positionen: Optional["BmgNormPrivatTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summenblock: Optional[SummenblockBmgTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    begruendung: List[BegruendungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    anhangid: List[AnhangidTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    beleg: List["BmgNormPrivatTyp.Beleg"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )

    @dataclass
    class Ueberweiser(UeberweiserTyp):
        """
        :ivar lanr: Angabe der Arztnummer.
        """

        lanr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "total_digits": 9,
            },
        )

    @dataclass
    class Behandelter(BehandelterTyp):
        """
        :ivar verwandtschaft: Verwandtschaftsverhältnis zum
            Versicherten.
        :ivar kontakt:
        :ivar aisid: Patientenidentifikation im Arztsystem.
        :ivar idbundesweit: Patientenidentifikation, die bundesweit
            gültig ist.
        """

        verwandtschaft: Optional[VerwandtschaftskennungEnum] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        aisid: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )
        idbundesweit: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )

    @dataclass
    class Versicherter(VersicherterTyp):
        versicherung: Optional[VersicherungTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        anschrift: Optional[Anschrift2Typ] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )

    @dataclass
    class Positionen:
        goziffer: List[GozifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        entschaedigung: List[EntschaedigungTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        auslagen: List[AuslagenTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        sonstigeshonorar: List["BmgNormPrivatTyp.Positionen.Sonstigeshonorar"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        gozziffer: List[GozzifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )

        @dataclass
        class Sonstigeshonorar(HonorarTyp):
            leistungskuerzel: Optional[object] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://padinfo.de/ns/pad",
                },
            )

    @dataclass
    class Beleg:
        eigenlabor: Optional[EigenlaborTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        fremdlabor: Optional[FremdlaborTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        material: Optional[MaterialTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        materialpass: Optional[MaterialpassTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )


@dataclass
class EigenanteilsrechnungTyp:
    """
    :ivar leistungserbringerid: Angabe des Leistungserbringers für diese
        Behandlung. Gültig für alle Posiionen innerhalb der Rechnung.
        Abweichungen sind in den entspr. Positionen anzugeben.
    :ivar ueberweiser: Angabe eines Überweisers, der u.U. für die
        Abrechnung relevant ist.
    :ivar behandelter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Patienten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar versicherter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Versicherten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar zeitraum: Angabe des Zeitraumes. Bei stationärer Behandlung,
        Angabe des Aufnahme- und Entlassungsdatums.
    :ivar diagnose: Diagnosen können sowohl kodiert als auch als Text
        angegeben werden.
    :ivar positionen:
    :ivar summenblock:
    :ivar begruendung:
    :ivar anhangid: Verweis auf Dateianhang innerhalb der Datenlieferung
        (Referenz zur Angabe in Auftragsdatei).
    :ivar beleg:
    """

    class Meta:
        name = "Eigenanteilsrechnung.Typ"

    leistungserbringerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    ueberweiser: Optional["EigenanteilsrechnungTyp.Ueberweiser"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandelter: Optional["EigenanteilsrechnungTyp.Behandelter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    versicherter: Optional["EigenanteilsrechnungTyp.Versicherter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zeitraum: Optional[ZeitraumTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    diagnose: List[DiagnoseTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    positionen: Optional["EigenanteilsrechnungTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summenblock: Optional[SummenblockEigenanteilTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    begruendung: List[BegruendungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    anhangid: List[AnhangidTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    beleg: List["EigenanteilsrechnungTyp.Beleg"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )

    @dataclass
    class Ueberweiser(UeberweiserTyp):
        """
        :ivar lanr: Angabe der Arztnummer.
        """

        lanr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "total_digits": 9,
            },
        )

    @dataclass
    class Behandelter(BehandelterTyp):
        """
        :ivar verwandtschaft: Verwandtschaftsverhältnis zum
            Versicherten.
        :ivar kontakt:
        :ivar aisid: Patientenidentifikation im Arztsystem.
        :ivar idbundesweit: Patientenidentifikation, die bundesweit
            gültig ist.
        """

        verwandtschaft: Optional[VerwandtschaftskennungEnum] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        aisid: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )
        idbundesweit: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )

    @dataclass
    class Versicherter(VersicherterTyp):
        versicherung: Optional[VersicherungTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        anschrift: Optional[AnschriftTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )

    @dataclass
    class Positionen:
        goziffer: List[GozifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        entschaedigung: List[EntschaedigungTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        auslagen: List[AuslagenTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        sonstigeshonorar: List[HonorarTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        bema: List[BemaZifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        gozziffer: List[GozzifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )

    @dataclass
    class Beleg:
        eigenlabor: Optional[EigenlaborTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        fremdlabor: Optional[FremdlaborTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        material: Optional[MaterialTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        materialpass: Optional[MaterialpassTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )


@dataclass
class EigenanteilsrechnungKfoTyp:
    """
    :ivar leistungserbringerid: Angabe des Leistungserbringers für diese
        Behandlung. Gültig für alle Posiionen innerhalb der Rechnung.
        Abweichungen sind in den entspr. Positionen anzugeben.
    :ivar ueberweiser: Angabe eines Überweisers, der u.U. für die
        Abrechnung relevant ist.
    :ivar behandelter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Patienten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar versicherter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Versicherten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar zeitraum: Angabe des Zeitraumes. Bei stationärer Behandlung,
        Angabe des Aufnahme- und Entlassungsdatums.
    :ivar diagnose: Diagnosen können sowohl kodiert als auch als Text
        angegeben werden.
    :ivar kfokopfdaten:
    :ivar kfoplandaten:
    :ivar positionen:
    :ivar summenblock:
    :ivar anhangid: Verweis auf Dateianhang innerhalb der Datenlieferung
        (Referenz zur Angabe in Auftragsdatei).
    :ivar beleg:
    """

    class Meta:
        name = "EigenanteilsrechnungKFO.Typ"

    leistungserbringerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    ueberweiser: Optional["EigenanteilsrechnungKfoTyp.Ueberweiser"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandelter: Optional["EigenanteilsrechnungKfoTyp.Behandelter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    versicherter: Optional["EigenanteilsrechnungKfoTyp.Versicherter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zeitraum: Optional[ZeitraumTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    diagnose: List[DiagnoseTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    kfokopfdaten: Optional[KvkartendatenTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    kfoplandaten: Optional[KfoplandatenTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    positionen: Optional["EigenanteilsrechnungKfoTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    summenblock: Optional[SummenblockEigenanteilKfoTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    anhangid: List[AnhangidTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    beleg: List["EigenanteilsrechnungKfoTyp.Beleg"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )

    @dataclass
    class Ueberweiser(UeberweiserTyp):
        """
        :ivar lanr: Angabe der Arztnummer.
        """

        lanr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "total_digits": 9,
            },
        )

    @dataclass
    class Behandelter(BehandelterTyp):
        """
        :ivar verwandtschaft: Verwandtschaftsverhältnis zum
            Versicherten.
        :ivar kontakt:
        :ivar aisid: Patientenidentifikation im Arztsystem.
        :ivar idbundesweit: Patientenidentifikation, die bundesweit
            gültig ist.
        """

        verwandtschaft: Optional[VerwandtschaftskennungEnum] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        aisid: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )
        idbundesweit: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )

    @dataclass
    class Versicherter(VersicherterTyp):
        versicherung: Optional[VersicherungTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        anschrift: Optional[AnschriftTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )

    @dataclass
    class Positionen:
        bema: List[BemaZifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        bemakfo: List[BemaKfozifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        eigenlaborkfo: List[EigenlaborKfozifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        bemakfozwsumme: List[BemaKfozwSummeTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )

    @dataclass
    class Beleg:
        eigenlabor: Optional[EigenlaborTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        fremdlabor: Optional[FremdlaborTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        material: Optional[MaterialTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        materialpass: Optional[MaterialpassTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )


@dataclass
class UnfalldatenTyp:
    """
    :ivar unfalltag:
    :ivar aktenzeichen:
    :ivar unfallhergang:
    :ivar personalunfall: Ist der Versicherte bei einem
        Unfallversicherungsträger beschäftigt: true
    :ivar arbeitgeber:
    :ivar refarztbericht: Verweis auf einen Arztbericht. Z.B. die
        Refernznummer eines D-Arztbericht im Dale-UV Vaerfahren.
    """

    class Meta:
        name = "Unfalldaten.Typ"

    unfalltag: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    aktenzeichen: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 65,
        },
    )
    unfallhergang: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 80,
        },
    )
    personalunfall: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    arbeitgeber: Optional[UnfallarbeitgeberTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    refarztbericht: Optional["UnfalldatenTyp.Refarztbericht"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )

    @dataclass
    class Refarztbericht:
        """
        :ivar value:
        :ivar typ: Bezeichner für Arztbericht (Bsp.: DABE, HABE, NASB,
            ZWIB, HAVB, KOEB, KNEB, STEB, VEEB)
        """

        value: str = field(
            default="",
            metadata={
                "required": True,
                "min_length": 1,
                "max_length": 15,
            },
        )
        typ: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )


@dataclass
class HumanmedizinTyp:
    """
    :ivar leistungserbringerid: Angabe des Leistungserbringers für diese
        Behandlung. Gültig für alle Posiionen innerhalb der Rechnung.
        Abweichungen sind in den entspr. Positionen anzugeben.
    :ivar ueberweiser: Angabe eines Überweisers, der u.U. für die
        Abrechnung relevant ist.
    :ivar behandelter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Patienten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar versicherter: Falls alle Leistungen in der gesamten Rechnung
        nur einen Versicherten betreffen, so braucht dieser nur bei dem
        ersten Behandlungsfall angegeben zu werden.
    :ivar zeitraum: Angabe des Zeitraumes. Bei stationärer Behandlung,
        Angabe des Aufnahme- und Entlassungsdatums.
    :ivar mwstsatz: Angabe des Umsatzsteuersatzes des Abrechnungsfalls
        (wird von Angaben auf Positionsebene überschrieben).
    :ivar minderungssatz: Minderungssatz, um den dieser Abrechnungsfall
        gemindert wird.
    :ivar behandlungsart: Angabe, ob es sich um eine ambulante,
        stationäre oder eine weitere Behandlung handelt.
    :ivar vertragsart: Vertragsart für Abrechnungsfall.
    :ivar beschreibung: Beschreibungszeile zur Behandlung.
    :ivar beteiligung:
    :ivar aktenzeichen: Aktenzeichen oder Fallnummer.
    :ivar unfalldaten: Unfallinformationen bei Rechnungen an die
        Berufsgenossenschaft.
    :ivar diagnose: Diagnosen können sowohl kodiert als auch als Text
        angegeben werden.
    :ivar klasse:
    :ivar positionen:
    :ivar anhangid: Verweis auf Dateianhang innerhalb der Datenlieferung
        (Referenz zur Angabe in Auftragsdatei).
    :ivar rechnungssondertyp:
    """

    class Meta:
        name = "Humanmedizin.Typ"

    leistungserbringerid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    ueberweiser: Optional["HumanmedizinTyp.Ueberweiser"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandelter: Optional["HumanmedizinTyp.Behandelter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    versicherter: Optional["HumanmedizinTyp.Versicherter"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    zeitraum: Optional[ZeitraumTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    mwstsatz: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_inclusive": Decimal("0.00"),
            "max_inclusive": Decimal("100.00"),
            "fraction_digits": 2,
        },
    )
    minderungssatz: Optional[MinderungssatzEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    behandlungsart: Optional[BehandlungsartEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    vertragsart: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "total_digits": 3,
        },
    )
    beschreibung: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 60,
        },
    )
    beteiligung: List[BeteiligungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    aktenzeichen: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "max_length": 40,
        },
    )
    unfalldaten: Optional[UnfalldatenTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    diagnose: List[DiagnoseTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    klasse: Optional[UnterkunftstationaerEnum] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    positionen: Optional["HumanmedizinTyp.Positionen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    anhangid: List[AnhangidTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    rechnungssondertyp: Optional[RechnungssondertypEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

    @dataclass
    class Ueberweiser(UeberweiserTyp):
        """
        :ivar lanr: Angabe der Arztnummer.
        """

        lanr: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "total_digits": 9,
            },
        )

    @dataclass
    class Behandelter(BehandelterTyp):
        """
        :ivar verwandtschaft: Verwandtschaftsverhältnis zum
            Versicherten.
        :ivar kontakt:
        :ivar aisid: Patientenidentifikation im Arztsystem.
        :ivar idbundesweit: Patientenidentifikation, die bundesweit
            gültig ist.
        """

        verwandtschaft: Optional[VerwandtschaftskennungEnum] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        aisid: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )
        idbundesweit: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 40,
            },
        )

    @dataclass
    class Versicherter(VersicherterTyp):
        versicherung: Optional[VersicherungTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        anschrift: Optional[AnschriftTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontakt: List[KontaktTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )

    @dataclass
    class Positionen:
        goziffer: List[GozifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        entschaedigung: List[EntschaedigungTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        auslagen: List[AuslagenTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        sonstigeshonorar: List[HonorarTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        gozziffer: List[GozzifferTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        text: List[TextzeileTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        posanzahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 4,
            },
        )


@dataclass
class RechnungTyp:
    """
    :ivar rechnungsempfaenger:
    :ivar zahlung: Zusätzliche Zahlungsvereinbarungen.
    :ivar rechnungsvorgaben: Angabe aller Beträge auf Rechnungsebene.
    :ivar abrechnungsfall:
    :ivar abrechnungsanweisung:
    :ivar anfangstext:
    :ivar endetext:
    :ivar id: Eindeutiger Bezeichner für Rechnung, wird als Referenz zur
        Rechnung im Arztsystem in den Quittungen angegeben.
    :ivar abrechnungsform: Individuelles Kennzeichen für die PVS zur
        Abrechnung der Arztdaten.
    :ivar druckkennzeichen: Kennzeichen, dass Rechnung  bei der PVS
        gedruckt wird (Standardfall) oder beim Arzt .
    :ivar eabgabe: Kennzeichen, ob die Rechnung elektronisch versendet
        werden soll.
    :ivar mahnkennzeichen: gmv steht für gerichtliches Mahnverfahren.
    :ivar aisrechnungsnr: Individuelle Arzt Rechnungsnummer.
    :ivar aisaktenzeichen:
    :ivar aisendbetrag: Rechnungsbetrag, der vom AIS ermittelt wurde.
    """

    class Meta:
        name = "Rechnung.Typ"

    rechnungsempfaenger: Optional[RechnungsempfaengerTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    zahlung: Optional["RechnungTyp.Zahlung"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    rechnungsvorgaben: Optional["RechnungTyp.Rechnungsvorgaben"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
        },
    )
    abrechnungsfall: List["RechnungTyp.Abrechnungsfall"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_occurs": 1,
        },
    )
    abrechnungsanweisung: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    anfangstext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    endetext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "max_length": 40,
        },
    )
    abrechnungsform: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "total_digits": 8,
        },
    )
    druckkennzeichen: bool = field(
        default=True,
        metadata={
            "type": "Attribute",
        },
    )
    eabgabe: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    mahnkennzeichen: Optional[MahnkennzeichenEnum] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    aisrechnungsnr: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 14,
        },
    )
    aisaktenzeichen: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "max_length": 40,
        },
    )
    aisendbetrag: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0.00"),
            "total_digits": 9,
            "fraction_digits": 2,
        },
    )

    @dataclass
    class Zahlung:
        """
        :ivar ratenzahlung:
        :ivar kontoverbindung: Kontoverbindung um Betrag direkt
            abzubuchen (Lastschrift, Ratenzahlung).
        :ivar art:
        """

        ratenzahlung: Optional[RatenzahlungTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        kontoverbindung: Optional[KontoTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        art: Optional[ZahlungsartEnum] = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass
    class Rechnungsvorgaben:
        """
        :ivar direktzahlungsbetrag: Betrag, der bereits gezahlt wurde
            (Gesamt- oder Teilbetrag).
        :ivar nachlass:
        :ivar zuzahlungsbetrag:
        :ivar beteiligung:
        """

        direktzahlungsbetrag: Optional[Decimal] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
                "min_inclusive": Decimal("0.00"),
                "total_digits": 9,
                "fraction_digits": 2,
            },
        )
        nachlass: Optional[NachlassTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        zuzahlungsbetrag: Optional[
            "RechnungTyp.Rechnungsvorgaben.Zuzahlungsbetrag"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        beteiligung: List[BeteiligungTyp] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )

        @dataclass
        class Zuzahlungsbetrag:
            """
            :ivar value:
            :ivar kennzeichen: Nach Schlüssel 15 (§301 Abs. 3 SGB V)
            """

            value: Optional[Decimal] = field(
                default=None,
                metadata={
                    "required": True,
                    "min_inclusive": Decimal("0.00"),
                    "total_digits": 9,
                    "fraction_digits": 2,
                },
            )
            kennzeichen: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                    "length": 1,
                },
            )

    @dataclass
    class Abrechnungsfall:
        bema: Optional[BemaTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        bmgnormprivat: Optional[BmgNormPrivatTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        bmgnormkfoprivat: Optional[BmgNormKfoprivatTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        eigenanteilsrechnung: Optional[EigenanteilsrechnungTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        eigenanteilsrechnungkfo: Optional[EigenanteilsrechnungKfoTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )
        humanmedizin: Optional[HumanmedizinTyp] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://padinfo.de/ns/pad",
            },
        )


@dataclass
class RechnungListe:
    """
    :ivar hinweistext: Hinweistext für gesamte Datenlieferung.
    :ivar nachrichtentyp:
    :ivar rechnungsersteller: Angabe des Rechnungserstellers mit
        angegebener Kundenkennung der PVS, gültig für alle Rechnungen
        der Datenlieferung.
    :ivar leistungserbringer: Liste aller Leistungserbringer, auf die in
        den Rechnungsdaten referenziert wird.
    :ivar rechnung: Wurzelelement pro Arztrechnung.
    :ivar anzahl:
    """

    class Meta:
        name = "Rechnung.Liste"

    hinweistext: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    nachrichtentyp: str = field(
        init=False,
        default="ADL",
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    rechnungsersteller: Optional[RechnungserstellerTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    leistungserbringer: List[LeistungserbringerTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_occurs": 1,
        },
    )
    rechnung: List[RechnungTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "min_occurs": 1,
        },
    )
    anzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
