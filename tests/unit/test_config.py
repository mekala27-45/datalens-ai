"""Tests for application configuration."""


from datalens_ai.core.config import (
    AppConfig,
    get_available_providers,
    is_demo_mode,
)


class TestAppConfig:
    def test_defaults(self):
        config = AppConfig()
        assert config.ai.default_provider == "mock"
        assert config.engine.max_result_rows == 10000
        assert config.ui.theme == "professional"


class TestIsDemo:
    def test_demo_when_no_key(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("DATALENS_DEMO_MODE", raising=False)
        assert is_demo_mode() is True

    def test_not_demo_when_key_set(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        assert is_demo_mode() is False

    def test_explicit_demo_mode(self, monkeypatch):
        monkeypatch.setenv("DATALENS_DEMO_MODE", "true")
        assert is_demo_mode() is True


class TestGetAvailableProviders:
    def test_mock_always_available(self):
        providers = get_available_providers()
        mock = [p for p in providers if p["key"] == "mock"]
        assert len(mock) == 1
        assert mock[0]["available"] is True
