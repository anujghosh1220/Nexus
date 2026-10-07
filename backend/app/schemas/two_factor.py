from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.schemas.user import UserResponse


class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_code_uri: str
    issuer: str = "NEXUS"
    account: str


class TwoFactorVerifyRequest(BaseModel):
    token: str = Field(..., min_length=6, max_length=6, pattern=r"^[0-9]+$")


class TwoFactorVerifyResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    requires_2fa: bool = False


class TwoFactorDisableRequest(BaseModel):
    password: str = Field(..., min_length=1)


class TwoFactorStatusResponse(BaseModel):
    enabled: bool
