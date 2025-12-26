"""
Add Database Indexes for Performance
Run this once to add indexes that speed up queries
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.config import engine
from sqlalchemy import text

def add_indexes():
    """Add performance indexes to predictions table"""

    print("Adding database indexes for better performance...")

    conn = engine.connect()

    try:
        # Add status index
        conn.execute(text('CREATE INDEX IF NOT EXISTS ix_predictions_status ON predictions(status);'))
        print("✅ Created index on status column")

        # Add confidence index
        conn.execute(text('CREATE INDEX IF NOT EXISTS ix_predictions_confidence ON predictions(confidence);'))
        print("✅ Created index on confidence column")

        conn.commit()
        print("\n✅ All indexes created successfully!")
        print("Queries should now be much faster!")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    add_indexes()
