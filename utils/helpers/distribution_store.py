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
        os.makedirs(self.base_dir, exist_ok=True)
        return os.path.join(self.base_dir, "distribution.db")

    def _get_document_dir(self, document_id: str) -> str:
        """Get the directory path for a specific document."""
        # Always use base name without extension for directory
        base_id = document_id.rsplit(".", 1)[0] if "." in document_id else document_id
        doc_dir = os.path.join(self.base_dir, base_id)
        os.makedirs(doc_dir, exist_ok=True)
        return doc_dir

    def _initialize_db(self) -> None:
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS distribution_documents (
                        id TEXT PRIMARY KEY,
                        api_key TEXT NOT NULL,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        processed_text TEXT,
                        redacted_pdf_path TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    )
                    """
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error initializing distribution store: {e}", exc_info=True)
            raise

    def store_document_file(self, document_id: str, file_data: bytes) -> str:
        """Store the original document file."""
        # Get base name without extension for directory
        base_id = document_id.rsplit(".", 1)[0] if "." in document_id else document_id
        doc_dir = self._get_document_dir(base_id)

        # Use the original document_id for the file name
        file_path = os.path.join(doc_dir, document_id)

        try:
            with open(file_path, "wb") as f:
                f.write(file_data)
            return file_path
        except Exception as e:
            logger.error(
                f"Error storing distribution document file {document_id}: {e}",
                exc_info=True,
            )
            raise

    def get_document_path(self, document_id: str) -> Optional[str]:
        """Get the path to the original document file."""
        # Get base name without extension for directory
        base_id = document_id.rsplit(".", 1)[0] if "." in document_id else document_id
        doc_dir = self._get_document_dir(base_id)

        try:
            # First try exact match with document_id
            exact_path = os.path.join(doc_dir, document_id)
            if os.path.exists(exact_path):
                return exact_path

            # If not found, look for any file starting with the base_id
            files = [f for f in os.listdir(doc_dir) if f.startswith(base_id)]
            return os.path.join(doc_dir, files[0]) if files else None
        except Exception as e:
            logger.error(
                f"Error getting document path for {document_id}: {e}", exc_info=True
            )
            return None

    def add_document(self, document_id: str) -> None:
        """Add a new document to the store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if document already exists and is being processed
                cursor = conn.execute(
                    "SELECT status FROM distribution_documents WHERE id = ? AND api_key = ?",
                    (document_id, self.api_key),
                )
                existing = cursor.fetchone()
                if existing and existing[0] in [
                    DistributionStatus.UPLOADED.value,
                    DistributionStatus.PROCESSING.value,
                ]:
                    return  # Skip if already being processed

                # Delete existing document with same ID if exists for this user
                conn.execute(
                    "DELETE FROM distribution_documents WHERE id = ? AND api_key = ?",
                    (document_id, self.api_key),
                )

                now = datetime.now().isoformat()
                conn.execute(
                    """
                    INSERT INTO distribution_documents
                    (id, api_key, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        document_id,
                        self.api_key,
                        DistributionStatus.UPLOADED.value,
                        now,
                        now,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error adding document {document_id}: {e}", exc_info=True)
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
                    WHERE id = ? AND api_key = ?
                    """,
                    (
                        status.value,
                        error_message,
                        processed_text,
                        now,
                        document_id,
                        self.api_key,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(
                f"Error updating status for document {document_id}: {e}", exc_info=True
            )
            raise

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document details by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM distribution_documents WHERE id = ? AND api_key = ?",
                    (document_id, self.api_key),
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(
                f"Error getting distribution document {document_id}: {e}",
                exc_info=True,
            )
            raise

    def cleanup(self) -> None:
        """Clean up the distribution store."""
        try:
            if os.path.exists(self.base_dir):
                import shutil

                shutil.rmtree(self.base_dir)
        except Exception as e:
            logger.error(f"Error cleaning up distribution store: {e}", exc_info=True)
            raise

    def store_redacted_pdf_path(self, document_id: str, redacted_pdf_path: str) -> None:
        """Store the path to the redacted PDF file."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE distribution_documents
                    SET redacted_pdf_path = ?
                    WHERE id = ? AND api_key = ?
                    """,
                    (redacted_pdf_path, document_id, self.api_key),
                )
                conn.commit()
        except Exception as e:
            logger.error(
                f"Error storing redacted PDF path for document {document_id}: {e}",
                exc_info=True,
            )
            raise

    def get_redacted_pdf_path(self, document_id: str) -> Optional[str]:
        """Get the path to the redacted PDF file."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT redacted_pdf_path FROM distribution_documents WHERE id = ? AND api_key = ?",
                    (document_id, self.api_key),
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(
                f"Error getting redacted PDF path for document {document_id}: {e}",
                exc_info=True,
            )
            raise


@st.cache_resource
def get_distribution_store() -> DistributionStore:
    """Get or create a DistributionStore instance."""
    if "distribution_store" not in st.session_state:
        st.session_state.distribution_store = DistributionStore(
            st.session_state.api_key
        )
    return st.session_state.distribution_store
