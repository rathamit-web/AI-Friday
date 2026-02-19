import re
from src.config import ENABLE_PII_DETECTION, REDACT_EMAIL, REDACT_PHONE, REDACT_SSN

EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'\b(?:\+?1[-.]?)?(?:\([0-9]{3}\)|[0-9]{3})[-.]?[0-9]{3}[-.]?[0-9]{4}\b'
SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'

def redact_pii(text: str) -> str:
    """Redact personally identifiable information from text."""
    if not ENABLE_PII_DETECTION:
        return text
    
    if REDACT_EMAIL:
        text = re.sub(EMAIL_PATTERN, '[EMAIL_REDACTED]', text)
    if REDACT_PHONE:
        text = re.sub(PHONE_PATTERN, '[PHONE_REDACTED]', text)
    if REDACT_SSN:
        text = re.sub(SSN_PATTERN, '[SSN_REDACTED]', text)
    
    return text

def contains_pii(text: str) -> dict:
    """Check if text contains PII and return findings."""
    findings = {
        'has_pii': False,
        'email': [],
        'phone': [],
        'ssn': []
    }
    
    if ENABLE_PII_DETECTION:
        if REDACT_EMAIL:
            findings['email'] = re.findall(EMAIL_PATTERN, text)
        if REDACT_PHONE:
            findings['phone'] = re.findall(PHONE_PATTERN, text)
        if REDACT_SSN:
            findings['ssn'] = re.findall(SSN_PATTERN, text)
        
        findings['has_pii'] = bool(findings['email'] or findings['phone'] or findings['ssn'])
    
    return findings
