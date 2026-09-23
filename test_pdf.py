from ingestion.loader_factory import LoaderFactory

loader = LoaderFactory.get_loader(
    "data/raw/sample.txt")

print(type(loader).__name__)