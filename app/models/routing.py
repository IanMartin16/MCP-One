from typing import Optional
from pydantic import BaseModel, Field

class OrchestrationInput(BaseModel):
    user_input: str
    intent_family: Optional[str] = None
    allowed_modules: list[str] = Field(default_factory=list)
    client_context: dict = Field(default_factory=dict)
    request_id: Optional[str] = None