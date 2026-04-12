"""pytest configuration — adds scripts/ to sys.path for imports."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
