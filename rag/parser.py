import os
import json
from typing import Dict, List, Optional
from core_logging.logger import logger

class DocumentParser:
    """Parses and extracts content from various document and source code types."""
    
    @staticmethod
    def read_text_file(filepath: str) -> str:
        """Safely reads a text file using UTF-8."""
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {e}")
            return f"[ERROR] Could not read file: {e}"

    @staticmethod
    def parse_pdf(filepath: str) -> str:
        """Extracts text from PDF files, falling back gracefully if pypdf is missing."""
        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
            return "\n".join(text)
        except ImportError:
            logger.warning("pypdf is not installed. PDF text extraction is limited. Install via pip install pypdf")
            return f"[PARSING FAILED] pypdf library is missing. Cannot parse PDF at: {filepath}"
        except Exception as e:
            logger.error(f"Failed to parse PDF {filepath}: {e}")
            return f"[ERROR] Failed to parse PDF: {e}"

    @staticmethod
    def parse_docx(filepath: str) -> str:
        """Extracts text from DOCX files, falling back gracefully if python-docx is missing."""
        try:
            import docx
            doc = docx.Document(filepath)
            text = [para.text for para in doc.paragraphs]
            return "\n".join(text)
        except ImportError:
            logger.warning("python-docx is not installed. DOCX text extraction is limited. Install via pip install python-docx")
            return f"[PARSING FAILED] python-docx library is missing. Cannot parse DOCX at: {filepath}"
        except Exception as e:
            logger.error(f"Failed to parse DOCX {filepath}: {e}")
            return f"[ERROR] Failed to parse DOCX: {e}"

    def parse(self, filepath: str) -> str:
        """Router to select parser based on file extension."""
        _, ext = os.path.splitext(filepath.lower())
        logger.info(f"Parsing file: {filepath} with extension: {ext}")
        
        if ext in (".txt", ".md", ".json", ".yaml", ".yml", ".ini", ".conf", ".cfg", ".spec"):
            return self.read_text_file(filepath)
        elif ext in (".py", ".js", ".ts", ".php", ".sh", ".bash", ".bat", ".ps1", ".java", ".c", ".cpp", ".h"):
            # Source files can be read as standard text files
            content = self.read_text_file(filepath)
            # Prepend context to help LLM recognize file type and path
            return f"Source File: {os.path.basename(filepath)}\nPath: {filepath}\nExtension: {ext}\n\n```\n{content}\n```"
        elif ext == ".pdf":
            return self.parse_pdf(filepath)
        elif ext in (".docx", ".doc"):
            return self.parse_docx(filepath)
        else:
            # Fallback: try to read as standard text
            logger.warning(f"Unknown extension {ext} for {filepath}. Attempting to read as plain text.")
            return self.read_text_file(filepath)

# Global parser instance
document_parser = DocumentParser()
