import pytest
import pandas as pd
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base
from backend.ingestion.base import IngestionModule
from backend.ingestion.runner import run_all

class MockSuccessModule(IngestionModule):
    @property
    def source_name(self) -> str:
        return "mock_success"

    def fetch(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        return pd.DataFrame({"col": [1, 2, 3]})

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Just return the same df
        return df

    def load(self, df: pd.DataFrame, session) -> int:
        return len(df)


class MockFailModule(IngestionModule):
    @property
    def source_name(self) -> str:
        return "mock_fail"

    def fetch(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        raise ValueError("Simulated network failure")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def load(self, df: pd.DataFrame, session) -> int:
        return 0


def test_ingestion_runner():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 2)

    modules = [MockSuccessModule(), MockFailModule()]
    
    results = run_all(session, start_date, end_date, modules)

    # Runner should complete without raising exception
    assert "mock_success" in results
    assert results["mock_success"]["status"] == "success"
    assert results["mock_success"]["rows_loaded"] == 3

    assert "mock_fail" in results
    assert results["mock_fail"]["status"] == "error"
    assert "Simulated network failure" in results["mock_fail"]["error"]
