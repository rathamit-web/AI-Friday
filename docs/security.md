# Security & PII Handling

## Overview

This guide covers data privacy, PII detection/redaction, and secure practices for the RAG system.

## PII Detection & Redaction

The system automatically detects and can redact personally identifiable information.

### Automatic Detection

```python
from src.security import contains_pii, redact_pii

# Check for PII
text = "Contact John at john.doe@company.com or 555-123-4567"
findings = contains_pii(text)

# Output:
# {
#   'has_pii': True,
#   'email': ['john.doe@company.com'],
#   'phone': ['555-123-4567'],
#   'ssn': []
# }
```

### Automatic Redaction

```python
# Redact PII from text
original = "Email: jane@company.com, SSN: 123-45-6789"
redacted = redact_pii(original)

# Output: "Email: [EMAIL_REDACTED], SSN: [SSN_REDACTED]"
```

### Configuration

In `.env`:

```env
# Enable/disable PII detection
ENABLE_PII_DETECTION=true

# Choose which PII types to detect
REDACT_EMAIL=true
REDACT_PHONE=true
REDACT_SSN=true
```

### Detected Patterns

| Type | Pattern | Example |
|------|---------|---------|
| Email | `user@domain.com` | john.doe@company.com |
| Phone | `(123) 456-7890` | 555-123-4567, +1-555-123-4567 |
| SSN | `123-45-6789` | 123-45-6789 |

### Limitations

Current detection does NOT catch:
- Credit card numbers (can be added)
- Account numbers (can be added)
- Names (too context-dependent)
- Addresses (too context-dependent)

To extend detection, modify `src/security.py`:

```python
CREDIT_CARD_PATTERN = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'

def redact_pii(text: str) -> str:
    """Redact PII from text."""
    if ENABLE_PII_DETECTION:
        # ... existing code ...
        if REDACT_CREDIT_CARDS:
            text = re.sub(CREDIT_CARD_PATTERN, '[CREDIT_CARD_REDACTED]', text)
    return text
```

## Secrets Management

### Environment Variables

Never commit sensitive data. Use `.env` file:

```env
# ✅ Good - in .env (not in git)
OLLAMA_BASE_URL=http://localhost:11434
API_KEY=your_secret_key

# ❌ Bad - hardcoded in code
OLLAMA_BASE_URL = "http://localhost:11434"
```

### .gitignore

Ensure `.gitignore` includes:

```
.env
.env.local
*.log
__pycache__/
*.pyc
.vscode/settings.json
output/chroma_db/
*.db
```

### Secret Rotation

For production API keys:

```python
# Load from secure vault, not .env
import os
from pathlib import Path

def get_secret(key_name: str) -> str:
    """Get secret from environment or vault."""
    # Try environment first
    if value := os.getenv(key_name):
        return value
    
    # Try ~/.secrets/
    secret_file = Path.home() / '.secrets' / key_name
    if secret_file.exists():
        return secret_file.read_text().strip()
    
    raise ValueError(f"Secret not found: {key_name}")
```

## Knowledge Base Privacy

### Data Classification

When loading documents, classify sensitivity:

```python
DOCUMENT_CLASSIFICATION = {
    'public': 'Can be cached, displayed, shared',
    'internal': 'Restricted to team',
    'confidential': 'Encrypted, access-controlled',
    'sensitive': 'Redact before logging'
}
```

### Loading Sensitive Data

```python
from src.security import redact_pii
from src.data_loader import load_kb_directory

docs = load_kb_directory('data/kb')

# Redact PII before indexing
for doc in docs:
    doc['content'] = redact_pii(doc['content'])

# Index the redacted content
chunks = chunk_documents(docs)
vectorstore.add_documents_to_store(chunks)
```

### Logging Sensitive Data

Be careful what you log:

```python
from src.logging_config import logger
from src.security import redact_pii

# ✅ Good - redact before logging
query = user_input
logger.info(f"Processing query: {redact_pii(query)}")

# ❌ Bad - logs full query with PII
logger.info(f"Processing query: {query}")
```

## Data Privacy Best Practices

### 1. Minimize Data Collection
Only collect/store what you need:

```python
# ✅ Good - store only necessary fields
task = {
    'task_id': 'T001',
    'input': 'What is X?',
    'schema': 'qna'
}

# ❌ Bad - store unnecessary fields
task = {
    'task_id': 'T001',
    'user_email': 'user@company.com',
    'user_ip': '192.168.1.1',
    'input': 'What is X?',
    'timestamp': datetime.now()
}
```

### 2. Limit Retention
Delete old data:

```python
import os
from datetime import datetime, timedelta
from pathlib import Path

def cleanup_old_results(output_dir: str = 'output', days: int = 30):
    """Delete results older than N days."""
    cutoff = datetime.now() - timedelta(days=days)
    
    for file_path in Path(output_dir).glob('results_*.json'):
        if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff:
            file_path.unlink()
            print(f"Deleted: {file_path}")
```

