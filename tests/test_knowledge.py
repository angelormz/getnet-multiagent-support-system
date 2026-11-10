
from app.agents.knowledge import is_getnet_question
from app.agents.knowledge import handle_knowledge
from app.tools.web_search import search_web
from ddgs.exceptions import DDGSException


def test_getnet_product():
    assert is_getnet_question(
        "¿Qué tarjetas acepta Get Smart?"
    ) is True


def test_payment_terminal():
    assert is_getnet_question(
        "¿Cómo funciona mi terminal de pago?"
    ) is True


def test_settlements():
    assert is_getnet_question(
        "¿Cómo puedo consultar mis liquidaciones?"
    ) is True


def test_general_question():
    assert is_getnet_question(
        "¿Qué es la computación cuántica?"
    ) is False


def test_python_question():
    assert is_getnet_question(
        "¿Qué es Python?"
    ) is False


def test_knowledge_without_web_results(monkeypatch):
    monkeypatch.setattr(
        "app.agents.knowledge.search_web",
        lambda query, max_results=3: [],
    )

    result = handle_knowledge(
        "¿Qué es la computación cuántica?"
    )

    assert result["status"] == "insufficient_information"
    assert result["sources"] == []



def test_web_search_provider_failure(monkeypatch):
    from app.tools import web_search

    class FakeDDGS:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def text(self, query, **kwargs):
            raise DDGSException("Provider unavailable")

    monkeypatch.setattr(
        web_search,
        "DDGS",
        FakeDDGS,
    )

    result = web_search.search_web(
        "computación cuántica",
        max_results=2,
    )

    assert result == []



def test_knowledge_llm_timeout(monkeypatch):
    import httpx

    # 1. Simulamos documentos recuperados del RAG.
    def fake_search(question, top_k=3):
        return [
            {
                "text": "Getnet Portal is a sales management tool.",
                "source": "https://www.getnet.net/mx/",
                "country": "MX",
                "distance": 0.1,
            }
        ]

    # 2. Simulamos que Ollama tarda demasiado.
    def fake_llm(*args, **kwargs):
        raise httpx.ReadTimeout(
            "Simulated Ollama timeout"
        )

    # 3. Sustituimos temporalmente las funciones reales.
    monkeypatch.setattr(
        "app.agents.knowledge.search_knowledge",
        fake_search,
    )

    monkeypatch.setattr(
        "app.agents.knowledge.generate_response",
        fake_llm,
    )

    # 4. Ejecutamos el Knowledge Agent.
    result = handle_knowledge(
        "What is Getnet Portal?"
    )

    # 5. Verificamos el comportamiento esperado.
    assert result["status"] == "error"
    assert result["sources"] == []
    assert "tardó demasiado" in result["answer"]
