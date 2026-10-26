from pathlib import Path
import re

root = Path(".")

print("=== DATABASE CONNECTIONS ===")
for path in sorted(Path("src/ingestion").glob("*.py")):
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = re.findall(r"duckdb\.connect\s*\((.*?)\)", text, re.S)
    if matches:
        print(f"\n{path}")
        for match in matches:
            print("  duckdb.connect(", " ".join(match.split()), ")")

print("\n=== SQL REFERENCES ===")
for path in sorted(Path("src/ingestion").glob("build_*.py")):
    text = path.read_text(encoding="utf-8", errors="replace")
    sql_refs = sorted(set(re.findall(
        r"""["']([^"']*sql/[^"']*\.sql)["']""", text
    )))
    print(f"\n{path}")
    print("  " + (", ".join(sql_refs) if sql_refs else "No literal SQL path detected"))

print("\n=== DEPENDENCY / CONFIG FILES ===")
for name in [
    "requirements.txt", "pyproject.toml", "uv.lock",
    ".env.example", "AI_USAGE.md", "metric_dictionary.md"
]:
    print(f"{name}: {'present' if (root / name).exists() else 'missing'}")
