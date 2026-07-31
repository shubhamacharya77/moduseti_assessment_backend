import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


class SupabaseStorageClient:
    """Wrapper service for Supabase object storage file uploads."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY

    def save_local_backup(self, file_bytes: bytes, filename: str, destination_dir: str = "./uploads") -> str:
        """Saves file locally if Supabase credentials are not configured."""
        os.makedirs(destination_dir, exist_ok=True)
        file_path = os.path.join(destination_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return file_path
