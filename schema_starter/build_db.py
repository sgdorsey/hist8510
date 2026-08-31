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


if __name__ == "__main__": #means that this entire file is only going to run if someone executes the file directly (it's common in python to import files into another one - this means that if you were to import this, the script would have acess to the constants but wouldn't run the main database function)
    main()
