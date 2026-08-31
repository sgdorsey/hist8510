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
