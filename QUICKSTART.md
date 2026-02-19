# RAG Hackathon Starter Kit - Quick Start

## 📋 Friday Morning Checklist (7:00 AM - 8:00 AM)

Before the hackathon begins, run these commands to verify everything is ready:

```powershell
# 1. Install dependencies (5 min)
python -m pip install -r requirements.txt

# 2. Start Ollama (if not already running)
# Open separate terminal and run: ollama serve
# Then pull required models
ollama pull llama3.2
ollama pull gte-large

# 3. Index the sample knowledge base (2 min)
python src/main.py --index --kb-dir data/kb

# 4. Run a quick smoke test (2 min)
python src/main.py --process data/samples/sample_task.json --schema generic_extraction

# 5. Check output
ls output/
cat output/results.json
```

## ⚡ When You Get the Use Case (8:00 AM Onwards)

### Step 1: Add Your Domain Data (10-15 min)
```powershell
# Place your domain documents in data/kb/
# Supported formats: CSV, JSON, TXT, PDF

# Add sample data
Copy-Item "your_company_docs.pdf" "data/kb/"
Copy-Item "your_policies.csv" "data/kb/"
```

### Step 2: Re-index (5 min)
```powershell
# Re-index with your new data
python src/main.py --index --kb-dir data/kb

# This creates/updates the vector database in output/chroma_db/
```

### Step 3: Choose Your Schema and Test (10 min)
```powershell
# Available schemas:
# - classification (sentiment, categories)
# - generic_extraction (entities, facts)
# - qna (question answering)
# - summarization (text summaries)
# - action_plan (step-by-step procedures)

# Test with a quick query
python src/main.py --text "Your test query here" --schema classification

# Output goes to output/results.json
```

### Step 4: Batch Process Tasks (5-30 min)
```powershell
# Process CSV batch
python src/main.py --process-csv data/samples/your_tasks.csv --schema classification

# Process single JSON
python src/main.py --process data/samples/your_task.json --schema qna
```

### Step 5: Evaluate Results (5 min)
```powershell
python src/evaluate.py --results output/results.json --output-dir output

# View metrics
cat output/metrics_report.md
```

## 🔧 Common Commands Cheat Sheet

### Indexing
```powershell
# Full index from scratch
python src/main.py --index --kb-dir data/kb

# Clear and rebuild (if needed)
Remove-Item -Recurse -Force output/chroma_db
python src/main.py --index --kb-dir data/kb
```

### Processing
```powershell
# Single JSON task
python src/main.py --process data/samples/task.json --schema generic_extraction

# CSV batch
python src/main.py --process-csv data/samples/tasks.csv --schema classification

# Direct text query
python src/main.py --text "What is X?" --schema qna

# Without RAG (direct LLM)
python src/main.py --text "Query" --schema classification --no-rag
```

### Testing
```powershell
# Run tests
python -m pytest tests/ -v

# Quick import check
python -c "from src import config, agent, metrics; print('✅ All imports OK')"
```

### Evaluation
```powershell
# Generate metrics
python src/evaluate.py --results output/results.json

# View report
cat output/metrics_report.md
cat output/metrics.json
```

### Cleanup
```powershell
# Clean up results and vector DB
Remove-Item -Recurse -Force output/chroma_db
Remove-Item -Recurse -Force output/artifacts
Remove-Item output/*.json
```

## 🚨 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langchain'"
**Fix:**
```powershell
python -m pip install -r requirements.txt
```

### Issue: "Connection refused" when connecting to Ollama
**Fix:**
1. Check Ollama is running: `ollama serve` in a separate terminal
2. Verify OLLAMA_BASE_URL in `.env` is correct (default: http://localhost:11434)
3. Check firewall isn't blocking port 11434

### Issue: "Models not found" (llama3.2, gte-large)
**Fix:**
```powershell
ollama pull llama3.2
ollama pull gte-large
```

### Issue: Vector database corrupted
**Fix:**
```powershell
Remove-Item -Recurse -Force output/chroma_db
python src/main.py --index --kb-dir data/kb
```

### Issue: JSON parsing errors in output
**Fix:**
- Check LLM_TEMPERATURE=0.3 in `.env` (keeps outputs deterministic)
- Verify prompt template in `src/prompt_library.py`
- Test with simpler input first

### Issue: Out of memory
**Fix:**
- Reduce CHUNK_SIZE in `.env` (try 500)
- Reduce RETRIEVAL_TOP_K (try 3)
- Process smaller batches

### Issue: Slow performance
**Fix:**
- Use faster model: Set OLLAMA_MODEL=gemma in `.env`
- Reduce chunks: CHUNK_SIZE=500, CHUNK_OVERLAP=100
- Process in smaller batches

## 📊 What Each Output File Contains

- `output/results.json` - Main results from your tasks
- `output/metrics.json` - Quantitative metrics (schema pass rate, latency, etc.)
- `output/metrics_report.md` - Human-readable evaluation report
- `output/chroma_db/` - Vector database (don't modify directly)
- `output/app.log` - Debug logs

## ✅ Pre-Hackathon Verification

Before Friday 8 AM, verify:

```powershell
# 1. Python 3.8+ installed
python --version

# 2. Dependencies installable
python -m pip install -r requirements.txt

# 3. Ollama running
ollama list

# 4. Models available
ollama show llama3.2
ollama show gte-large

# 5. Test indexing
python src/main.py --index --kb-dir data/kb
ls output/chroma_db

# 6. Test basic query
python src/main.py --text "test" --schema classification
cat output/results.json
```

All ✅? You're ready for Friday!

## 🎯 Pro Tips for Hackathon Day

1. **Prep your prompts** - Edit `src/prompt_library.py` with domain-specific instructions
2. **Add example data early** - Having sample KB entries speeds up iteration
3. **Use classification schema first** - Good for initial exploration of any dataset
4. **Monitor metrics** - Run evaluation frequently to track quality
5. **Cache successful prompts** - Save working prompts to a file
6. **Batch process** - Use CSV batch processing for multiple tasks
7. **Check logs** - View `output/app.log` when debugging
8. **Test without RAG first** - Use `--no-rag` to test LLM alone
9. **Keep .env clean** - Backup working .env as .env.backup
10. **Git commit often** - Save working versions frequently

## 🏆 Evaluation Tips

To maximize your hackathon score:

- **Schema Pass Rate** >90%: Ensure JSON outputs are always valid
- **Latency** <5s per query: Use gte-large embeddings, chunk appropriately
- **Accuracy**: Provide high-quality knowledge base documents
- **Coverage**: Use RAG mode with retrieved context for best results
- **Documentation**: Generate metrics report to show your results

Good luck! 🚀
