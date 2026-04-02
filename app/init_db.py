from app.db.session import engine
from app.db.base_class import Base
from app.models.domain import *

print("Creating tables directly via SQLAlchemy...")
try:
    Base.metadata.create_all(bind=engine)
    print("Successfully created all tables in Neon DB!")
except Exception as e:
    print(f"Failed to create tables: {e}")