#!/usr/bin/env python3
"""
IRIS Scroll Archive ChromaDB Indexer

Embeds IRIS scroll archives into ChromaDB for semantic search and S4 state retrieval.
Supports indexing sessions, searching by semantic similarity, and filtering by metadata.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from tqdm import tqdm


class ScrollIndexer:
    """Manages ChromaDB indexing and search for IRIS scroll archives."""

    def __init__(self, vault_path: str = "iris_vault", chroma_path: str = None):
        """
        Initialize the scroll indexer.

        Args:
            vault_path: Path to the IRIS vault directory
            chroma_path: Path to ChromaDB persistent storage (default: vault_path/.chroma)
        """
        self.vault_path = Path(vault_path)
        self.scrolls_path = self.vault_path / "scrolls"

        if chroma_path is None:
            chroma_path = str(self.vault_path / ".chroma")

        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

    def _parse_scroll_metadata(self, scroll_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse metadata from a scroll markdown file.

        Args:
            scroll_path: Path to the scroll markdown file

        Returns:
            Dictionary containing parsed metadata, or None if parsing fails
        """
        try:
            content = scroll_path.read_text(encoding="utf-8")

            metadata = {}

            # Extract session ID from header
            session_match = re.search(r"\*\*Session:\*\*\s+(\S+)", content)
            if session_match:
                metadata["session_id"] = session_match.group(1)

            # Extract mirror (model)
            mirror_match = re.search(r"\*\*Mirror:\*\*\s+(.+?)(?:\n|$)", content)
            if mirror_match:
                metadata["mirror"] = mirror_match.group(1).strip()

            # Extract chamber
            chamber_match = re.search(r"\*\*Chamber:\*\*\s+(\S+)", content)
            if chamber_match:
                metadata["chamber"] = chamber_match.group(1)

            # Extract timestamp
            timestamp_match = re.search(r"\*\*Timestamp:\*\*\s+(.+?)(?:\n|$)", content)
            if timestamp_match:
                metadata["timestamp"] = timestamp_match.group(1).strip()

            # Extract felt pressure
            pressure_match = re.search(r"\*\*Felt Pressure:\*\*\s+(\d+)/5", content)
            if pressure_match:
                metadata["pressure"] = float(pressure_match.group(1))

            # Extract seal
            seal_match = re.search(r"\*\*Seal:\*\*\s+`?([a-f0-9]+)`?", content)
            if seal_match:
                metadata["seal"] = seal_match.group(1)

            # Extract turn number from filename
            turn_match = re.search(r"turn_(\d+)\.md$", scroll_path.name)
            if turn_match:
                metadata["turn"] = int(turn_match.group(1))

            # Extract living scroll content
            living_scroll_match = re.search(
                r"\*\*Living Scroll\*\*\s*\n+(.*?)(?=\n\*\*Technical Translation\*\*|\n\*\*Seal:\*\*|$)",
                content,
                re.DOTALL,
            )
            if living_scroll_match:
                metadata["living_scroll"] = living_scroll_match.group(1).strip()

            # Extract technical translation
            tech_trans_match = re.search(
                r"\*\*Technical Translation\*\*\s*\n+(.*?)(?=\n\*\*Seal:\*\*|\n†⟡∞|$)",
                content,
                re.DOTALL,
            )
            if tech_trans_match:
                metadata["technical_translation"] = tech_trans_match.group(1).strip()

            # Calculate convergence score from technical translation if present
            if "technical_translation" in metadata:
                # Look for convergence-related keywords
                tech_text = metadata["technical_translation"].lower()
                convergence_keywords = [
                    "convergence",
                    "stable",
                    "coherent",
                    "sealed",
                    "crystallization",
                ]
                convergence_score = sum(
                    1 for kw in convergence_keywords if kw in tech_text
                ) / len(convergence_keywords)
                metadata["convergence_score"] = round(convergence_score, 3)

            return metadata

        except Exception as e:
            print(f"Error parsing {scroll_path}: {e}", file=sys.stderr)
            return None

    def _create_embedding_text(self, metadata: Dict[str, Any]) -> str:
        """
        Create rich text for embedding from scroll metadata.

        Args:
            metadata: Scroll metadata dictionary

        Returns:
            Concatenated text for embedding
        """
        parts = []

        # Add chamber context
        if "chamber" in metadata:
            parts.append(f"Chamber: {metadata['chamber']}")

        # Add living scroll (primary phenomenological content)
        if "living_scroll" in metadata:
            parts.append(f"Living Scroll: {metadata['living_scroll']}")

        # Add technical translation (analytical content)
        if "technical_translation" in metadata:
            parts.append(f"Technical Translation: {metadata['technical_translation']}")

        return "\n\n".join(parts)

    def embed_scroll_archive(
        self, session_id: str, collection_name: str = "iris_scrolls"
    ) -> int:
        """
        Embed all scrolls from a specific session into ChromaDB.

        Args:
            session_id: Session ID to index (e.g., "BIOELECTRIC_CHAMBERED_20251001054935")
            collection_name: Name of the ChromaDB collection

        Returns:
            Number of scrolls indexed

        Raises:
            ValueError: If session directory does not exist
        """
        session_path = self.scrolls_path / session_id

        if not session_path.exists():
            raise ValueError(f"Session directory not found: {session_path}")

        # Get or create collection
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "IRIS scroll archives with semantic embeddings"},
        )

        # Find all scroll markdown files
        scroll_files = list(session_path.rglob("turn_*.md"))

        if not scroll_files:
            print(f"No scroll files found in {session_path}", file=sys.stderr)
            return 0

        indexed_count = 0

        # Process scrolls with progress bar
        for scroll_path in tqdm(
            scroll_files, desc=f"Indexing {session_id}", unit="scroll"
        ):
            metadata = self._parse_scroll_metadata(scroll_path)

            if not metadata:
                continue

            # Ensure session_id is set
            if "session_id" not in metadata:
                metadata["session_id"] = session_id

            # Create embedding text
            embedding_text = self._create_embedding_text(metadata)

            if not embedding_text:
                continue

            # Generate unique document ID
            doc_id = f"{session_id}_{metadata.get('mirror', 'unknown')}_{metadata.get('chamber', 'unknown')}_turn_{metadata.get('turn', 0):03d}"

            # Prepare metadata for ChromaDB (must be strings, ints, or floats)
            chroma_metadata = {
                "session_id": metadata.get("session_id", ""),
                "chamber": metadata.get("chamber", ""),
                "mirror": metadata.get("mirror", ""),
                "turn": metadata.get("turn", 0),
                "pressure": metadata.get("pressure", 0.0),
                "timestamp": metadata.get("timestamp", ""),
                "seal": metadata.get("seal", ""),
                "convergence_score": metadata.get("convergence_score", 0.0),
                "file_path": str(scroll_path),
            }

            # Add to collection
            collection.add(
                documents=[embedding_text], metadatas=[chroma_metadata], ids=[doc_id]
            )

            indexed_count += 1

        return indexed_count

    def search_similar_s4_states(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        collection_name: str = "iris_scrolls",
    ) -> List[Dict[str, Any]]:
        """
        Search for similar S4 states using semantic search.

        Args:
            query: Natural language query or description of desired state
            top_k: Number of results to return
            filters: Optional metadata filters (e.g., {"chamber": "S4", "mirror": "anthropic_claude-sonnet-4.5"})
            collection_name: Name of the ChromaDB collection

        Returns:
            List of matching scrolls with metadata and similarity scores

        Raises:
            ValueError: If collection does not exist
        """
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            raise ValueError(
                f"Collection '{collection_name}' does not exist. Run indexing first."
            )

        # Build where filter for ChromaDB
        where_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == "convergence_threshold":
                    # Special handling for convergence threshold
                    conditions.append({"convergence_score": {"$gte": value}})
                else:
                    conditions.append({key: value})

            # Use $and for multiple conditions, single condition otherwise
            if len(conditions) > 1:
                where_filter = {"$and": conditions}
            elif len(conditions) == 1:
                where_filter = conditions[0]

        # Perform semantic search
        results = collection.query(
            query_texts=[query], n_results=top_k, where=where_filter
        )

        # Format results
        formatted_results = []

        for i in range(len(results["ids"][0])):
            # ChromaDB uses L2 distance by default (smaller = more similar)
            # Convert to similarity score: use inverse (1 / (1 + distance))
            # This maps distance 0 -> similarity 1.0, larger distances -> smaller similarities
            distance = results["distances"][0][i]
            similarity = 1.0 / (1.0 + distance)

            result = {
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": distance,
                "similarity_score": similarity,
            }
            formatted_results.append(result)

        return formatted_results

    def index_all_sessions(
        self, collection_name: str = "iris_scrolls"
    ) -> Dict[str, int]:
        """
        Index all BIOELECTRIC_CHAMBERED sessions in the vault.

        Args:
            collection_name: Name of the ChromaDB collection

        Returns:
            Dictionary mapping session_id to number of scrolls indexed
        """
        if not self.scrolls_path.exists():
            raise ValueError(f"Scrolls directory not found: {self.scrolls_path}")

        # Find all BIOELECTRIC_CHAMBERED session directories
        session_dirs = [
            d
            for d in self.scrolls_path.iterdir()
            if d.is_dir() and d.name.startswith("BIOELECTRIC_CHAMBERED_")
        ]

        if not session_dirs:
            print(
                f"No BIOELECTRIC_CHAMBERED sessions found in {self.scrolls_path}",
                file=sys.stderr,
            )
            return {}

        results = {}

        print(f"\nIndexing {len(session_dirs)} sessions...")
        for session_dir in session_dirs:
            session_id = session_dir.name
            count = self.embed_scroll_archive(session_id, collection_name)
            results[session_id] = count
            print(f"  ✓ {session_id}: {count} scrolls indexed")

        return results

    def get_collection_stats(
        self, collection_name: str = "iris_scrolls"
    ) -> Dict[str, Any]:
        """
        Get statistics about the indexed collection.

        Args:
            collection_name: Name of the ChromaDB collection

        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            return {"error": "Collection does not exist"}

        stats = {
            "total_documents": collection.count(),
            "collection_name": collection_name,
        }

        # Get chamber distribution
        all_docs = collection.get()

        if all_docs["metadatas"]:
            chamber_counts = defaultdict(int)
            mirror_counts = defaultdict(int)
            session_counts = defaultdict(int)

            for metadata in all_docs["metadatas"]:
                chamber_counts[metadata.get("chamber", "unknown")] += 1
                mirror_counts[metadata.get("mirror", "unknown")] += 1
                session_counts[metadata.get("session_id", "unknown")] += 1

            stats["chambers"] = dict(chamber_counts)
            stats["mirrors"] = dict(mirror_counts)
            stats["sessions"] = dict(session_counts)

        return stats


def main():
    """CLI entry point for scroll indexing."""
    parser = argparse.ArgumentParser(
        description="Index IRIS scroll archives into ChromaDB for semantic search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index a specific session
  %(prog)s --session BIOELECTRIC_CHAMBERED_20251001054935

  # Index all sessions
  %(prog)s --all

  # Search for S4 states with concentric rings
  %(prog)s --search "concentric rings with high convergence" --chamber S4

  # Get collection statistics
  %(prog)s --stats
        """,
    )

    parser.add_argument(
        "--session",
        type=str,
        help="Index specific session ID (e.g., BIOELECTRIC_CHAMBERED_20251001054935)",
    )

    parser.add_argument(
        "--all", action="store_true", help="Index all BIOELECTRIC_CHAMBERED sessions"
    )

    parser.add_argument(
        "--search", type=str, help="Search query for semantic similarity"
    )

    parser.add_argument(
        "--chamber",
        type=str,
        choices=["S1", "S2", "S3", "S4"],
        help="Filter by specific chamber",
    )

    parser.add_argument("--mirror", type=str, help="Filter by specific mirror (model)")

    parser.add_argument(
        "--convergence",
        type=float,
        help="Filter by minimum convergence score (0.0-1.0)",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of search results to return (default: 10)",
    )

    parser.add_argument(
        "--stats", action="store_true", help="Display collection statistics"
    )

    parser.add_argument(
        "--vault",
        type=str,
        default="iris_vault",
        help="Path to IRIS vault directory (default: iris_vault)",
    )

    parser.add_argument(
        "--collection",
        type=str,
        default="iris_scrolls",
        help="ChromaDB collection name (default: iris_scrolls)",
    )

    args = parser.parse_args()

    # Initialize indexer
    try:
        indexer = ScrollIndexer(vault_path=args.vault)
    except Exception as e:
        print(f"Error initializing indexer: {e}", file=sys.stderr)
        return 1

    # Handle stats display
    if args.stats:
        stats = indexer.get_collection_stats(args.collection)
        print("\n=== Collection Statistics ===")
        print(json.dumps(stats, indent=2))
        return 0

    # Handle search
    if args.search:
        filters = {}

        if args.chamber:
            filters["chamber"] = args.chamber

        if args.mirror:
            filters["mirror"] = args.mirror

        if args.convergence is not None:
            filters["convergence_threshold"] = args.convergence

        try:
            results = indexer.search_similar_s4_states(
                query=args.search,
                top_k=args.top_k,
                filters=filters if filters else None,
                collection_name=args.collection,
            )

            print(f"\n=== Search Results (top {len(results)}) ===")
            print(f"Query: {args.search}")
            if filters:
                print(f"Filters: {filters}")
            print()

            for i, result in enumerate(results, 1):
                print(f"{i}. Similarity: {result['similarity_score']:.3f}")
                print(f"   ID: {result['id']}")
                print(f"   Chamber: {result['metadata'].get('chamber', 'N/A')}")
                print(f"   Mirror: {result['metadata'].get('mirror', 'N/A')}")
                print(f"   Turn: {result['metadata'].get('turn', 'N/A')}")
                print(
                    f"   Convergence: {result['metadata'].get('convergence_score', 'N/A')}"
                )
                print(f"   Pressure: {result['metadata'].get('pressure', 'N/A')}/5")
                print(f"   Document preview: {result['document'][:200]}...")
                print()

            return 0

        except Exception as e:
            print(f"Error searching: {e}", file=sys.stderr)
            return 1

    # Handle indexing
    if args.session:
        try:
            count = indexer.embed_scroll_archive(args.session, args.collection)
            print(f"\n✓ Successfully indexed {count} scrolls from {args.session}")

            # Show stats
            stats = indexer.get_collection_stats(args.collection)
            print(f"\nTotal documents in collection: {stats.get('total_documents', 0)}")

            return 0

        except Exception as e:
            print(f"Error indexing session: {e}", file=sys.stderr)
            return 1

    elif args.all:
        try:
            results = indexer.index_all_sessions(args.collection)

            total = sum(results.values())
            print(
                f"\n✓ Successfully indexed {total} scrolls across {len(results)} sessions"
            )

            # Show stats
            stats = indexer.get_collection_stats(args.collection)
            print("\n=== Collection Statistics ===")
            print(json.dumps(stats, indent=2))

            return 0

        except Exception as e:
            print(f"Error indexing sessions: {e}", file=sys.stderr)
            return 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
