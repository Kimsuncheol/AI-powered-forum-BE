from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Get environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ MySQL connection successful:", result.scalar())
    except Exception as e:
        print("❌ MySQL connection failed:", e)

if __name__ == "__main__":
    test_connection()