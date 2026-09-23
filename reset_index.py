from vectorstore.index_manager import IndexManager


def main():

    manager = IndexManager()

    print(f"Before reset: {manager.count()} vectors")

    manager.reset_collection()

    print(f"After reset: {manager.count()} vectors")


if __name__ == "__main__":
    main()
