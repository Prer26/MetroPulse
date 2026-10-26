from pathlib import Path

root = Path(".")
sql_files = sorted(Path("sql").rglob("*.sql"))

build_files = sorted(
    p for p in root.rglob("*.py")
    if p.name.startswith("build_")
    and not any(part in {".venv", "venv", "__pycache__"} for part in p.parts)
)

lines = [
    "# SQL Transformation Inventory",
    "",
    f"- SQL files discovered: **{len(sql_files)}**",
    f"- Build scripts discovered: **{len(build_files)}**",
    "",
    "A file count alone does not prove that every SQL file is an independent, "
    "successfully executed transformation. Pair each transformation with its "
    "build script and verify its output.",
    "",
    "## SQL files",
    "",
]

for path in sql_files:
    lines.append(f"- `{path.as_posix()}`")

lines += ["", "## Build scripts", ""]
for path in build_files:
    lines.append(f"- `{path.as_posix()}`")

lines += [
    "",
    "## Verification checklist",
    "",
    "- [ ] At least 12 meaningful SQL transformations are documented.",
    "- [ ] Each transformation has a documented input and output.",
    "- [ ] The build process runs successfully and can be repeated.",
    "- [ ] Joins and aggregations are checked for double counting.",
    "- [ ] Relevant tests and reconciliation checks pass.",
    "",
]

Path("docs").mkdir(exist_ok=True)
Path("docs/sql_transformation_inventory.md").write_text(
    "\n".join(lines), encoding="utf-8"
)

print("Updated docs/sql_transformation_inventory.md")
print(f"SQL files: {len(sql_files)}")
print(f"Build scripts: {len(build_files)}")
print("\nBuild scripts found:")
for path in build_files:
    print(" -", path.as_posix())
