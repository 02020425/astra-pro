from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings

CHINESE_SEPARATORS = [
    "\n\n", "\n",
    "。", "！", "？",
    "；", "：", "，",
    ".", "!", "?",
    ";", ":", ",",
    " ", "",
]


class TextChunker:
    """Splits raw text into overlapping chunks for embedding and retrieval."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def split(self, text: str) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            separators=CHINESE_SEPARATORS,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        return splitter.split_text(text)
