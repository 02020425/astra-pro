import os

from ..log import logger


class DocumentParser:
    """Parses uploaded document files into plain text."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}

    def parse(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")

        logger.info("Parsing document", file_path=file_path, ext=ext)

        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext == ".docx":
            return self._parse_docx(file_path)
        elif ext in (".md", ".txt"):
            return self._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _parse_pdf(self, file_path: str) -> str:
        import fitz
        doc = fitz.open(file_path)
        try:
            pages = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    pages.append(text)
            text = "\n\n".join(pages)
            if not text.strip():
                raise ValueError("PDF contains no extractable text (possibly image-only)")
            return text.strip()
        finally:
            doc.close()

    def _parse_docx(self, file_path: str) -> str:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        if not paragraphs:
            raise ValueError("DOCX contains no text")
        return "\n".join(paragraphs)

    def _parse_text(self, file_path: str) -> str:
        for encoding in ("utf-8", "gbk", "gb2312", "utf-16"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    text = f.read()
                if text.strip():
                    return text.strip()
            except (UnicodeDecodeError, UnicodeError):
                continue
        raise ValueError("Could not decode file — tried utf-8, gbk, gb2312, utf-16")
