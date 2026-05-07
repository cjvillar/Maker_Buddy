"""
DigiKey API v4 client for Maker Buddy.

Token strategy: stored in Django's cache backend (works across multiple
workers/processes).  Falls back to a fresh fetch on any cache miss.

Usage:
    from parts.services.digikey import DigiKeyClient
    client = DigiKeyClient()
    part   = client.get_part("2648-SC0915TR-ND")
    hits   = client.keyword_search("ATmega328P", limit=5)
"""

# from __future__ import annotations

import logging
import time
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
DETAILS_URL = "https://api.digikey.com/products/v4/search/{part}/productdetails"
KEYWORD_URL = "https://api.digikey.com/products/v4/search/keyword"

CACHE_KEY_TOKEN = "digikey_oauth_token"
# shave 60 sec off the real TTL so never serve a token that expires mid-request
TOKEN_TTL_BUFFER = 60


# Exceptions
class DigiKeyError(Exception):
    """Base error for all DigiKey client problems."""


class DigiKeyAuthError(DigiKeyError):
    """Raised when we cannot obtain / refresh an OAuth token."""


class DigiKeyRateLimitError(DigiKeyError):
    """Raised on HTTP 429 — caller should back off and retry."""


class DigiKeyNotFoundError(DigiKeyError):
    """Raised when a part number returns no results."""