### 3. Access Control
Restrict who can access what:

```python
# Pseudo-code for access control
def can_access_results(user_role: str, result_sensitivity: str) -> bool:
    """Check if user can access this result."""
    access_matrix = {
        'public': ['user', 'admin'],
        'internal': ['admin', 'manager'],
        'confidential': ['admin']
    }
    return user_role in access_matrix.get(result_sensitivity, [])
```

### 4. Data Anonymization
Remove identifying information when possible:

```python
import hashlib

def anonymize_id(user_id: str, salt: str = 'default') -> str:
    """Create non-reversible anonymized ID."""
    return hashlib.sha256(f"{user_id}{salt}".encode()).hexdigest()[:16]

# Usage:
user_id = "john_doe_123"
anon_id = anonymize_id(user_id)  # f3e4d1b2c5a8f9d6
```

### 5. Encryption
For sensitive storage:

```python
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    """Encrypt sensitive data."""
    cipher = Fernet(key)
    return cipher.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted: str, key: bytes) -> str:
    """Decrypt sensitive data."""
    cipher = Fernet(key)
    return cipher.decrypt(encrypted.encode()).decode()

# Generate key (store securely, not in code):
# key = Fernet.generate_key()
```

## Audit & Monitoring

### Audit Logging

Log sensitive operations:

```python
from datetime import datetime
import json

def audit_log(action: str, details: dict, level: str = 'INFO'):
    """Log security-relevant actions."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details,
        'level': level
    }
    
    logger.info(json.dumps(log_entry))

# Usage:
audit_log('kb_indexed', {'doc_count': 42, 'kb_dir': 'data/kb'})
audit_log('results_accessed', {'user': 'admin', 'result_id': 'R123'}, 'WARNING')
```

### Monitoring PII Detection

Track PII incidents:

```python
from collections import defaultdict

pii_stats = defaultdict(int)

def monitor_pii(text: str, doc_id: str):
    """Monitor and log PII findings."""
    findings = contains_pii(text)
    
    if findings['has_pii']:
        pii_stats['total_incidents'] += 1
        pii_stats['email_count'] += len(findings['email'])
        pii_stats['phone_count'] += len(findings['phone'])
        pii_stats['ssn_count'] += len(findings['ssn'])
        
        logger.warning(f"PII found in {doc_id}: {findings}")
        
        return True
    
    return False

# Usage:
for doc in documents:
    monitor_pii(doc['content'], doc['id'])

print(f"PII Stats: {dict(pii_stats)}")
```

## Compliance Considerations

### GDPR (EU)
- Right to be forgotten: Ability to delete user data
- Data minimization: Collect only necessary data
- Purpose limitation: Use data only for stated purpose
- Consent: Document consent for data use

### CCPA (California)
- Consumer right to know
- Consumer right to delete
- Consumer right to opt-out

### Implementation
```python
def delete_user_data(user_id: str):
    """Delete all data for user (GDPR compliance)."""
    # Find all results associated with user
    user_results = find_results_by_user(user_id)
    
    # Delete from vector DB
    for result_id in user_results:
        vectorstore.delete(result_id)
    
    # Delete from file system
    for result_file in Path('output').glob(f'*{user_id}*'):
        result_file.unlink()
    
    audit_log('user_data_deleted', {'user_id': user_id, 'count': len(user_results)})
```

## Security Checklist

Before deploying:

- [ ] `.env` file in `.gitignore`
- [ ] No secrets in code or logs
- [ ] PII detection enabled for user input
- [ ] Results encrypted before transmission
- [ ] Access control implemented
- [ ] Audit logging in place
- [ ] Data retention policy defined
- [ ] Regular security reviews scheduled
- [ ] Dependencies updated and patched
- [ ] Input validation on all endpoints

## Incident Response

If a security incident occurs:

1. **Identify**: What data was exposed?
2. **Isolate**: Stop the breach
3. **Notify**: Alert affected users
4. **Investigate**: Root cause analysis
5. **Document**: Create incident report
6. **Remediate**: Fix vulnerability
7. **Monitor**: Watch for recurrence

```python
def handle_security_incident(incident_type: str, details: dict):
    """Handle security incident."""
    logger.critical(f"SECURITY INCIDENT: {incident_type}")
    audit_log(incident_type, details, 'CRITICAL')
    
    # Take action based on incident type
    if incident_type == 'unauthorized_access':
        # Revoke access tokens
        # Lock accounts
        pass
    
    elif incident_type == 'data_breach':
        # Delete compromised data
        # Notify users
        pass
    
    # Create incident ticket
    create_incident_ticket(incident_type, details)
```

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GDPR Compliance](https://gdpr-info.eu/)
- [CCPA](https://oag.ca.gov/privacy/ccpa)
- [Cryptography Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
