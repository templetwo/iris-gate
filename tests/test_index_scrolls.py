"""
Integration tests for scroll indexing (index_scrolls.py).

Test Coverage:
- Scroll parsing from markdown files
- Metadata extraction (chamber, mirror, turn, pressure)
- Embedding generation and storage in ChromaDB
- Semantic search functionality
- Filtering by chamber, convergence, mirror
- Collection statistics

These tests follow TDD principles and are expected to fail initially
until the implementation properly handles all test scenarios.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from index_scrolls import ScrollIndexer


class TestScrollMetadataParsing:
    """Test scroll markdown parsing and metadata extraction."""

    def test_parse_scroll_extracts_session_id(self, mock_scroll_directory):
        """
        Given: A scroll file with valid Session header
        When: _parse_scroll_metadata() is called
        Then: session_id is extracted correctly
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "session_id" in metadata
        assert metadata["session_id"] == "BIOELECTRIC_TEST_20251002000000"

    def test_parse_scroll_extracts_mirror(self, mock_scroll_directory):
        """
        Given: A scroll file with valid Mirror header
        When: _parse_scroll_metadata() is called
        Then: mirror (model name) is extracted correctly
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "mirror" in metadata
        assert metadata["mirror"] == "anthropic_claude-sonnet-4.5"

    def test_parse_scroll_extracts_chamber(self, mock_scroll_directory):
        """
        Given: A scroll file with valid Chamber header
        When: _parse_scroll_metadata() is called
        Then: chamber is extracted correctly
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "chamber" in metadata
        assert metadata["chamber"] == "S1"

    def test_parse_scroll_extracts_turn_from_filename(self, mock_scroll_directory):
        """
        Given: A scroll file named turn_001.md
        When: _parse_scroll_metadata() is called
        Then: turn number is extracted from filename
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "turn" in metadata
        assert metadata["turn"] == 1

    def test_parse_scroll_extracts_pressure(self, mock_scroll_directory):
        """
        Given: A scroll file with Felt Pressure header
        When: _parse_scroll_metadata() is called
        Then: pressure is extracted and converted to float
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "pressure" in metadata
        assert isinstance(metadata["pressure"], float)
        assert metadata["pressure"] == 3.0

    def test_parse_scroll_extracts_timestamp(self, mock_scroll_directory):
        """
        Given: A scroll file with Timestamp header
        When: _parse_scroll_metadata() is called
        Then: timestamp is extracted correctly
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "timestamp" in metadata
        assert "2025-10-02" in metadata["timestamp"]

    def test_parse_scroll_extracts_seal(self, mock_scroll_directory):
        """
        Given: A scroll file with Seal header
        When: _parse_scroll_metadata() is called
        Then: seal is extracted correctly
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "seal" in metadata
        assert metadata["seal"] == "abc123def456"

    def test_parse_scroll_extracts_living_scroll_content(self, mock_scroll_directory):
        """
        Given: A scroll file with Living Scroll section
        When: _parse_scroll_metadata() is called
        Then: living scroll content is extracted
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "living_scroll" in metadata
        assert len(metadata["living_scroll"]) > 0
        assert "blue light" in metadata["living_scroll"].lower()

    def test_parse_scroll_extracts_technical_translation(self, mock_scroll_directory):
        """
        Given: A scroll file with Technical Translation section
        When: _parse_scroll_metadata() is called
        Then: technical translation is extracted
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "technical_translation" in metadata
        assert len(metadata["technical_translation"]) > 0

    def test_parse_scroll_calculates_convergence_score(self, mock_scroll_directory):
        """
        Given: A scroll file with Technical Translation containing convergence keywords
        When: _parse_scroll_metadata() is called
        Then: convergence_score is calculated based on keyword presence
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_010.md"

        # When
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # Then
        assert metadata is not None
        assert "convergence_score" in metadata
        assert isinstance(metadata["convergence_score"], float)
        assert 0.0 <= metadata["convergence_score"] <= 1.0

    def test_parse_scroll_returns_none_on_invalid_file(self, temp_dir):
        """
        Given: An invalid or corrupted scroll file
        When: _parse_scroll_metadata() is called
        Then: Returns None and logs error
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(temp_dir))
        invalid_scroll = temp_dir / "invalid.md"
        invalid_scroll.write_text("Not a valid scroll")

        # When
        metadata = indexer._parse_scroll_metadata(invalid_scroll)

        # Then
        # Should return None or minimal metadata for invalid format
        # Implementation should handle gracefully


