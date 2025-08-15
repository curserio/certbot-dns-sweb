from typing import Any, Callable
import time
from certbot.plugins import dns_common
from .sweb_api import SwebAPI

DOCS = "https://apidoc.sweb.ru/domains/dns"

class Authenticator(dns_common.DNSAuthenticator):
    """
    Certbot DNS-01 Authenticator for SpaceWeb official API.
    """

    description = "Obtain certificates using a DNS TXT record (SpaceWeb official API)."

    def more_info(self) -> str:
        return ("This plugin automates the DNS-01 challenge by creating and removing "
                "_acme-challenge TXT records via the official SpaceWeb JSON-RPC API. "
                f"Docs: {DOCS}")

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., Any]) -> None:
        super().add_parser_arguments(add, default_propagation_seconds=60)
        add("credentials", help="Path to SpaceWeb credentials INI file.")
        add("base-url", default="https://api.sweb.ru", help="SpaceWeb API base URL")

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "SpaceWeb credentials INI file",
            {
                "token": "SpaceWeb API token (optional if login+password provided)",
                "login": "SpaceWeb login (optional if token provided)",
                "password": "SpaceWeb password (optional if token provided)",
                "base_url": "API base URL (optional)",
            },
        )

    # --- Certbot hooks ---
    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        api = self._api_client()
        sub = self._to_sub(validation_name, domain)
        api.add_acme_txt(domain, sub, validation)
        time.sleep(self.conf("propagation-seconds"))

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        try:
            api = self._api_client()
            sub = self._to_sub(validation_name, domain)
            api.delete_acme_txt(domain, sub, validation)
        except Exception:
            # Best-effort
            pass

    # --- Helpers ---
    def _api_client(self) -> SwebAPI:
        token = self.credentials.conf("token") if self.credentials and self.credentials.conf("token") else None
        login = self.credentials.conf("login") if self.credentials and self.credentials.conf("login") else None
        password = self.credentials.conf("password") if self.credentials and self.credentials.conf("password") else None
        base_url = self.conf("base-url") or (self.credentials.conf("base_url") if self.credentials and self.credentials.conf("base_url") else "https://api.sweb.ru")
        return SwebAPI(base_url=base_url, token=token, login=login, password=password)

    @staticmethod
    def _to_sub(validation_name: str, domain: str) -> str:
        # Convert "_acme-challenge.example.com" -> "_acme-challenge"
        suffix = "." + domain.lstrip(".")
        if validation_name.endswith(suffix):
            return validation_name[: -len(suffix)]
        return validation_name
