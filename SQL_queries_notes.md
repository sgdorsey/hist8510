# WHERE - watch for WHERE city_id = 1 OR city_id = 2 AND year > 1990 (reads and city_id=1 OR (city_id = 2 AND year > 1990))
# SQL evaluates AND before OR, so USE PARENTHESIS (like PEMDAS)
# Group By
# Having - Where's counterpart, but runs after grouping (GROUP BY, then HAVING more than 200 locations, etc.)
# LEFT JOIN - every row from the left table survives even with nothing to match - the unmatched sude comes back NULL, which is how you prove an absence
# Count, sum, avg, min, max
# aliases = AS is a nickname for an output column or table
# to run the queries line, sqlite3 dbname < queries.sql> (you can pull multiple queries in the same file, and put messages to yourself)