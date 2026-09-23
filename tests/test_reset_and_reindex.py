from services.indexing_service import IndexingService


def main():

    print("=" * 60)
    print("RESET + REINDEX TEST")
    print("=" * 60)

    service = IndexingService()

    # --------------------------------------------------
    # RESET COLLECTION
    # --------------------------------------------------

    print("\n[1] Resetting ChromaDB collection...")

    service.index_manager.reset_collection()

    print("Collection reset successfully.")

    # --------------------------------------------------
    # REINDEX LOCAL KNOWLEDGE BASE
    # --------------------------------------------------

    print("\n[2] Re-indexing local knowledge base...")

    service.index_directory("data/raw")

    print("\n" + "=" * 60)
    print("RESET + REINDEX COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