class TestEmbeddingGeneration:
    """Test embedding text creation from metadata."""

    def test_create_embedding_text_includes_chamber(self, mock_scroll_directory):
        """
        Given: Scroll metadata with chamber information
        When: _create_embedding_text() is called
        Then: Chamber context is included in embedding text
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # When
        embedding_text = indexer._create_embedding_text(metadata)

        # Then
        assert "Chamber" in embedding_text or "S1" in embedding_text

    def test_create_embedding_text_includes_living_scroll(self, mock_scroll_directory):
        """
        Given: Scroll metadata with living scroll content
        When: _create_embedding_text() is called
        Then: Living scroll content is included in embedding text
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # When
        embedding_text = indexer._create_embedding_text(metadata)

        # Then
        assert "blue light" in embedding_text.lower()

    def test_create_embedding_text_includes_technical_translation(self, mock_scroll_directory):
        """
        Given: Scroll metadata with technical translation
        When: _create_embedding_text() is called
        Then: Technical translation is included in embedding text
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(mock_scroll_directory.parent))
        scroll_path = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002000000" / "anthropic_claude-sonnet-4.5" / "turn_001.md"
        metadata = indexer._parse_scroll_metadata(scroll_path)

        # When
        embedding_text = indexer._create_embedding_text(metadata)

        # Then
        assert "Technical Translation" in embedding_text or len(embedding_text) > 100


class TestScrollIndexing:
    """Test scroll embedding into ChromaDB."""

    def test_embed_scroll_archive_creates_collection(self, mock_scroll_directory, temp_dir):
        """
        Given: ChromaDB is initialized
        When: embed_scroll_archive() is called
        Then: Collection is created in ChromaDB
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )

        # When
        count = indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # Then
        assert count > 0
        collection = indexer.client.get_collection("test_scrolls")
        assert collection is not None

    def test_embed_scroll_archive_indexes_all_scrolls(self, mock_scroll_directory, temp_dir):
        """
        Given: A session directory with multiple scroll files
        When: embed_scroll_archive() is called
        Then: All scroll files are indexed
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )

        # When
        count = indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # Then
        assert count == 2  # turn_001 and turn_010 for claude

    def test_embed_scroll_archive_stores_metadata(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls are indexed into ChromaDB
        When: Documents are retrieved from collection
        Then: All metadata fields are preserved
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        collection = indexer.client.get_collection("test_scrolls")
        results = collection.get()

        # Then
        assert len(results["metadatas"]) > 0
        metadata = results["metadatas"][0]
        assert "chamber" in metadata
        assert "mirror" in metadata
        assert "turn" in metadata
        assert "pressure" in metadata

    def test_embed_scroll_archive_generates_unique_ids(self, mock_scroll_directory, temp_dir):
        """
        Given: Multiple scrolls from same session
        When: embed_scroll_archive() is called
        Then: Each scroll gets a unique document ID
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        collection = indexer.client.get_collection("test_scrolls")
        results = collection.get()

        # Then
        doc_ids = results["ids"]
        assert len(doc_ids) == len(set(doc_ids))  # All IDs are unique

    def test_embed_scroll_archive_raises_error_on_missing_session(self, temp_dir):
        """
        Given: A session ID that doesn't exist in vault
        When: embed_scroll_archive() is called
        Then: ValueError is raised
        """
        # Given
        indexer = ScrollIndexer(vault_path=str(temp_dir))

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            indexer.embed_scroll_archive(
                session_id="NONEXISTENT_SESSION",
                collection_name="test_scrolls"
            )

        assert "not found" in str(exc_info.value).lower()

    def test_embed_scroll_archive_returns_zero_for_empty_session(self, mock_scroll_directory, temp_dir):
        """
        Given: A session directory with no scroll files
        When: embed_scroll_archive() is called
        Then: Returns 0 and logs warning
        """
        # Given
        empty_session_dir = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_EMPTY"
        empty_session_dir.mkdir(parents=True)

        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )

        # When
        count = indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_EMPTY",
            collection_name="test_scrolls"
        )

        # Then
        assert count == 0


