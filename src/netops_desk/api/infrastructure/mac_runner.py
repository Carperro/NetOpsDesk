"""Adaptador de infraestructura para mac-vendor-lookup."""

# Cambiamos VendorNotFound por VendorNotFoundError
from mac_vendor_lookup import MacLookup, VendorNotFoundError

class MacVendorLookupAdapter:
    def __init__(self):
        self.lookup_client = MacLookup()

    def lookup(self, mac: str) -> str:
        try:
            return self.lookup_client.lookup(mac)
        except VendorNotFoundError: # <-- Acá también
            return "Desconocido"