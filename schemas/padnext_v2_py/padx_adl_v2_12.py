from dataclasses import dataclass

from schemas.padnext_v2_py.padx_basis_v2_12 import RechnungListe

__NAMESPACE__ = "http://padinfo.de/ns/pad"


@dataclass
class Rechnungen(RechnungListe):
    class Meta:
        name = "rechnungen"
        namespace = "http://padinfo.de/ns/pad"
