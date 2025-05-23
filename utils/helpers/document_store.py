import json
import os
import sqlite3
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from utils.helpers.logger import logger


class DocumentStatus(Enum):
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DocumentStore:
    def __init__(self, api_key: str):
        """Initialize document store for the given API key."""
        self.api_key = api_key
        # Create user-specific directory inside data folder
        self.base_dir = os.path.join(
            os.path.dirname(__file__), "../../data/users", self.api_key
        )
        self.db_path = self._get_db_path()

        # Clean up existing data for this user
        # self.cleanup()

        # Initialize fresh database
        os.makedirs(self.base_dir, exist_ok=True)
        self._initialize_db()

    def _get_db_path(self) -> str:
        """Get the path to the SQLite database file."""
        os.makedirs(self.base_dir, exist_ok=True)
        return os.path.join(self.base_dir, "documents.db")

    def _get_document_dir(self, document_id: str) -> str:
        """Get the directory path for a specific document."""
        # Always use base name without extension for directory
        base_id = document_id.rsplit(".", 1)[0] if "." in document_id else document_id
        doc_dir = os.path.join(self.base_dir, base_id)
        os.makedirs(doc_dir, exist_ok=True)
        return doc_dir

    def store_document_file(
        self, document_id: str, file_data: bytes, file_type: str
    ) -> str:
        """
        Store the original document file.

        Args:
            document_id: The ID of the document
            file_data: The binary content of the file
            file_type: The MIME type of the file

        Returns:
            str: Path to the stored file
        """
        # Get base name without extension for directory
        base_id = document_id.rsplit(".", 1)[0] if "." in document_id else document_id
        doc_dir = self._get_document_dir(base_id)

        # Use the original document_id if it has an extension, otherwise add one
        if "." not in document_id:
            extension = {
                "application/pdf": ".pdf",
                "image/png": ".png",
                "image/jpeg": ".jpg",
            }.get(file_type, ".pdf")
            file_name = f"{document_id}{extension}"
        else:
            file_name = document_id

        file_path = os.path.join(doc_dir, file_name)

        try:
            with open(file_path, "wb") as f:
                f.write(file_data)
            return file_path
        except Exception as e:
            logger.error(
                f"Error storing document file {document_id}: {e}", exc_info=True
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

    def _initialize_db(self) -> None:
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY,
                        api_key TEXT NOT NULL,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        result JSON,
                        api_headers JSON,
                        ocr_data JSON,
                        redacted_pdf_path TEXT,
                        user_modifications JSON,
                        ocr_text TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    )
                    """
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error initializing document store: {e}", exc_info=True)
            raise

    def add_document(self, document_id: str) -> None:
        """Add a new document to the store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if document already exists and is being processed
                cursor = conn.execute(
                    "SELECT status FROM documents WHERE id = ? AND api_key = ?",
                    (document_id, self.api_key),
                )
                existing = cursor.fetchone()
                if existing and existing[0] in [
                    DocumentStatus.UPLOADED.value,
                    DocumentStatus.QUEUED.value,
                    DocumentStatus.PROCESSING.value,
                ]:
                    return  # Skip if already being processed

                # Delete existing document with same ID if exists for this user
                conn.execute(
                    "DELETE FROM documents WHERE id = ? AND api_key = ?",
                    (document_id, self.api_key),
                )

                now = datetime.now().isoformat()
                conn.execute(
                    """
                    INSERT INTO documents (id, api_key, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        document_id,
                        self.api_key,
                        DocumentStatus.UPLOADED.value,
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
        status: DocumentStatus,
        error_message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        api_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Update the status of a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                now = datetime.now().isoformat()
                conn.execute(
                    """
                    UPDATE documents
                    SET status = ?, error_message = ?, result = ?, api_headers = ?, updated_at = ?
                    WHERE id = ? AND api_key = ?
                    """,
                    (
                        status.value,
                        error_message,
                        json.dumps(result) if result else None,
                        json.dumps(api_headers) if api_headers else None,
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
                    "SELECT * FROM documents WHERE id = ? AND api_key = ?",
                    (document_id, self.api_key),
                )
                row = cursor.fetchone()

                if row:
                    result = dict(row)
                    if result["result"]:
                        result["result"] = json.loads(result["result"])
                    if result.get("user_modifications"):
                        result["user_modifications"] = json.loads(
                            result["user_modifications"]
                        )
                    return result
                return None
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}", exc_info=True)
            raise

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the store for the current user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM documents WHERE api_key = ? ORDER BY created_at DESC",
                    (self.api_key,),
                )
                documents = []
                for row in cursor:
                    doc = dict(row)
                    if doc["result"]:
                        doc["result"] = json.loads(doc["result"])
                    documents.append(doc)
                return documents
        except Exception as e:
            logger.error(f"Error getting all documents: {e}", exc_info=True)
            raise

    def cleanup(self) -> None:
        """Clean up the document store and all stored files."""
        if not os.path.exists(self.base_dir):
            return

        try:
            # First try to close any open database connections
            with sqlite3.connect(self.db_path) as conn:
                conn.close()
        except Exception as e:
            logger.warning(f"Error closing database connection during cleanup: {e}")

        # Try to remove files with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                import shutil

                shutil.rmtree(self.base_dir)
                break
            except PermissionError as e:
                if attempt == max_retries - 1:
                    logger.warning(
                        f"Could not remove directory {self.base_dir} after {max_retries} attempts: {e}"
                    )
                else:
                    import time

                    time.sleep(0.5)  # Wait before retry
            except Exception as e:
                logger.warning(f"Error during cleanup of {self.base_dir}: {e}")
                break

    def store_ocr_data(self, document_id: str, ocr_data: dict) -> None:
        """Store OCR data including word coordinates for a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # First check if column exists
                cursor = conn.execute("PRAGMA table_info(documents)")
                columns = [col[1] for col in cursor.fetchall()]

                # Add column if it doesn't exist
                if "ocr_data" not in columns:
                    conn.execute("ALTER TABLE documents ADD COLUMN ocr_data JSON")

                # Update the data
                conn.execute(
                    """
                    UPDATE documents
                    SET ocr_data = ?
                    WHERE id = ? AND api_key = ?
                    """,
                    (json.dumps(ocr_data), document_id, self.api_key),
                )
                conn.commit()
        except Exception as e:
            logger.error(
                f"Error storing OCR data for document {document_id}: {e}", exc_info=True
            )
            raise

    def get_ocr_data(self, document_id: str) -> Optional[dict]:
        """Get OCR data including word coordinates for a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT ocr_data FROM documents WHERE id = ?", (document_id,)
                )
                row = cursor.fetchone()
                if row and row["ocr_data"]:
                    return json.loads(row["ocr_data"])
                return None
        except Exception as e:
            logger.error(
                f"Error getting OCR data for document {document_id}: {e}", exc_info=True
            )
            raise

    def store_redacted_pdf_path(self, document_id: str, redacted_pdf_path: str) -> None:
        """Store the path to the redacted version of a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE documents
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
        """Get the path to the redacted version of a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT redacted_pdf_path FROM documents WHERE id = ? AND api_key = ?",
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

    def store_user_modifications(self, document_id: str, df: pd.DataFrame) -> None:
        """Store user modifications to a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                now = datetime.now().isoformat()
                conn.execute(
                    """
                    UPDATE documents
                    SET user_modifications = ?, updated_at = ?
                    WHERE id = ? AND api_key = ?
                    """,
                    (df.to_json(orient="records"), now, document_id, self.api_key),
                )
                conn.commit()
        except Exception as e:
            logger.error(
                f"Error storing user modifications for document {document_id}: {e}",
                exc_info=True,
            )
            raise

    def store_ocr_text(self, document_id: str, ocr_text: str) -> None:
        """Store OCR text for a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                now = datetime.now().isoformat()
                conn.execute(
                    """
                    UPDATE documents
                    SET ocr_text = ?, updated_at = ?
                    WHERE id = ? AND api_key = ?
                    """,
                    (ocr_text or "", now, document_id, self.api_key),
                )
                conn.commit()
        except Exception as e:
            logger.error(
                f"Error storing OCR text for document {document_id}: {e}", exc_info=True
            )
            raise

    def get_ocr_text(self, document_id: str) -> str:
        """Get OCR text for a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT ocr_text FROM documents WHERE id = ? AND api_key = ?",
                    (document_id, self.api_key),
                )
                result = cursor.fetchone()
                return result[0] if result and result[0] else ""
        except Exception as e:
            logger.error(
                f"Error getting OCR text for document {document_id}: {e}", exc_info=True
            )
            return ""


