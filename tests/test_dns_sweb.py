import unittest
from unittest.mock import patch, MagicMock
from certbot_dns_sweb.dns_sweb import Authenticator

class DummyCreds:
    def __init__(self, data):
        self._data = data
    def conf(self, key):
        return self._data.get(key)

class DummyConfig(dict):
    def __call__(self, key):
        return self.get(key)

class TestPlugin(unittest.TestCase):
    @patch("certbot_dns_sweb.dns_sweb.SwebAPI")
    def test_perform_calls_add(self, api_cls):
        api = MagicMock()
        api_cls.return_value = api

        a = Authenticator(config=DummyConfig({"propagation-seconds": 0}), name="dns-sweb")
        a.credentials = DummyCreds({"token": "X"})
        a._perform("example.ru", "_acme-challenge.example.ru", "value123")
        api.add_acme_txt.assert_called_with("example.ru", "_acme-challenge", "value123")

    @patch("certbot_dns_sweb.dns_sweb.SwebAPI")
    def test_cleanup_calls_delete(self, api_cls):
        api = MagicMock()
        api_cls.return_value = api

        a = Authenticator(config=DummyConfig({"propagation-seconds": 0}), name="dns-sweb")
        a.credentials = DummyCreds({"token": "X"})
        a._cleanup("example.ru", "_acme-challenge.example.ru", "value123")
        api.delete_acme_txt.assert_called_with("example.ru", "_acme-challenge", "value123")

if __name__ == "__main__":
    unittest.main()
