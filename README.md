# AI Hackathon Starter Kit

Complete RAG-based chatbot skeleton ready for any AI use case.

## Quick Start

\\\ash
# Clone and setup
git clone https://github.com/rathamit-web/AI-Hackathon.git
cd AI-Hackathon
cp .env.example .env
python -m pip install -r requirements.txt

# Add your domain docs to data/kb/
# Then index
python src/main.py --index --kb-dir data/kb

# Process tasks
python src/main.py --process-csv data/samples/sample_input.csv --schema classification
\\\

## What's Included

- ✅ RAG Pipeline (LangChain + Chroma + Ollama)
- ✅ Chunking with overlap
- ✅ CSV/JSON/PDF/TXT input support
- ✅ Prompt library with 5+ schemas
- ✅ Evaluation framework
- ✅ Metrics & baseline comparison
- ✅ VS Code debug configs

See \docs/README.md\ for full documentation.
