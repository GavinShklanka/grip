"""API router for structural tracking and governance artifacts."""

from fastapi import APIRouter
import json
from pathlib import Path

from backend.config import get_settings

router = APIRouter()

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

@router.get("/assumptions")
def get_assumptions():
    """Returns the parsed markdown assumptions register."""
    limitations_file = DOCS_DIR / "limitations.md"
    content = ""
    if limitations_file.exists():
        with open(limitations_file, encoding="utf-8") as f:
            content = f.read()
    else:
        # Note: We will generate the docs later in M29
        content = "Documentation pending logic generation."
        
    return {"assumptions_markdown": content}


@router.get("/provenance/{domain_id}/{country_id}")
def get_provenance(domain_id: str, country_id: str):
    """Exposes the exact deterministic boundaries formatting the metric origin structures."""
    # Reading config to show bounds
    try:
        with open(CONFIG_DIR / "domains.json", encoding="utf-8") as f:
            domains = json.load(f)["domains"]
            
        domain_meta = next((d for d in domains if d["id"] == domain_id), None)
        if not domain_meta:
            return {"error": "Domain not found"}
            
        return {
            "domain_id": domain_id,
            "country_id": country_id,
            "indicators_used": domain_meta["indicators"]
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/data-quality")
def get_data_quality():
    """Summarizes overall dataset staleness."""
    # Simulated wrapper since actual quality is embedded directly into DomainScore queries per M12.
    return {
        "status": "healthy",
        "description": "Calculated via staleness decay mappings directly inside Domain integration endpoints."
    }


@router.get("/system-status")
def get_system_status():
    """Surfaces engine configuration locks and bypass rules."""
    settings = get_settings()
    
    return {
        "api_bypassed": settings.demo_mode,
        "database_url": "sqlite:// (in-memory)" if ":memory:" in settings.database_url else "configured",
        "log_level": 'INFO'
    }
