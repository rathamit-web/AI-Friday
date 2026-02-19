#!/usr/bin/env python
"""
Verification script to check if all components are ready for hackathon.
Run this to verify everything is working before Friday.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_mark(condition, message):
    """Print check mark or X based on condition."""
    if condition:
        print(f"{GREEN}✅{RESET} {message}")
        return True
    else:
        print(f"{RED}❌{RESET} {message}")
        return False

def print_section(title):
    """Print section header."""
    print(f"\n{YELLOW}{'=' * 60}{RESET}")
    print(f"{YELLOW}{title}{RESET}")
    print(f"{YELLOW}{'=' * 60}{RESET}\n")

def verify_structure():
    """Verify folder structure."""
    print_section("1. FOLDER STRUCTURE")
    
    required_dirs = [
        'src',
        'data/kb',
        'data/samples',
        'data/eval',
        'output/artifacts',
        'output/chroma_db',
        'docs',
        'tests',
        '.vscode'
    ]
    
    results = []
    for dir_path in required_dirs:
        exists = Path(dir_path).is_dir()
        results.append(check_mark(exists, f"Directory: {dir_path}"))
    
    return all(results)

def verify_files():
    """Verify critical files exist."""
    print_section("2. CRITICAL FILES")
    
    required_files = {
        'Core Configuration': [
            'requirements.txt',
            '.env.example',
            '.gitignore',
            'Makefile',
            'README.md'
        ],
        'Source Modules': [
            'src/__init__.py',
            'src/config.py',
            'src/logging_config.py',
            'src/security.py',
            'src/data_loader.py',
            'src/chunking.py',
            'src/embeddings.py',
            'src/vectorstore.py',
            'src/llm.py',
            'src/prompt_library.py',
            'src/schemas.py',
            'src/agent.py',
            'src/csv_processor.py',
            'src/main.py',
            'src/metrics.py',
            'src/metrics_report.py',
            'src/evaluate.py'
        ],
        'Documentation': [
            'docs/INDEX.md',
            'docs/pipeline.md',
            'docs/prompt-library.md',
            'docs/evaluation.md',
            'docs/coding-standards.md',
            'docs/security.md',
            'docs/slides.md',
            'QUICKSTART.md'
        ],
        'Tests': [
            'tests/__init__.py',
            'tests/test_basic.py'
        ],
        'Sample Data': [
            'data/kb/sample_kb.csv',
            'data/kb/sample_kb.txt',
            'data/samples/sample_input.csv',
            'data/samples/sample_task.json',
            'data/eval/sample_eval.jsonl'
        ],
        'VS Code Config': [
            '.vscode/tasks.json',
            '.vscode/launch.json'
        ]
    }
    
    all_exist = True
    for category, files in required_files.items():
        print(f"\n{category}:")
        for file_path in files:
            exists = Path(file_path).is_file()
            all_exist = all_exist and exists
            check_mark(exists, file_path)
    
    return all_exist

def verify_imports():
    """Verify critical imports work."""
    print_section("3. IMPORT VERIFICATION")
    
    imports_to_check = [
        ('src.config', 'Configuration module'),
        ('src.logging_config', 'Logging setup'),
        ('src.data_loader', 'Data loader'),
        ('src.chunking', 'Chunking'),
        ('src.embeddings', 'Embeddings'),
        ('src.vectorstore', 'Vector store'),
        ('src.llm', 'LLM wrapper'),
        ('src.prompt_library', 'Prompt library'),
        ('src.schemas', 'Schemas'),
        ('src.agent', 'Agent'),
        ('src.metrics', 'Metrics'),
        ('src.metrics_report', 'Metrics report'),
        ('src.main', 'Main CLI'),
    ]
    
    results = []
    for module_name, description in imports_to_check:
        try:
            __import__(module_name)
            results.append(check_mark(True, f"{description}: {module_name}"))
        except Exception as e:
            print(f"{RED}❌{RESET} {description}: {module_name}")
            print(f"   Error: {str(e)[:60]}")
            results.append(False)
    
    return all(results)

def verify_dependencies():
    """Check if required packages can be imported."""
    print_section("4. DEPENDENCY CHECK")
    
    dependencies = [
        ('langchain', 'LangChain'),
        ('langchain_community', 'LangChain Community'),
        ('chromadb', 'Chroma DB'),
        ('pydantic', 'Pydantic'),
        ('pdfplumber', 'PDF Plumber'),
        ('sklearn', 'scikit-learn'),
        ('rouge_score', 'ROUGE Score'),
        ('pytest', 'pytest'),
        ('dotenv', 'python-dotenv'),
        ('tqdm', 'tqdm'),
    ]
    
    results = []
    for package_name, description in dependencies:
        try:
            __import__(package_name)
            results.append(check_mark(True, f"{description}: {package_name}"))
        except ImportError:
            print(f"{RED}❌{RESET} {description}: {package_name} (not installed)")
            results.append(False)
    
    return all(results)

def verify_data():
    """Verify sample data exists and is readable."""
    print_section("5. SAMPLE DATA")
    
    data_files = {
        'data/kb/sample_kb.csv': 'CSV Knowledge Base',
        'data/kb/sample_kb.txt': 'Text Knowledge Base',
        'data/samples/sample_input.csv': 'Sample Input CSV',
        'data/samples/sample_task.json': 'Sample Task JSON',
        'data/eval/sample_eval.jsonl': 'Sample Evaluation Data',
    }
    
    results = []
    for file_path, description in data_files.items():
        try:
            path = Path(file_path)
            exists = path.is_file() and path.stat().st_size > 0
            results.append(check_mark(exists, f"{description}: {file_path} ({path.stat().st_size} bytes)"))
        except Exception as e:
            check_mark(False, f"{description}: {file_path}")
            results.append(False)
    
    return all(results)

def verify_env():
    """Verify .env.example exists and has required variables."""
    print_section("6. ENVIRONMENT CONFIGURATION")
    
    env_path = Path('.env.example')
    
    if not env_path.exists():
        check_mark(False, ".env.example file exists")
        return False
    
    check_mark(True, ".env.example file exists")
    
    required_vars = [
        'OLLAMA_MODEL',
        'OLLAMA_EMBEDDING_MODEL',
        'OLLAMA_BASE_URL',
        'LLM_TEMPERATURE',
        'CHUNK_SIZE',
        'RETRIEVAL_TOP_K',
        'VECTOR_DB_PATH',
    ]
    
    env_content = env_path.read_text()
    
    results = []
    for var in required_vars:
        has_var = var in env_content
        results.append(check_mark(has_var, f"Variable: {var}"))
    
    return all(results)

def verify_prompt_templates():
    """Verify all prompt templates are available."""
    print_section("7. PROMPT TEMPLATES")
    
    try:
        from src.prompt_library import list_available_schemas
        
        schemas = list_available_schemas()
        expected_schemas = [
            'generic_extraction',
            'classification',
            'qna',
            'summarization',
            'action_plan',
            'rag'
        ]
        
        results = []
        for schema in expected_schemas:
            results.append(check_mark(schema in schemas, f"Schema: {schema}"))
        
        return all(results)
    except Exception as e:
        print(f"{RED}❌{RESET} Failed to check prompt templates: {e}")
        return False

def verify_schemas():
    """Verify all Pydantic schemas are available."""
    print_section("8. PYDANTIC SCHEMAS")
    
    try:
        from src.schemas import SCHEMA_MODELS
        
        expected_schemas = [
            'generic_extraction',
            'classification',
            'qna',
            'summarization',
            'action_plan',
            'rag'
        ]
        
        results = []
        for schema in expected_schemas:
            exists = schema in SCHEMA_MODELS
            results.append(check_mark(exists, f"Model: {schema}"))
        
        return all(results)
    except Exception as e:
        print(f"{RED}❌{RESET} Failed to check Pydantic schemas: {e}")
        return False

def verify_git():
    """Verify git setup."""
    print_section("9. GIT CONFIGURATION")
    
    gitignore_path = Path('.gitignore')
    
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        has_env = '.env' in content
        has_pycache = '__pycache__' in content
        
        check_mark(True, ".gitignore exists")
        check_mark(has_env, ".gitignore includes .env")
        check_mark(has_pycache, ".gitignore includes __pycache__")
        
        return has_env and has_pycache
    else:
        check_mark(False, ".gitignore exists")
        return False

def main():
    """Run all verifications."""
    print(f"\n{YELLOW}{'#' * 60}{RESET}")
    print(f"{YELLOW}# RAG HACKATHON - PRE-FLIGHT VERIFICATION{RESET}")
    print(f"{YELLOW}# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{YELLOW}{'#' * 60}{RESET}\n")
    
    checks = [
        ('Folder Structure', verify_structure),
        ('Critical Files', verify_files),
        ('Import Verification', verify_imports),
        ('Dependencies', verify_dependencies),
        ('Sample Data', verify_data),
        ('Environment Config', verify_env),
        ('Prompt Templates', verify_prompt_templates),
        ('Pydantic Schemas', verify_schemas),
        ('Git Setup', verify_git),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n{RED}❌ {check_name} failed with error: {e}{RESET}")
            results[check_name] = False
      # Summary
    print_section("VERIFICATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status} {check_name}")
    
    print(f"\n{YELLOW}Overall: {passed}/{total} checks passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✅ ALL CHECKS PASSED - YOU'RE READY FOR FRIDAY!{RESET}\n")
        return 0
    else:
        print(f"\n{YELLOW}⚠️  {total - passed} checks need attention. Review errors above.{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
