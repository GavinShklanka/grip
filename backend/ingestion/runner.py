"""Ingestion runner to orchestrate multiple data source modules."""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Type

from backend.ingestion.base import IngestionModule

logger = logging.getLogger(__name__)


def run_all(
    session: Session, 
    start_date: datetime, 
    end_date: datetime, 
    modules: List[IngestionModule]
) -> Dict[str, Any]:
    """Run multiple ingestion modules, isolating failures.

    Parameters
    ----------
    session : Session
        Database session to use for all modules.
    start_date : datetime
        Start of the fetch window.
    end_date : datetime
        End of the fetch window.
    modules : List[IngestionModule]
        Instantiated ingestion modules to run.

    Returns
    -------
    Dict[str, Any]
        Summary of the execution, mapping source_name to loaded row count or error string.
    """
    results = {}
    
    for module in modules:
        source = module.source_name
        try:
            rows = module.run(session, start_date, end_date)
            results[source] = {"status": "success", "rows_loaded": rows}
            
        except Exception as e:
            logger.error(f"Ingestion failed for module {source}: {str(e)}", exc_info=True)
            results[source] = {"status": "error", "error": str(e)}
            
            # Note: staleness flags will naturally arise because the data was not updated.
            # The scoring engine's quality checks handle staleness on the read side.
            
    return results
