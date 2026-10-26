
import duckdb

con = duckdb.connect("metropulse.duckdb", read_only=True)

tables = con.execute("SHOW TABLES").fetchall()

for (table,) in tables:
    print(f"\n{'=' * 50}")
    print(f"TABLE: {table}")
    print("=" * 50)

    columns = con.execute(
        f'DESCRIBE SELECT * FROM "{table}"'
    ).fetchall()

    for column in columns:
        print(f"{column[0]} ({column[1]})")

con.close()
