from datetime import datetime

def fmt_date(val):
    if val is None:
        return ''
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d')
    return str(val)[:10]

def safe_str(val, length=0):
    if val is None:
        return ''
    s = str(val)
    return s[:length] if length else s
