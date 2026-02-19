.PHONY: install index run test clean

install:
python -m pip install -r requirements.txt

index:
python src/main.py --index --kb-dir data/kb

run:
python src/main.py --process data/samples/sample_task.json --schema generic_extraction

test:
python -m pytest -q tests/

clean:
Remove-Item -Recurse -Force output/chroma_db, output/artifacts
