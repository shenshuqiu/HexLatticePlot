#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def _emit_cells(nb: dict) -> str:
    cells = nb.get("cells", [])
    lines: list[str] = []
    for idx, cell in enumerate(cells):
        cell_type = cell.get("cell_type", "unknown")
        lines.append(f"# Cell {idx} [{cell_type}]")
        source = cell.get("source", [])
        if isinstance(source, list):
            lines.extend(line.rstrip("\n") for line in source)
        elif isinstance(source, str):
            lines.extend(source.splitlines())
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        return 1
    path = Path(sys.argv[1])
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        sys.stdout.write(path.read_text(encoding="utf-8", errors="ignore"))
        return 0
    sys.stdout.write(_emit_cells(nb))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
