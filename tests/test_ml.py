import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base, DomainScore
from backend.ml.features import FeatureEngineer
from backend.ml.labels import LabelGenerator
from backend.ml.train import ModelTrainer
from backend.ml.inference import InferenceEngine


@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_ml_pipeline_e2e(test_session, tmp_path):
    # 1. Populate DB with sufficient data to allow rolling features and diffs
    now = datetime(2024, 1, 10)
    records = []
    
    # We populate 14 days of data for two countries so rolling(7) fills
    for i in range(14):
        ts = now - timedelta(days=i)
        
        # Normal operations
        base_score = 10.0
        # If it's near May 2022 (when seed events say disruption is), we would simulate.
        # But we can just use any date, we'll configure a dummy JSON override if needed,
        # or we just let it train with all 0s if we don't mock the JSON.
        # However, RandomForest requires both classes (0 and 1) to fit without crashing if we don't handle it gracefully.
        # The LabelGenerator reads data/seed/disruption_events.json natively. One of the events is E01 at "2022-05-14".
        
        # Instead of 2024, let's inject data directly around 2022-05-14 so it grabs the real label!
        ts_real = datetime(2023, 10, 8) - timedelta(days=i)
        
        # As it gets closer to event, score spikes
        score_val = 80.0 if i < 3 else 20.0
        
        records.append(DomainScore(
            domain_id="energy_dependence",
            entity_type="country",
            entity_id="FI",
            timestamp=ts_real,
            score=score_val,
            data_coverage=1.0
        ))
        
        # Inject standard stable data for another country
        records.append(DomainScore(
            domain_id="energy_dependence",
            entity_type="country",
            entity_id="LT",
            timestamp=ts_real,
            score=15.0,
            data_coverage=1.0
        ))
        
    test_session.bulk_save_objects(records)
    test_session.commit()
    
    start_train = datetime(2023, 10, 1)
    end_train = datetime(2023, 10, 15)
    
    # Run Feature Engineering
    fe = FeatureEngineer(test_session)
    df_feat = fe.generate_features(start_train, end_train)
    
    assert not df_feat.empty
    assert "energy_dependence_vel" in df_feat.columns
    assert "energy_dependence_volatility_7d" in df_feat.columns
    
    # Run Label Generation
    lg = LabelGenerator()
    df_label = lg.get_labels(df_feat)
    assert not df_label.empty
    assert "label" in df_label.columns
    # Check if we successfully tagged the 2022-05-14 window based on seed data
    assert df_label["label"].sum() > 0
    
    # Train
    trainer = ModelTrainer(test_session)
    # Mocking the ARTEFACTS_DIR so we don't overwrite production disk state
    import backend.ml.train as tr
    tr.ARTEFACTS_DIR = tmp_path
    
    saved_path = trainer.train_and_save(start_train, end_train)
    assert Path(saved_path).exists()
    
    # Inference
    import backend.ml.inference as inf
    inf.MODEL_PATH = Path(saved_path)
    engine = InferenceEngine(custom_model_path=Path(saved_path))
    
    df_pred = engine.predict_risk(df_feat)
    assert not df_pred.empty
    assert "risk_probability" in df_pred.columns
    
    # A predictive probability float should be bound to each row
    assert isinstance(df_pred["risk_probability"].iloc[0], float)
