import sys
import os
from sqlalchemy import text

# Add the current directory to the Python path to allow absolute imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.db.session import engine

def run_migration():
    print("Connecting to the database to rename 'curious' to 'openness'...")
    try:
        with engine.connect() as conn:
            # PostgreSQL command to rename a column
            conn.execute(text('ALTER TABLE persons RENAME COLUMN curious TO openness;'))
            conn.commit()
            print("Successfully migrated the database scheme: renamed 'curious' to 'openness'.")
    except Exception as e:
        print("Failed to run migration. It's possible the column is already renamed or the database is inaccessible.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    run_migration()

