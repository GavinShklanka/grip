"""Base ingestion interfaces for GRIP data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import pandas as pd
from typing import Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class IngestionModule(ABC):
    """Abstract interface that all data ingestion modules must implement."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Identifier for this data source (e.g., 'entso_e', 'entsog')."""
        pass

    @abstractmethod
    def fetch(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch raw data from the external source.

        Parameters
        ----------
        start_date : datetime
            Start of the fetch window.
        end_date : datetime
            End of the fetch window.

        Returns
        -------
        pd.DataFrame
            Raw data fetched from the source.
        """
        pass

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform raw data into the GRIP indicator format.

        Parameters
        ----------
        df : pd.DataFrame
            Raw data from fetch().

        Returns
        -------
        pd.DataFrame
            Transformed data ready for insertion into indicator_values table.
        """
        pass

    @abstractmethod
    def load(self, df: pd.DataFrame, session: Session) -> int:
        """Load transformed data into the database.

        Parameters
        ----------
        df : pd.DataFrame
            Transformed data.
        session : Session
            SQLAlchemy database session.

        Returns
        -------
        int
            Number of rows successfully inserted.
        """
        pass

    def run(self, session: Session, start_date: datetime, end_date: datetime) -> int:
        """Run the full ingestion pipeline for this module.

        Parameters
        ----------
        session : Session
            Database session to use.
        start_date : datetime
            Start of the fetch window.
        end_date : datetime
            End of the fetch window.

        Returns
        -------
        int
            Rows loaded.
        """
        logger.info(f"Running ingestion for {self.source_name} ({start_date} to {end_date})")
        df_raw = self.fetch(start_date, end_date)
        
        if df_raw.empty:
            logger.info(f"[{self.source_name}] fetch returned empty dataframe.")
            return 0
            
        df_transformed = self.transform(df_raw)
        
        if df_transformed.empty:
            logger.info(f"[{self.source_name}] transform returned empty dataframe.")
            return 0
            
        rows_loaded = self.load(df_transformed, session)
        logger.info(f"[{self.source_name}] Successfully loaded {rows_loaded} rows.")
        return rows_loaded
