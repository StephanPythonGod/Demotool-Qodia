from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from xsdata.models.datatype import XmlDateTime

from schemas.padnext_v2_py.padx_basis_v2_12 import (
    DateilaengeTyp,
    DokumenttypTyp,
    NachrichtentypTyp,
    TeilnehmerTyp,
)

__NAMESPACE__ = "http://padinfo.de/ns/pad"


class VerschluesselungVerfahren(Enum):
    """
    :cvar VALUE_0: Keine Verschlüsselung.
    :cvar VALUE_1: PKCS#7 Verfahren.
    """

    VALUE_0 = Decimal("0")
    VALUE_1 = Decimal("1")


@dataclass
class DateiTyp:
    """
    :ivar dokumententyp:
    :ivar name: Dateiname, ohne Pfadangaben.
    :ivar beschreibung:
    :ivar dateilaenge: Dateigröße unverschlüsselt und unkomprimiert.
    :ivar id: Eindeutige Identifikation für Datei innerhalb einer
        Datenlieferung.
    :ivar erstellungsdatum: Erstellungsdatum mit Uhrzeit der Datei.
    """

    class Meta:
        name = "Datei.Typ"

    dokumententyp: Optional[DokumenttypTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://padinfo.de/ns/pad",
            "required": True,
            "max_length": 40,
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
    dateilaenge: Optional[DateilaengeTyp] = field(
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
    erstellungsdatum: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Auftrag:
    """
    :ivar empfaenger: Empfänger der Datenlieferung.
    :ivar absender: Absender der Datenlieferung.
    :ivar nachrichtentyp:
    :ivar system: Angaben über das System, dass die Daten erstellt hat.
    :ivar verschluesselung:
    :ivar empfangsquittung: Ist eine Empfangsbestätigung für diese
        Datenlieferung erwünscht? Mit email Adresse.
    :ivar datei: Informationen über alle Nutzdateien der Datenlieferung.
    :ivar erstellungsdatum: Erstellungsdatum mit Uhrzeit des Auftrages.
    :ivar transfernr: Pro Empfänger wird eine laufende Nummer
        hochgezählt
    :ivar echtdaten: Kennug, ob es sich um Echt- oder Testdaten handelt.
    :ivar dateianzahl: Anzahl der Dateien pro Datenlieferung (ohne
        Auftragsdatei).
    """

    class Meta:
        name = "auftrag"
        namespace = "http://padinfo.de/ns/pad"

    empfaenger: Optional[TeilnehmerTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    absender: Optional[TeilnehmerTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    nachrichtentyp: Optional[NachrichtentypTyp] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    system: Optional["Auftrag.System"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    verschluesselung: Optional["Auftrag.Verschluesselung"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    empfangsquittung: Optional["Auftrag.Empfangsquittung"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    datei: List[DateiTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
            "max_occurs": 9999,
        },
    )
    erstellungsdatum: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    transfernr: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "total_digits": 6,
        },
    )
    echtdaten: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    dateianzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "total_digits": 4,
        },
    )

    @dataclass
    class System:
        """
        :ivar produkt:
        :ivar version:
        :ivar hersteller:
        :ivar zertifizierungsnr: Diese Nummer wird beim
            Zertifizierungsprozess für das jeweilige System vergeben.
        """

        produkt: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
                "max_length": 40,
            },
        )
        version: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
                "max_length": 20,
            },
        )
        hersteller: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
                "max_length": 40,
            },
        )
        zertifizierungsnr: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "max_length": 20,
            },
        )

    @dataclass
    class Verschluesselung:
        """
        :ivar verfahren: PKCS7, keine.
        :ivar idcert: Kennung für Empfänger Zertifikat (enthält
            öffentlichen Schlüssel).
        """

        verfahren: Optional[VerschluesselungVerfahren] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "total_digits": 1,
            },
        )
        idcert: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "max_length": 128,
            },
        )

    @dataclass
    class Empfangsquittung:
        value: Optional[bool] = field(
            default=None,
            metadata={
                "required": True,
            },
        )
        email: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "max_length": 100,
            },
        )
