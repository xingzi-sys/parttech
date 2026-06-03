from email_validator import validate_email, EmailNotValidError
import re

def validate_email_format(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_phone(phone):
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_credit_code(code):
    pattern = r'^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$'
    return bool(re.match(pattern, code))

def sanitize_input(text, max_length=500):
    if not text:
        return ''
    text = str(text).strip()[:max_length]
    return text