def get_document_store(api_key: Optional[str] = None) -> DocumentStore:
    """Get or create a DocumentStore instance."""
    # Create a fresh instance each time
    if api_key is not None:
        return DocumentStore(api_key)
    if "document_store" not in st.session_state:
        st.session_state.document_store = DocumentStore(st.session_state.api_key)
    return st.session_state.document_store


def render_document_list_sidebar() -> None:
    """Render the sidebar with document list and status."""
    with st.sidebar:
        if st.session_state.stage != "analyze":
            if st.button("Zum Hauptmenü", use_container_width=True):
                st.session_state.stage = "analyze"
                st.rerun()
        if st.session_state.api_key_tested:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.title("Dokumente")
            with col2:
                if st.button("🔄", help="Aktualisieren"):
                    st.rerun()

            try:
                document_store = get_document_store(st.session_state.api_key)
                documents = (
                    document_store.get_all_documents()
                )  # Already filtered by api_key

                if not documents:
                    st.info("Keine Dokumente vorhanden")
                    return

                for doc in documents:
                    if doc["status"] != DocumentStatus.UPLOADED.value:
                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])

                            with col1:
                                doc_name = doc["id"]

                                if st.button(
                                    doc_name.replace("_", " | ")
                                    .replace(".pdf", "")
                                    .replace("pdf", ""),
                                    key=f"doc_btn_{doc_name}",
                                    use_container_width=True,
                                ):
                                    st.session_state.selected_document_id = doc_name
                                    st.session_state.stage = "result"
                                    from utils.session import reset

                                    reset()
                                    st.rerun()

                            with col2:
                                if doc["id"] == st.session_state.selected_document_id:
                                    st.write("📄")

                            with col3:
                                status = doc["status"]
                                if status == DocumentStatus.QUEUED.value:
                                    st.write("⏳")
                                elif status == DocumentStatus.PROCESSING.value:
                                    st.write("🤖")
                                elif status == DocumentStatus.COMPLETED.value:
                                    st.write("✅")
                                elif status == DocumentStatus.FAILED.value:
                                    st.write("❌")

                st.subheader("Weitere Dokumente hochladen:")
                uploaded_files = st.file_uploader(
                    "Dokumente hochladen",
                    type=["pdf", "png", "jpg"],
                    accept_multiple_files=True,
                    key="document_uploader_sidebar",
                    label_visibility="collapsed",
                )

                if uploaded_files:
                    from utils.stages.analyze import handle_file_upload

                    handle_file_upload(uploaded_files, from_sidebar=True)

                # Add section for uploaded documents
                if st.session_state.api_key_tested:
                    uploaded_docs = [
                        doc
                        for doc in documents
                        if doc["status"] == DocumentStatus.UPLOADED.value
                    ]
                else:
                    uploaded_docs = []
                if uploaded_docs:
                    st.subheader("Hochgeladene Dokumente:")
                    for doc in uploaded_docs:
                        st.text(doc["id"])

                st.subheader("Weitere Dokumente selektieren:")
                if st.button("Hier klicken", use_container_width=True):
                    st.session_state.stage = "select_documents"
                    st.rerun()

            except Exception:
                st.error("Bitte überprüfen Sie Ihre API-Einstellungen")
                return
