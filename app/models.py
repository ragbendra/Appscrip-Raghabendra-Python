from pydantic import BaseModel
from datetime import datetime

class TradeAnalysisResponse(BaseModel):
    sector: str
    generated_at: datetime
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