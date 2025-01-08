import os
import sqlite3
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import streamlit as st

from utils.helpers.logger import logger


class DistributionStatus(Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DistributionStore:
    def __init__(self, api_key: str):
        """Initialize distribution store for the given API key."""
        self.api_key = api_key
        self.base_dir = os.path.join(
            os.path.dirname(__file__), "../../data/distribution", self.api_key
        )
        self.db_path = self._get_db_path()

        # Initialize fresh database
        os.makedirs(self.base_dir, exist_ok=True)
        self._initialize_db()

    def _get_db_path(self) -> str:
        """Get the path to the SQLite database file."""
        return os.path.join(self.base_dir, "distribution.db")

    def _initialize_db(self) -> None:
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS distribution_documents (
                        id TEXT PRIMARY KEY,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        processed_text TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    )
                """
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error initializing distribution store: {e}")
            raise

    def store_document_file(self, document_id: str, file_data: bytes) -> str:
        """Store the original document file."""
        file_path = os.path.join(self.base_dir, document_id)
        try:
            with open(file_path, "wb") as f:
                f.write(file_data)
            return file_path
        except Exception as e:
            logger.error(f"Error storing distribution document file {document_id}: {e}")
            raise

    def get_document_path(self, document_id: str) -> Optional[str]:
        """Get the path to the original document file."""
        file_path = os.path.join(self.base_dir, document_id)
        if os.path.exists(file_path):
            return file_path
        return None

    def add_document(self, document_id: str) -> None:
        """Add a new document to the store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                now = datetime.now().isoformat()
                conn.execute(
                    """
                    INSERT OR REPLACE INTO distribution_documents
                    (id, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (document_id, DistributionStatus.UPLOADED.value, now, now),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error adding distribution document {document_id}: {e}")
            raise

    def update_status(
        self,
        document_id: str,
        status: DistributionStatus,
        error_message: Optional[str] = None,
        processed_text: Optional[str] = None,
    ) -> None:
        """Update the status of a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                now = datetime.now().isoformat()
                conn.execute(
                    """
                    UPDATE distribution_documents
                    SET status = ?, error_message = ?, processed_text = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        status.value,
                        error_message,
                        processed_text,
                        now,
                        document_id,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(
                f"Error updating status for distribution document {document_id}: {e}"
            )
            raise

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document details by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM distribution_documents WHERE id = ?", (document_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting distribution document {document_id}: {e}")
            raise

    def cleanup(self) -> None:
        """Clean up the distribution store."""
        try:
            if os.path.exists(self.base_dir):
                import shutil

                shutil.rmtree(self.base_dir)
        except Exception as e:
            logger.error(f"Error cleaning up distribution store: {e}")
            raise


@st.cache_resource
def get_distribution_store() -> DistributionStore:
    """Get or create a DistributionStore instance."""
    if "distribution_store" not in st.session_state:
        st.session_state.distribution_store = DistributionStore(
            st.session_state.api_key
        )
    return st.session_state.distribution_store
