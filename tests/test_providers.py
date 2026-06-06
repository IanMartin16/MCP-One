from app.models.provider import ProviderRequest
from app.providers.anthropic_client import AnthropicClient
from app.providers.openai_client import OpenAIClient


def test_openai_stub_generate():
    client = OpenAIClient()
    response = client.generate(
        ProviderRequest(prompt="Summarize the market.")
    )

    assert response.success is True
    assert response.provider == "openai"
    assert response.content is not None
    assert response.raw["stub"] is True


def test_anthropic_stub_generate():
    client = AnthropicClient()
    response = client.generate(
        ProviderRequest(prompt="Explain this capability.")
    )

    assert response.success is True
    assert response.provider == "anthropic"
    assert response.content is not None
    assert response.raw["stub"] is True