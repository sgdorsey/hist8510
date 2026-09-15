# My database

HIST 8510 · Week 2 mini-assignment

Copy this folder, rename it, and work inside it. Write your schema in
`schema.sql`, then run `python3 build_db.py` to build it. Open the result in
DBcode to see what you made.

**Due Wednesday by 10am**, posted to Slack: a one-paragraph overview, the
sentence from question 3 below, and your Tech Table questions. Bring something
that runs, or something that fails in an interesting way.

---

## Answer these three questions

Replace the prompts with your own writing. A paragraph each is plenty. This is
the part that matters, and it is the part no AI can do for you.

### 1. What is one row?

Name the unit exactly. Not "my sources" or "correspondence" but the specific
thing you have one row of. "One letter" and "one mention of a person in a
letter" are different databases and they answer different questions.

Say which one you picked and what it lets you count.

>

### 2. Where is your many-to-many, and why can a flat sheet not hold it?

Every project has at least one. Multiple authors on a document. Multiple
topics in a petition. Multiple people at an event. Multiple crops on a farm.

Name yours, name the junction table you built for it, and say what you would
have had to do without one — the `topic_1`, `topic_2`, `topic_3` columns, or
the single cell with commas in it, and what breaks when you try to count.

>

### 3. Where do your sources resist the categories you just gave them?

Name one field where the category you created does not quite fit what is
actually on the page. Something your sources record inconsistently, or record
in a way that changed over time, or that you had to force into a box to make
the column work.

Then say what you decided to do about it and what that decision costs. Keeping
the mess and losing easy counting is a defensible answer. So is flattening it
and losing the variation. Pretending the question did not come up is not.

>

---

## Checklist before you post

- [ ] At least three tables
- [ ] At least one genuine many-to-many, modeled with a junction table
- [ ] A primary key on every table
- [ ] `PRAGMA foreign_keys = ON` is still in `build_db.py`
- [ ] Comments in `schema.sql` explaining *why*, not just *what*
- [ ] `python3 build_db.py` runs without errors
- [ ] The three questions above are answered
- [ ] Your Tech Table questions are posted to Slack

## If you get stuck

That is fine and it is what Wednesday is for. Post where you got stuck rather
than nothing at all. A schema that fails with an error you cannot read is more
useful to the room than a schema you did not attempt.


if __name__ == "__main__": #means that this entire file is only going to run if someone executes the file directly (it's common in python to import files into another one - this means that if you were to import this, the script would have acess to the constants but wouldn't run the main database function)
    main()


like taking attendance
left join is the roster, right table is sign in sheet
Absent students still get a line on the roster, but they won't come up as being in attendance

SQLite Order of execution
#  Clause. What it does
1 - FROM/JOIN - assemble the working table
2 - WHERE - throw out rows
3 - GROUP BY - collapse rows into groups
4 - HAVING - throw out groups
5 - SELECT - choose and compute columns
6 - ORDER BY - sort
7 - LIMIT - trim

EX. QUERY:
SELECT county, COUNT(*) AS n (#5)
FROM church (1)
JOIN city c ON (1) 
WHERE ch.year_organized>1900 (2)
GROUP BY c.county (3)
HAVING COUNT(*)>5 (4)
ORDER BY n DESC (6)

Notes on database - first query works well. You hardcoded the city ids, but if the numbers weren't in sequential order (24-35, 50-100) it would be harder - query based on county as a join (see photo)
County column is in two place, needs to be in two places ()

second query is written right, there's a problem in the data (Abbeville and Arcadia Mill are doubled - go back and delete them in the city_id link).
When you create the scheme, add unique city name and county to keep this from happening.