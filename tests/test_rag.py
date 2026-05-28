import pytest
from astra_pro.rag.chunker import CHINESE_SEPARATORS, TextChunker
from astra_pro.rag.parser import DocumentParser
from astra_pro.tools.knowledge_base import KnowledgeBaseTool, knowledge_base_tool


class TestTextChunker:
    def test_chinese_splitting(self):
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        text = "这是第一句话。这是第二句话！这是第三句话？这是第四句话。"
        chunks = chunker.split(text)
        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk) <= 100

    def test_empty_text(self):
        chunker = TextChunker()
        chunks = chunker.split("")
        assert chunks == []

    def test_separators_order(self):
        zh_endings = {"。", "！", "？"}
        for sep in zh_endings:
            assert sep in CHINESE_SEPARATORS
        zh_idx = min(CHINESE_SEPARATORS.index(s) for s in zh_endings)
        en_idx = CHINESE_SEPARATORS.index(".")
        assert zh_idx < en_idx


class TestDocumentParser:
    def test_txt_parsing(self, tmp_path):
        file_path = tmp_path / "test.txt"
        file_path.write_text("Hello 世界", encoding="utf-8")
        parser = DocumentParser()
        result = parser.parse(str(file_path))
        assert "Hello 世界" in result

    def test_unsupported_extension(self):
        parser = DocumentParser()
        with pytest.raises(ValueError, match="Unsupported file type"):
            parser.parse("file.xyz")

    def test_md_parsing(self, tmp_path):
        file_path = tmp_path / "readme.md"
        content = "# Title\n\nSome **markdown** text."
        file_path.write_text(content, encoding="utf-8")
        parser = DocumentParser()
        result = parser.parse(str(file_path))
        assert "Title" in result
        assert "markdown" in result


class TestKnowledgeBaseTool:
    def test_tool_interface(self):
        tool = KnowledgeBaseTool()
        assert tool.name == "knowledge_base"
        assert isinstance(tool.description, str)

        definition = tool.get_definition()
        assert definition["type"] == "function"
        assert definition["function"]["name"] == "knowledge_base"
        params = definition["function"]["parameters"]
        assert "query" in params["properties"]
        assert "subject" in params["properties"]
        assert "top_k" in params["properties"]
        assert "query" in params["required"]

    def test_call_without_query(self):
        result = knowledge_base_tool.call({"query": ""})
        assert "知识库" in result
