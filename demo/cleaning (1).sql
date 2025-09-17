-- Cleaning script for my_table
WITH src AS (SELECT * FROM my_table)
, step_1 AS (SELECT * FROM src QUALIFY ROW_NUMBER() OVER (PARTITION BY "CustomerID" ORDER BY "CustomerID") = 1)
SELECT * FROM step_1;