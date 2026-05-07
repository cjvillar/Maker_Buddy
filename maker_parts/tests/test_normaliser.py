from django.test import TestCase
from maker_parts.services.digikey import DigiKeyClient


class NormaliserTests(TestCase):
    """
    Tests for DigiKeyClient._normalise_part.

    These use a raw API response fixture so we never hit the real API.
    If DigiKey changes their response shape again, these tests will catch it.
    """

    # Mini v4 API response matching Digikey API response
    RAW_V4 = {
        "Description": {"ProductDescription": "RASPBERRY PI PICO RP2040"},
        "Manufacturer": {"Name": "Raspberry Pi"},
        "ManufacturerProductNumber": "SC0915",
        "UnitPrice": 4.59,
        "ProductUrl": "https://www.digikey.com/en/products/detail/raspberry-pi/SC0915/13624793",
        "DatasheetUrl": "https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf",
        "QuantityAvailable": 50674,
        "Category": {"Name": "Development Boards, Kits, Programmers"},
        "ProductVariations": [
            {
                "DigiKeyProductNumber": "2648-SC0915TR-ND",
                "PackageType": {"Id": 1, "Name": "Tape & Reel (TR)"},
                "StandardPricing": [
                    {
                        "BreakQuantity": 2400,
                        "UnitPrice": 4.00002,
                        "TotalPrice": 9600.048,
                    }
                ],
                "QuantityAvailableforPackageType": 50400,
            },
            {
                "DigiKeyProductNumber": "2648-SC0915CT-ND",
                "PackageType": {"Id": 2, "Name": "Cut Tape (CT)"},
                "StandardPricing": [
                    {"BreakQuantity": 1, "UnitPrice": 4.59, "TotalPrice": 4.59}
                ],
                "QuantityAvailableforPackageType": 50674,
            },
        ],
    }

    def test_digikey_part_number_from_variation(self):
        """DigiKeyProductNumber must come from ProductVariations, not top level."""
        result = DigiKeyClient._normalise_part(self.RAW_V4)
        self.assertEqual(result["digikey_part_number"], "2648-SC0915CT-ND")

    def test_manufacturer_pn_correct_field(self):
        """ManufacturerProductNumber is the v4 field name, not ManufacturerPartNumber."""
        result = DigiKeyClient._normalise_part(self.RAW_V4)
        self.assertEqual(result["manufacturer_pn"], "SC0915")

    def test_manufacturer_name(self):
        result = DigiKeyClient._normalise_part(self.RAW_V4)
        self.assertEqual(result["manufacturer"], "Raspberry Pi")

    def test_description(self):
        result = DigiKeyClient._normalise_part(self.RAW_V4)
        self.assertEqual(result["description"], "RASPBERRY PI PICO RP2040")

    def test_pricing_tiers_populated(self):
        result = DigiKeyClient._normalise_part(self.RAW_V4)
        self.assertEqual(len(result["pricing_tiers"]), 1)
        self.assertEqual(result["pricing_tiers"][0]["break_qty"], 1)
        self.assertEqual(result["pricing_tiers"][0]["unit_price"], 4.59)

    def test_empty_variations_returns_empty_strings(self):
        """Gracefully handle a response with no variations."""
        raw = dict(self.RAW_V4)
        raw["ProductVariations"] = []
        result = DigiKeyClient._normalise_part(raw)
        self.assertEqual(result["digikey_part_number"], "")
        self.assertEqual(result["pricing_tiers"], [])
