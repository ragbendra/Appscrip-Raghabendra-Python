import logging
import re
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.auth import verify_api_key
from app.limiter import token_bucket
from app.session import session_tracker
from app.search import search_sector_news
from app.analyzer import analyze_sector
from app.models import TradeAnalysisResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trade Opportunities API",
    description=(
        "A FastAPI service that analyzes market data and provides trade opportunity "
        "insights for specific sectors in India. Powered by Google Gemini AI and "
        "real-time web search data from DuckDuckGo."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Simple validation
VALID_SECTOR_PATTERN = re.compile(r'^[a-zA-Z\s\-]{2,50}$')


def get_client_ip(request: Request) -> str:
    return request.client.host


@app.get(
    "/analyze/{sector}",
    response_model=TradeAnalysisResponse,
    summary="Analyze trade opportunities for a sector",
    description=(
        "Accepts an Indian market sector name and returns a structured markdown "
        "report covering export/import opportunities, market drivers, key players, "
        "risks, and analyst outlook. Data is sourced from live web search and "
        "analyzed by Google Gemini AI."
    ),
    tags=["Trade Analysis"],
    responses={
        200: {
            "description": "Successful analysis report",
            "content": {
                "application/json": {
                    "example": {
                        "sector": "pharmaceuticals",
                        "generated_at": "2026-03-31T00:00:00Z",
                        "report": "# Pharmaceuticals Sector — India Trade Opportunities Report\n\n## 1. Sector Overview\n..."
                    }
                }
            }
        },
        401: {"description": "Missing API key — `X-API-Key` header not provided"},
        403: {"description": "Invalid API key"},
        422: {"description": "Invalid sector name — must be 2-50 characters (letters, spaces, hyphens)"},
        429: {"description": "Rate limit exceeded — retry after the duration in the `Retry-After` header"},
        500: {"description": "AI analysis or report generation failed"},
    }
)
async def analyze_trade_opportunities(
    sector: str,
    request: Request,
    _: str = Depends(verify_api_key),
):
    # 1. Validate input
    sector = sector.strip().lower()
    if not VALID_SECTOR_PATTERN.match(sector):
        raise HTTPException(
            status_code=422,
            detail="Sector must be 2-50 characters (letters, spaces, hyphens)."
        )

    client_ip = get_client_ip(request)

    # 2. Rate limit
    allowed, retry_after = token_bucket.is_allowed(client_ip)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"Retry-After": str(retry_after)}
        )

    # 3. Track session
    session_tracker.record(client_ip, sector)

    # 4. Fetch data
    search_results = await search_sector_news(sector)

    # 5. Generate report
    try:
        report = await analyze_sector(sector, search_results)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate report"
        )

    if not report:
        raise HTTPException(
            status_code=500,
            detail="Empty report generated"
        )

    # 6. Return response
    return TradeAnalysisResponse(
        sector=sector,
        generated_at=datetime.now(timezone.utc),
        report=report
    )