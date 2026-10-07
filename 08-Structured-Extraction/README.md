# Structured Extraction: From Images to CSV

## Setup

From inside the `08-Structured-Extraction` folder:

```bash
cp .env.example .env            # then paste your key into .env
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running it

```bash
source venv/bin/activate
python 01_directory_to_csv.py
python 02_census_to_csv.py
python 03_validate_census.py
```

The results go in `output/`:

```
output/directory.csv        one row per graduate
output/census.csv           one row per church
output/census_checked.csv   the census data plus the results of each check
```

You may see a warning that starts `Direct use of automatic function calling (AFC)...`.
It's harmless. Google's library prints it even though we aren't using that feature.

---

## How it works

1. **The codebook.** At the top of scripts 01 and 02, `FIELDS` lists every column with
   instructions for the model. This is where the historical decisions live: what counts as
   a separate field, what to keep exactly as printed, what to do with blanks.
2. **The schema.** `build_schema()` turns the codebook into a JSON schema. Gemini *must*
   answer in JSON with exactly those fields: no extra text, no missing columns.
3. **The CSV.** Python's `csv` module writes the file, so commas inside the data
   (`12 Vine St., Sharon, Pa.`) can't break the columns.
4. **Code does what code can do reliably.** The model reads the page. Code adds the image
   name and page number to each row, pulls the death year out of `Died 1898.`, and does the
   arithmetic checks.

**Every value is saved as text, exactly as written** (`"663.48"`, `"None"`, `"no"`).
Turning answers into numbers is an interpretation, so it happens in a separate step
(`to_number()` in script 03), where you can see and change the rules.

---

## Checking the results

**Directory:** script 01 prints how many entries it found on each page. **Count the entries
on the page yourself.** The most common failure with many records per page is a dropped or
merged row, and nothing else will catch it. The script also flags impossible years.

**Census:** the 1926 form has its own check printed on it ("The total given under Question 6
should be the same as the total of males and females given under Question 3"). Script 03
checks:

- Q1 + Q2 = Q3 (male + female = total members)
- Q3 = Q6 (both totals agree)
- Q4 + Q5 = Q6 (under 13 + 13 and over = total)
- Q13 + Q14 = Q15 (the expenditures add up)

A mismatch means one of three things: the model misread a number, the person filling out the
form made a mistake, or the form was corrected and the model picked the wrong value. Only
looking at the image tells you which.

---

## Things to try

- Add a column to a codebook. For example, the census form's Sunday school questions (16–17).
- Change an instruction. What happens if you drop "exactly as printed" from the `surname` field?
- Remove the `status` field from the directory codebook. Where do "Died" and "Address Unknown" end up?
- Put a census schedule where the totals *don't* add up in `images/census/` and run script 03.
