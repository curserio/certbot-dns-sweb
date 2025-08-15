import requests
from typing import Optional, Dict, Any, List

DEFAULT_BASE_URL = "https://api.sweb.ru"

class SwebAPIError(Exception):
    pass

class SwebAPI:
    """
    Minimal SpaceWeb API helper for DNS TXT management via official JSON-RPC.
    Endpoints:
      - Auth: POST https://api.sweb.ru/notAuthorized/ method=getToken
      - DNS:  POST https://api.sweb.ru/domains/dns      methods: info, editTxt
    """
    def __init__(self, base_url: str = DEFAULT_BASE_URL, token: Optional[str] = None,
                 login: Optional[str] = None, password: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self._token = token
        self._login = login
        self._password = password
        self.timeout = timeout

    @property
    def token(self) -> str:
        if self._token:
            return self._token
        if self._login and self._password:
            self._token = self.get_token(self._login, self._password)
            return self._token
        raise SwebAPIError("No token or login/password configured for SpaceWeb API")

    def _post(self, path: str, payload: Dict[str, Any], authorized: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.strip('/')}"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        }
        if authorized:
            headers["Authorization"] = f"Bearer {self.token}"
        r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        try:
            data = r.json()
        except Exception as e:
            raise SwebAPIError(f"Non-JSON response from {url}: {r.status_code} {r.text[:200]}") from e
        if "error" in data and data["error"]:
            msg = data["error"].get("message", "Unknown API error")
            raise SwebAPIError(msg)
        return data

    # ---------- Methods ----------
    def get_token(self, login: str, password: str) -> str:
        payload = {"jsonrpc": "2.0", "method": "getToken", "params": {"login": login, "password": password}}
        data = self._post("notAuthorized/", payload, authorized=False)
        token = data.get("result")
        if not token:
            raise SwebAPIError("SpaceWeb getToken returned no result")
        return token

    def dns_info(self, domain: str) -> Dict[str, Any]:
        payload = {"jsonrpc": "2.0", "method": "info", "params": {"domain": domain}}
        return self._post("domains/dns", payload)

    def edit_txt(self, domain: str, action: str, subdomain: str, value: str, index: Optional[int] = None) -> Any:
        params = {"domain": domain, "action": action, "subDomain": subdomain, "value": value}
        if index is not None:
            params["index"] = index
        payload = {"jsonrpc": "2.0", "method": "editTxt", "params": params}
        data = self._post("domains/dns", payload)
        return data.get("result")

    # Helpers specific for ACME
    def add_acme_txt(self, domain: str, subdomain: str, value: str) -> None:
        # Different panels use different verbs; try a sequence.
        last_error = None
        for action in ("add", "create", "edit"):
            try:
                self.edit_txt(domain, action, subdomain, value)
                return
            except SwebAPIError as e:
                last_error = e
        raise SwebAPIError(f"Unable to add TXT record: {last_error}")

    def _find_txt_candidates(self, node) -> List[Dict[str, Any]]:
        out = []
        def walk(n):
            if isinstance(n, dict):
                if n.get("type") == "TXT":
                    out.append(n)
                for v in n.values():
                    walk(v)
            elif isinstance(n, list):
                for v in n:
                    walk(v)
        walk(node)
        return out

    def find_txt_index(self, domain: str, subdomain: str, value: str) -> Optional[int]:
        data = self.dns_info(domain)
        result = data.get("result") or {}
        candidates = self._find_txt_candidates(result)
        # Try to match by exact "name" and value
        for rec in candidates:
            name = str(rec.get("name", "")).rstrip(".")
            if name in ("", "@"):
                name = "@"
            if name == subdomain.rstrip(".") and str(rec.get("value")) == value:
                try:
                    return int(rec.get("index"))
                except Exception:
                    return None
        # Fallback: match just by value
        for rec in candidates:
            if str(rec.get("value")) == value:
                try:
                    return int(rec.get("index"))
                except Exception:
                    return None
        return None

    def delete_acme_txt(self, domain: str, subdomain: str, value: str) -> None:
        idx = self.find_txt_index(domain, subdomain, value)
        verbs = ("remove", "delete", "edit")
        if idx is not None:
            for action in verbs:
                try:
                    self.edit_txt(domain, action, subdomain, value, index=idx)
                    return
                except SwebAPIError:
                    continue
        # Try without index
        for action in verbs:
            try:
                self.edit_txt(domain, action, subdomain, value)
                return
            except SwebAPIError:
                continue
        # Best-effort cleanup: do not raise
        return
