from services.indexing_service import IndexingService


def main():

    service = IndexingService()

    # Optional during development:
    # service.index_manager.reset_collection()

    service.index_directory("data/raw")


if __name__ == "__main__":
    main()