from fastapi import APIRouter

from app.providers.factory import get_provider_client
from app.models.provider import ProviderRequest

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/active")
def get_active_provider():
    client = get_provider_client()

    return {
        "provider": client.provider_name,
        "client_class": client.__class__.__name__,
    }


@router.post("/generate")
def generate_stub(payload: ProviderRequest):
    client = get_provider_client()
    response = client.generate(payload)
    return response