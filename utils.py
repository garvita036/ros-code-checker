from pathlib import Path

def read_file_safe(p: Path):
try:
return p.read_text(errors='ignore')
except Exception:
return
