"""File storage utilities"""

import os
import aiofiles
from pathlib import Path
from typing import BinaryIO
import uuid


class FileStorage:
    """Handle file uploads and storage"""

    def __init__(self, base_path: str = "storage/uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_upload_path(self, user_id: str, project_id: str, filename: str) -> Path:
        """Get upload path for a file"""
        # Create directory structure: storage/uploads/{user_id}/{project_id}/
        user_path = self.base_path / user_id / project_id
        user_path.mkdir(parents=True, exist_ok=True)

        # Generate unique filename to avoid collisions
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"

        return user_path / unique_name

    async def save_file(
        self,
        file_content: bytes,
        user_id: str,
        project_id: str,
        filename: str
    ) -> str:
        """
        Save uploaded file

        Returns:
            Relative path to saved file
        """
        file_path = self.get_upload_path(user_id, project_id, filename)

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        # Return relative path
        return str(file_path.relative_to(self.base_path.parent))

    async def read_file(self, file_path: str) -> bytes:
        """Read file content"""
        full_path = self.base_path.parent / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        async with aiofiles.open(full_path, 'rb') as f:
            return await f.read()

    def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        full_path = self.base_path.parent / file_path

        if full_path.exists():
            full_path.unlink()
            return True

        return False

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        full_path = self.base_path.parent / file_path
        return full_path.stat().st_size if full_path.exists() else 0


# Global storage instance
file_storage = FileStorage()
