from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import re

class TradeAnalysisResponse(BaseModel):
    sector: str
    generated_at: datetime
    cached: bool
    report: str

class SessionInfo(BaseModel):
    ip: str
    request_count: int
    sectors_queried: list[str]
    first_request: datetime
    last_request: datetime

class TokenBucketState(BaseModel):
    tokens: float
    last_refill: float