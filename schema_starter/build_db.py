"""
build_db.py  —  Run your schema.sql and make a database out of it
HIST 8510  ·  Week 2 mini-assignment

You should not need to change much in here. Write your schema in
schema.sql; this file just runs it.

Run it with:  python3 build_db.py

It deletes and rebuilds the database every time, which is what you want
while you are still changing your schema. Once you start putting real
data in, take the delete out.
"""

import os
import sqlite3

DB_FILE = "my_database.db"       # rename this to something meaningful - this is a constant, which tells us about a variable
SCHEMA_FILE = "schema.sql"

# seed files: each line tells us where the csv is, what table it will go into, and the order of the columns - important - based on the foreign keys)
# cities table: city, primary key
# venues table: title, primary ID, city ID (foreign key)
# if you do the venue table first, it will get confused because there are no cities yet
# order of the columns matters much less

def main():
    # While you are drafting, starting fresh every run is the right
    # behavior — you will be changing the schema constantly and half-built
    # tables from a previous attempt cause confusing errors.
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed the old {DB_FILE}")
# this checks to see if the database already exists or is open, and if so, it quits it (if not, it would overwrite your data) - it's an if/else path
    print("\nStep 1: Connecting...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f" connected to {DB_FILE}")

    # Do not delete this line. Without it every FOREIGN KEY in your schema
    # is decorative, and you will be able to insert rows pointing at
    # records that do not exist without ever being told.
    cursor.execute("PRAGMA foreign_keys = ON")

    with open(SCHEMA_FILE, encoding="utf-8") as f:
        cursor.executescript(f.read())
    cursor.execute("PRAGMA foreign_keys = ON")   # executescript can reset it

    import csv
    SEED_FILES = [
        ("seed/city.csv", "city",
         ["city_id", "city_name", "county", "state"]),
        ("seed/people.csv", "people",
         ["people_id", "name", "type", "years_active"]),
        ("seed/church.csv", "church",
         ["church_id", "name_of_church", "year_organized", "county", "denomination", "property_value", "present_membership", "charter_membership", "city_id"]),
        ("seed/church_people.csv", "church_people",
         ["church_id", "people_id"]),
    ]

    for path, table, columns in SEED_FILES:
        with open(path, encoding="utf-8-sig") as f:   # utf-8-sig strips Excel's BOM
            # An empty cell becomes NULL, not the string "". That is what
            # lets a nullable INTEGER column stay genuinely empty.
            rows = [[(r[c] or None) for c in columns] for r in csv.DictReader(f)]
        placeholders = ", ".join("?" for _ in columns)
        cursor.executemany(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", rows
        )
        print(f"  loaded {table:<16} {len(rows):>4} rows")

    conn.commit()

    # Show what got built, so you can see your schema took effect.
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    print(f"\nBuilt {DB_FILE} with {len(tables)} tables:\n")
    for (name,) in tables:
        print(f"  {name}")
        for col in cursor.execute(f"PRAGMA table_info({name})").fetchall():
            pk = "  PRIMARY KEY" if col[5] else ""
            null = "  NOT NULL" if col[3] else ""
            print(f"      {col[1]:<20} {col[2] or '(no type)':<10}{pk}{null}")
        for fk in cursor.execute(f"PRAGMA foreign_key_list({name})").fetchall():
            print(f"      -> {fk[3]} references {fk[2]}({fk[4]})")
        print()

    conn.close()
    print("Open it in DBcode to look at what you just made.")


if __name__ == "__main__":
    main()


