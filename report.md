# Data Quality Report

**Rows**: 120 | **Columns**: 6

## Suggested Rules

- `{'column': 'CustomerID', 'rule': 'dedupe_key'}`

- `{'column': 'Age', 'rule': 'between', 'min': -5.0, 'max': 67.0}`

- `{'column': 'Email', 'rule': 'not_null'}`

- `{'column': 'Country', 'rule': 'allowed_values', 'values': ['United Kingdom', 'UnitedStates', 'USA', 'UAE', 'U.S.A']}`

- `{'column': 'Salary', 'rule': 'between', 'min': 29810.862460966844, 'max': 92146.33406191334}`


## Top Anomalies (sample)


|   CustomerID | Name   |   Age | Email                 | Country      |   Salary |   anomaly_score | top_deviation_col   |
|-------------:|:-------|------:|:----------------------|:-------------|---------:|----------------:|:--------------------|
|         1003 | Julia  |     9 | julia350@mail.com     | USA          |  45725   |        0.591094 | Age                 |
|         1019 | Diana  |    10 | nan                   | U.S.A        |  88930.8 |        0.592531 | Salary              |
|         1040 | Diana  |    -2 | diana914@company.org  | UnitedStates |  74751.7 |        0.6046   | Age                 |
|         1043 | Diana  |    -5 | diana943@example.com  | UnitedStates |  48676.8 |        0.622859 | Age                 |
|         1061 | Julia  |    55 | nan                   | UAE          |  30676.8 |        0.588099 | Salary              |
|         1083 | Fatima |    67 | fatima602@example.com | UnitedStates |  83613   |        0.636368 | Age                 |