# Client
class DigiKeyClient:
    """
    Thin wrapper around the DigiKey Products v4 API.

    Credentials are read from Django settings:
        DIGIKEY_CLIENT_ID
        DIGIKEY_CLIENT_SECRET

    Both should come from environment variables via django-environ or
    python-dotenv — never hard-coded.
    """

    def __init__(self) -> None:
        self.client_id = settings.DIGIKEY_CLIENT_ID
        self.client_secret = settings.DIGIKEY_CLIENT_SECRET
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-DIGIKEY-Locale-Site": "US",
                "X-DIGIKEY-Locale-Language": "en",
                "X-DIGIKEY-Locale-Currency": "USD",
                "Content-Type": "application/json",
            }
        )

    # Token

    def _fetch_token(self) -> dict:
        """Request a fresh token from DigiKey and store it in the cache."""
        logger.info("Fetching new DigiKey OAuth token.")
        try:
            resp = requests.post(
                TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
                timeout=10,
            )
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise DigiKeyAuthError(
                f"Token request failed ({exc.response.status_code}): {exc.response.text}"
            ) from exc
        except requests.RequestException as exc:
            raise DigiKeyAuthError(f"Token request network error: {exc}") from exc

        token = resp.json()
        ttl = token.get("expires_in", 1800) - TOKEN_TTL_BUFFER
        cache.set(CACHE_KEY_TOKEN, token, timeout=ttl)
        logger.debug("DigiKey token cached for %d seconds.", ttl)
        return token

    def _get_token(self) -> dict:
        """Return a valid token from cache, or fetch a new one."""
        token = cache.get(CACHE_KEY_TOKEN)
        if token is None:
            token = self._fetch_token()
        return token

    def _auth_headers(self) -> dict:
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token['access_token']}",
            "X-DIGIKEY-Client-Id": self.client_id,
        }

    def _request(
        self,
        method: str,
        url: str,
        *,
        retry_on_401: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Make an authenticated request with basic retry logic:
          - 401 clear cache, re-fetch token, retry once
          - 429 raise DigiKeyRateLimitError immediately (caller decides)
          - other 4xx/5xx raise DigiKeyError
        """
        kwargs.setdefault("timeout", 15)
        headers = {**self._auth_headers(), **kwargs.pop("headers", {})}

        try:
            resp = self.session.request(method, url, headers=headers, **kwargs)
        except requests.RequestException as exc:
            raise DigiKeyError(f"Network error calling DigiKey: {exc}") from exc

        if resp.status_code == 401 and retry_on_401:
            logger.warning("DigiKey 401 — clearing token cache and retrying once.")
            cache.delete(CACHE_KEY_TOKEN)
            return self._request(method, url, retry_on_401=False, **kwargs)

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "unknown")
            raise DigiKeyRateLimitError(
                f"DigiKey rate limit hit. Retry After: {retry_after}s"
            )

        if resp.status_code == 404:
            raise DigiKeyNotFoundError(f"Part not found: {url}")

        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise DigiKeyError(
                f"DigiKey API error {resp.status_code}: {resp.text}"
            ) from exc

        return resp.json()

    # Public API

    def get_part(self, digikey_part_number: str) -> dict[str, Any]:
        """
        Fetch full product details for a single DigiKey part number.

        Returns the normalised dict from `_normalise_part`.
        Raises DigiKeyNotFoundError if the part doesn't exist.
        """
        url = DETAILS_URL.format(
            part=requests.utils.quote(digikey_part_number, safe="")
        )
        data = self._request("GET", url)
        product = data.get("Product")
        if not product:
            raise DigiKeyNotFoundError(
                f"No product found for part number: {digikey_part_number!r}"
            )
        return self._normalise_part(product)

    def keyword_search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Search by keyword or manufacturer part number.

        Returns a list of normalised part dicts (may be empty).
        """
        payload = {"Keywords": query, "Limit": limit, "Offset": offset}
        data = self._request("POST", KEYWORD_URL, json=payload)
        return [self._normalise_part(p) for p in data.get("Products", [])]

    def bulk_get_parts(
        self,
        part_numbers: list[str],
    ) -> dict[str, dict[str, Any] | None]:
        """
        Fetch details for a list of DigiKey part numbers.

        Returns a mapping of  { part_number: normalised_dict | None }.
        None means the part was not found or errored; the error is logged
        but does not abort the whole batch.
        """
        results: dict[str, dict | None] = {}
        for pn in part_numbers:
            try:
                results[pn] = self.get_part(pn)
                logger.debug("Fetched %s OK.", pn)
            except DigiKeyNotFoundError:
                logger.warning("Part not found on DigiKey: %s", pn)
                results[pn] = None
            except DigiKeyRateLimitError:
                # Re-raise the caller (management command / tasks) should
                # back off and reschedule.
                raise
            except DigiKeyError as exc:
                logger.error("Error fetching %s: %s", pn, exc)
                results[pn] = None
            # Delay between requests can adjust to stay under rate limits.
            time.sleep(0.25)
        return results

    # Normalisation

    @staticmethod
    def _normalise_part(raw: dict) -> dict[str, Any]:
        """
        Flatten the DigiKey v4 response into a consistent internal schema.

        v4 field mapping (differs from v3):
          - DigiKeyPartNumber: ProductVariations[0].DigiKeyProductNumber
          - ManufacturerPartNumber : ManufacturerProductNumber (top-level)
          - Description        : Description.ProductDescription
          - StandardPricing    : ProductVariations[0].StandardPricing
          - UnitPrice          : lowest break qty from variations pricing
        """
        # Pull the first variation (Cut Tape preferred, else first available)
        variations = raw.get("ProductVariations", [])
        variation = next(
            (
                v
                for v in variations
                if v.get("PackageType", {}).get("Name") == "Cut Tape (CT)"
            ),
            variations[0] if variations else {},
        )

        # Pricing from the matched variation
        pricing = [
            {
                "break_qty": tier["BreakQuantity"],
                "unit_price": tier["UnitPrice"],
            }
            for tier in variation.get("StandardPricing", [])
        ]

        # Unit price = lowest break qty price from variation
        unit_price = pricing[0]["unit_price"] if pricing else raw.get("UnitPrice")

        return {
            "digikey_part_number": variation.get("DigiKeyProductNumber", ""),
            "manufacturer_pn": raw.get("ManufacturerProductNumber", ""),
            "manufacturer": raw.get("Manufacturer", {}).get("Name", ""),
            "description": raw.get("Description", {}).get("ProductDescription", ""),
            "unit_price": unit_price,
            "quantity_available": variation.get("QuantityAvailableforPackageType")
            or raw.get("QuantityAvailable"),
            "product_url": raw.get("ProductUrl", ""),
            "datasheet_url": raw.get("DatasheetUrl", ""),
            "category": raw.get("Category", {}).get("Name", ""),
            "pricing_tiers": pricing,
            "source": "digikey",
        }
