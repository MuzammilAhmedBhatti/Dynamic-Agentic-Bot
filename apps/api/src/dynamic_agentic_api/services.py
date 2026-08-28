from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from dynamic_agentic_api.agents.document_graph import DocumentRagGraph
from dynamic_agentic_api.config import get_settings
from dynamic_agentic_api.data_sources.service import CredentialCipher, PostgresConnector
from dynamic_agentic_api.embeddings.providers import (
    EmbeddingProvider,
    FakeEmbeddingProvider,
    VertexEmbeddingProvider,
)
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.ingestion.ocr import UnavailableOcrService
from dynamic_agentic_api.ingestion.pdf import PdfProcessor
from dynamic_agentic_api.ingestion.scanning import SignatureOnlyMalwareScanner
from dynamic_agentic_api.ingestion.service import IngestionService
from dynamic_agentic_api.llm.gateway import FakeLlmProvider, LlmProvider, VertexGeminiProvider
from dynamic_agentic_api.llm.registry import LlmRegistry, ProviderModel
from dynamic_agentic_api.math.service import MathService
from dynamic_agentic_api.personas.service import PersonaRegistry
from dynamic_agentic_api.rag.service import RagService
from dynamic_agentic_api.storage.service import LocalStorageService, StorageService
from dynamic_agentic_api.tracing.service import TraceHub, TraceService
from dynamic_agentic_api.vector_store.service import (
    FakeVectorStore,
    PineconeVectorStore,
    VectorStore,
)


@dataclass(frozen=True, slots=True)
class CoreServices:
    storage: StorageService
    pdf: PdfProcessor
    traces: TraceService


@dataclass(frozen=True, slots=True)
class AiServices:
    ingestion: IngestionService
    rag: RagService
    graph: DocumentRagGraph
    vectors: VectorStore
    llms: LlmRegistry
    personas: PersonaRegistry
    database: PostgresConnector
    cipher: CredentialCipher


@lru_cache
def get_core_services() -> CoreServices:
    settings = get_settings()
    traces = TraceService(TraceHub())
    return CoreServices(
        storage=LocalStorageService(settings.local_storage_root),
        pdf=PdfProcessor(),
        traces=traces,
    )


@lru_cache
def get_ai_services() -> AiServices:
    settings = get_settings()
    core = get_core_services()
    embeddings: EmbeddingProvider
    llm: LlmProvider
    if settings.ai_provider_mode == "fake":
        embeddings = FakeEmbeddingProvider()
        vectors: VectorStore = FakeVectorStore()
        llm = FakeLlmProvider()
        catalog = [ProviderModel("fake", llm.model, True)]
    else:
        if not settings.managed_ai_configured:
            raise AppError(
                status_code=503,
                code="MANAGED_AI_NOT_CONFIGURED",
                message="Vertex AI and Pinecone configuration is required for this operation.",
            )
        assert settings.google_cloud_project
        assert settings.pinecone_api_key
        assert settings.pinecone_index
        embeddings = VertexEmbeddingProvider(
            project=settings.google_cloud_project,
            location=settings.resolved_vertex_embedding_location,
            model=settings.vertex_embedding_model,
            dimension=settings.vertex_embedding_dimension,
            timeout_seconds=settings.external_call_timeout_seconds,
            max_attempts=settings.external_call_max_attempts,
        )
        vectors = PineconeVectorStore(
            api_key=settings.pinecone_api_key,
            index_name=settings.pinecone_index,
            index_host=settings.pinecone_index_host,
            timeout_seconds=settings.external_call_timeout_seconds,
        )
        llm = VertexGeminiProvider(
            project=settings.google_cloud_project,
            location=settings.resolved_vertex_gemini_location,
            model=settings.vertex_gemini_model,
            timeout_seconds=settings.external_call_timeout_seconds,
            max_attempts=settings.external_call_max_attempts,
        )
        catalog = [
            ProviderModel("vertex-ai", settings.vertex_gemini_model, True),
            ProviderModel(
                "openai", "gpt-5.2", False, "OpenAI adapter/credentials are not configured."
            ),
            ProviderModel(
                "anthropic",
                "claude-sonnet-4-5",
                False,
                "Anthropic adapter/credentials are not configured.",
            ),
        ]
    llms = LlmRegistry([llm], catalog)
    personas = PersonaRegistry(default_provider=llm.provider_name, default_model=llm.model)
    cipher = CredentialCipher(settings)
    database = PostgresConnector(settings, cipher)
    rag = RagService(
        settings=settings,
        storage=core.storage,
        embeddings=embeddings,
        vectors=vectors,
        llm=llm,
    )
    ingestion = IngestionService(
        settings=settings,
        storage=core.storage,
        scanner=SignatureOnlyMalwareScanner(),
        pdf=core.pdf,
        ocr=UnavailableOcrService(),
        embeddings=embeddings,
        vectors=vectors,
    )
    return AiServices(
        ingestion=ingestion,
        rag=rag,
        graph=DocumentRagGraph(
            rag=rag,
            traces=core.traces,
            llms=llms,
            personas=personas,
            database=database,
            math=MathService(),
        ),
        vectors=vectors,
        llms=llms,
        personas=personas,
        database=database,
        cipher=cipher,
    )


def reset_test_services() -> None:
    get_ai_services.cache_clear()
    get_core_services.cache_clear()
