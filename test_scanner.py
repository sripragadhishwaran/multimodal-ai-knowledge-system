from ingestion.file_scanner import FileScanner

files = FileScanner.scan("data/raw")

print("Files Found:\n")

for file in files:
    print(file)