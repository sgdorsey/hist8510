"""
01_build_db.py  —  Build the database from the schema and the seed CSVs
HIST 8510  ·  Week 2  ·  Database Design

This script is deliberately thin. It does four things:

    1. opens a connection and turns foreign key enforcement ON
    2. runs 01_create_schema.sql
    3. loads the four seed CSVs
    4. prints what it built so you can see it worked

All the interesting decisions live in 01_create_schema.sql, not here. The
schema is the argument; this file is the plumbing that runs it.

That split is not just tidiness. In three weeks you will meet the same
pattern in the Flask tutorial, which keeps a schema.sql next to the app
and runs it with executescript() exactly like this.

Run it with:  python3 01_build_db.py
Start over with:  python3 00_reset.py
"""

import csv
import os
import sqlite3

DB_FILE = "sc_guides.db"
SCHEMA_FILE = "01_create_schema.sql"

# (csv path, table name, column names) — loaded in this order so that
# foreign keys always point at rows that already exist.
SEED_FILES = [
    ("seed/cities.csv", "cities",
     ["city_id", "city_name", "state"]),
    ("seed/venue_types.csv", "venue_types",
     ["type_id", "type_label"]),
    ("seed/venues.csv", "venues",
     ["venue_id", "title", "year", "source_id",
      "street_address", "description", "city_id"]),
    ("seed/venue_type_link.csv", "venue_type_link",
     ["venue_id", "type_id"]),
]


def main():
    print("=== Building the South Carolina guides database ===")

    # Step 0 ------------------------------------------------ refuse to clobber
    # If a database is already here, stop. Rebuilding would silently throw
    # away anything you added by hand, which is a bad surprise mid-class.
    if os.path.exists(DB_FILE):
        print(f"\n{DB_FILE} already exists.")
        print("Run  python3 00_reset.py  first if you want to start over.")
        return

    if not os.path.exists(SCHEMA_FILE):
        raise SystemExit(f"Cannot find {SCHEMA_FILE}. It should sit beside this script.")

    # Step 1 ---------------------------------------------------- connect
    print("\nStep 1: Connecting...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f"  Connected to {DB_FILE}")

    # This is the line people forget. Without it, every FOREIGN KEY in the
    # schema is decorative: bad inserts succeed and nothing warns you.
    # It has to be set on every connection, because it is a property of
    # the session and not of the file.
    cursor.execute("PRAGMA foreign_keys = ON")
    enforcing = cursor.execute("PRAGMA foreign_keys").fetchone()[0]
    print(f"  Foreign key enforcement: {'ON' if enforcing else 'OFF'}")

    # Step 2 ----------------------------------------------- run the schema
    # executescript() runs a whole file of SQL in one go. It is the same
    # call the Flask tutorial uses to set up its database.
    print(f"\nStep 2: Running {SCHEMA_FILE}...")
    with open(SCHEMA_FILE, encoding="utf-8") as f:
        cursor.executescript(f.read())
    print("  Created: cities, venue_types, venues, venue_type_link")

    # executescript() commits and then opens a new transaction, and on some
    # versions it resets the pragma. Set it again so the seed load below is
    # genuinely checked against the foreign keys.
    cursor.execute("PRAGMA foreign_keys = ON")

    # Step 3 ------------------------------------------------ load the seeds
    print("\nStep 3: Loading seed data...")
    for path, table, columns in SEED_FILES:
        if not os.path.exists(path):
            raise SystemExit(f"Cannot find {path}. Did you move the seed/ folder?")
        with open(path, encoding="utf-8") as f:
            rows = [[r[c] for c in columns] for r in csv.DictReader(f)]

        placeholders = ", ".join("?" for _ in columns)
        cursor.executemany(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            rows,
        )
        print(f"  {table:<16} {len(rows):>4} rows")

    conn.commit()

    # Step 4 ------------------------------------------------------- verify
    # A quick join, both to prove the relationships work and to show what
    # the junction table bought us.
    print("\nStep 4: Checking that the relationships hold...")
    sample = cursor.execute("""
        SELECT  v.year,
                v.title,
                c.city_name,
                GROUP_CONCAT(t.type_label, ' + ') AS types
        FROM venues v
        JOIN cities c            ON v.city_id = c.city_id
        JOIN venue_type_link l   ON v.venue_id = l.venue_id
        JOIN venue_types t       ON l.type_id = t.type_id
        WHERE v.title = 'Bushwacker''s Pub'
        GROUP BY v.venue_id
        ORDER BY v.year
    """).fetchall()

    print("\n  Bushwacker's Pub, Greenville, across the guide years:")
    for year, title, city, types in sample:
        print(f"    {year}   {types}")

    orphans = cursor.execute("""
        SELECT COUNT(*) FROM venues v
        LEFT JOIN cities c ON v.city_id = c.city_id
        WHERE c.city_id IS NULL
    """).fetchone()[0]
    print(f"\n  Venues pointing at a city that does not exist: {orphans}")

    conn.close()
    print("\n=== Done. Open sc_guides.db in DBcode and look around. ===")


if __name__ == "__main__":
    main()
