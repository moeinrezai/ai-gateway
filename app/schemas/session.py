import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_agent: str | None
    ip_hash: str | None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_current: bool = False
