from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDateTime

from schemas.padnext_v2_py.padx_basis_v2_12 import FehlerTyp

__NAMESPACE__ = "http://padinfo.de/ns/pad"


@dataclass
class Quittung:
    """
    Quittungsinformationen für eine Datenlieferung.

    :ivar nachrichtentyp:
    :ivar eingangsdatum: Eingangsdatum mit Uhrzeit der Datenlieferung
        bei der PVS.
    :ivar status: Verarbeitungsstatus der gesamten Datenlieferung.
    :ivar fehler: Fehlerangabe für die gesamte Datenlieferung.
    :ivar datenlieferung: Enthält die Transfernummer der zu
        quittierenden Datenlieferung und gibt den Inhalt des Feldes aus
        der Auftragsdatei an.
    :ivar dateianzahl: Anzahl der eingegangenen Dateien innerhalb der
        Datenlieferung.
    :ivar rechnungsanzahl: Anzahl der Rechnungen innerhalb der
        Datenlieferung.
    """

    class Meta:
        namespace = "http://padinfo.de/ns/pad"

    nachrichtentyp: str = field(
        init=False,
        default="QADL",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    eingangsdatum: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    status: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fehler: List[FehlerTyp] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    datenlieferung: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "total_digits": 6,
        },
    )
    dateianzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    rechnungsanzahl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