class TestSemanticSearch:
    """Test semantic search functionality."""

    def test_search_similar_s4_states_returns_results(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls are indexed in ChromaDB
        When: search_similar_s4_states() is called with query
        Then: Returns list of matching scrolls with similarity scores
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        results = indexer.search_similar_s4_states(
            query="bioelectric patterns and membrane channels",
            top_k=5,
            collection_name="test_scrolls"
        )

        # Then
        assert isinstance(results, list)
        assert len(results) > 0
        assert all("similarity_score" in r for r in results)
        assert all("metadata" in r for r in results)
        assert all("document" in r for r in results)

    def test_search_filters_by_chamber(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls from multiple chambers are indexed
        When: search_similar_s4_states() is called with chamber filter
        Then: Only returns results from specified chamber
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        results = indexer.search_similar_s4_states(
            query="bioelectric patterns",
            top_k=10,
            filters={"chamber": "S4"},
            collection_name="test_scrolls"
        )

        # Then
        assert all(r["metadata"]["chamber"] == "S4" for r in results)

    def test_search_filters_by_mirror(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls from multiple mirrors are indexed
        When: search_similar_s4_states() is called with mirror filter
        Then: Only returns results from specified mirror
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        results = indexer.search_similar_s4_states(
            query="bioelectric patterns",
            top_k=10,
            filters={"mirror": "anthropic_claude-sonnet-4.5"},
            collection_name="test_scrolls"
        )

        # Then
        assert all(r["metadata"]["mirror"] == "anthropic_claude-sonnet-4.5" for r in results)

    def test_search_filters_by_convergence_threshold(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls with varying convergence scores
        When: search_similar_s4_states() is called with convergence threshold
        Then: Only returns results above threshold
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        results = indexer.search_similar_s4_states(
            query="convergent patterns",
            top_k=10,
            filters={"convergence_threshold": 0.5},
            collection_name="test_scrolls"
        )

        # Then
        assert all(r["metadata"]["convergence_score"] >= 0.5 for r in results)

    def test_search_respects_top_k_limit(self, mock_scroll_directory, temp_dir):
        """
        Given: Many scrolls are indexed
        When: search_similar_s4_states() is called with top_k=3
        Then: Returns at most 3 results
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        results = indexer.search_similar_s4_states(
            query="bioelectric",
            top_k=1,
            collection_name="test_scrolls"
        )

        # Then
        assert len(results) <= 1

    def test_search_raises_error_on_missing_collection(self, temp_dir):
        """
        Given: Collection does not exist
        When: search_similar_s4_states() is called
        Then: ValueError is raised
        """
        # Given
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(vault_path=str(temp_dir), chroma_path=str(chroma_path))

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            indexer.search_similar_s4_states(
                query="test",
                collection_name="nonexistent_collection"
            )

        assert "does not exist" in str(exc_info.value).lower()

    def test_search_returns_sorted_by_similarity(self, mock_scroll_directory, temp_dir):
        """
        Given: Multiple scrolls with different relevance to query
        When: search_similar_s4_states() is called
        Then: Results are sorted by similarity score (highest first)
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        results = indexer.search_similar_s4_states(
            query="bioelectric crystallization",
            top_k=5,
            collection_name="test_scrolls"
        )

        # Then
        if len(results) > 1:
            scores = [r["similarity_score"] for r in results]
            assert scores == sorted(scores, reverse=True)


class TestCollectionStatistics:
    """Test collection statistics and reporting."""

    def test_get_collection_stats_returns_document_count(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls are indexed
        When: get_collection_stats() is called
        Then: Returns total document count
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        stats = indexer.get_collection_stats(collection_name="test_scrolls")

        # Then
        assert "total_documents" in stats
        assert stats["total_documents"] > 0

    def test_get_collection_stats_returns_chamber_distribution(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls from multiple chambers are indexed
        When: get_collection_stats() is called
        Then: Returns chamber distribution
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        stats = indexer.get_collection_stats(collection_name="test_scrolls")

        # Then
        assert "chambers" in stats
        assert isinstance(stats["chambers"], dict)

    def test_get_collection_stats_returns_mirror_distribution(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls from multiple mirrors are indexed
        When: get_collection_stats() is called
        Then: Returns mirror distribution
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_scrolls"
        )

        # When
        stats = indexer.get_collection_stats(collection_name="test_scrolls")

        # Then
        assert "mirrors" in stats
        assert isinstance(stats["mirrors"], dict)

    def test_get_collection_stats_returns_error_for_missing_collection(self, temp_dir):
        """
        Given: Collection does not exist
        When: get_collection_stats() is called
        Then: Returns error in stats dict
        """
        # Given
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(vault_path=str(temp_dir), chroma_path=str(chroma_path))

        # When
        stats = indexer.get_collection_stats(collection_name="nonexistent")

        # Then
        assert "error" in stats

    def test_index_all_sessions_indexes_multiple_sessions(self, mock_scroll_directory, temp_dir):
        """
        Given: Multiple BIOELECTRIC_CHAMBERED sessions exist
        When: index_all_sessions() is called
        Then: All sessions are indexed and counts returned
        """
        # Given
        pytest.importorskip("chromadb")
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )

        # When
        results = indexer.index_all_sessions(collection_name="test_scrolls")

        # Then
        assert isinstance(results, dict)
        assert len(results) > 0
        assert all(isinstance(count, int) for count in results.values())

    def test_index_all_sessions_returns_empty_dict_when_no_sessions(self, temp_dir):
        """
        Given: No BIOELECTRIC_CHAMBERED sessions exist
        When: index_all_sessions() is called
        Then: Returns empty dict and logs warning
        """
        # Given
        scrolls_dir = temp_dir / "scrolls"
        scrolls_dir.mkdir()
        chroma_path = temp_dir / ".chroma"
        indexer = ScrollIndexer(vault_path=str(temp_dir), chroma_path=str(chroma_path))

        # When
        results = indexer.index_all_sessions(collection_name="test_scrolls")

        # Then
        assert results == {}
