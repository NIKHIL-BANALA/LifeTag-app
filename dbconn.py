import os
import psycopg2
from urllib.parse import urlparse

# Get Neon DB URI from environment variable
NEON_URI = os.environ.get("DATABASE_URL")  # Set this in Render/Heroku

def get_conn():
    if not NEON_URI:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Parse the URI
    result = urlparse(NEON_URI)
    return psycopg2.connect(
        host=result.hostname,
        port=result.port or 5432,
        database=result.path.lstrip("/"),
        user=result.username,
        password=result.password,
        sslmode="require"
    )
