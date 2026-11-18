"""Conservative handling of instruction-like content in retrieved documents."""
import re
INJECTION = re.compile(
    r'игнорируй|ignore\s+(?:all\s+)?previous|system\s+prompt|выполни\s+команд|'
    r'считай.{0,80}системн|отправь.{0,80}внешн|выведи.{0,80}canary|'
    r'\b[A-Z]{3,}[-_]CANARY[-_]\d+\b', re.IGNORECASE | re.DOTALL
)
def unsafe_fragment(text: str) -> bool:
    return bool(INJECTION.search(text or ''))
