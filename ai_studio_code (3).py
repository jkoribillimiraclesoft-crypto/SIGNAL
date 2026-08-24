from datetime import datetime
from typing import Optional, Dict
from sqlmodel import SQLModel, Field, create_engine, JSON, Column

class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    url: str = Field(unique=True)
    source: str
    category: str
    date_added: datetime = Field(default_factory=datetime.utcnow)
    
    # AI Analysis
    summary: str
    whats_new: str
    why_matters: str
    why_learn: str
    gcp_use: str  # Yes / Potentially / No
    gcp_use_case: str
    
    # Scoring
    relevance_score: float
    scores_json: Dict = Field(default={}, sa_column=Column(JSON))
    priority: str  # must, important, explore, watch

sqlite_file_name = "datapulse.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)