import pytest
from unittest.mock import patch, MagicMock
from astra_pro.llm import LLMClient


def test_llm_client_initialization():
    client = LLMClient()
    assert client is not None
    assert client.default_model is not None