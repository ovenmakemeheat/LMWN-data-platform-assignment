# LMWN_asm

## Description

This is a Python project for the LMWN assignment that demonstrates Spark DataFrame manipulation techniques.

## Functions

### `flatten_df(df: DataFrame) -> DataFrame`

Recursively flattens a Spark DataFrame by:

- **StructType columns**: Expands nested structures into separate columns with underscore-separated names
- **ArrayType columns**: Preserves arrays without explosion (maintains original row count)

**Example:**

```python
# Input: DataFrame with nested structures
# Output: Flattened DataFrame with expanded columns, arrays preserved
```

**Key Features:**

- Handles deeply nested structures recursively
- Preserves data integrity during flattening
- Maintains original row count (no array explosion)
- Automatically generates descriptive column names

### `to_snake_case(name: str) -> str`

Converts column names to snake_case format by:

- Converting camelCase and PascalCase to snake_case
- Replacing dots with underscores
- Converting all characters to lowercase

**Example:**

```python
"driver_ID" → "driver_id"
"transactionRecord" → "transaction_record"
"trip_info.pricing.base_fare" → "trip_info_pricing_base_fare"
```

**Key Features:**

- Handles various naming conventions
- Preserves underscores in original names
- Consistent formatting for all column names

### `flatten_and_rename_to_snake_case(df: DataFrame) -> DataFrame`

Combines both functions to:

1. Flatten the DataFrame structure
2. Rename all columns to snake_case format

## Installation

To set up and run this project with uv, follow these steps:

### Initialize the project (UV)

```bash
uv init
```

### Add dependencies

```bash
uv add pyspark
```

### Run the main script

```bash
uv run python src/item1.py
```

## License

This project is licensed under the MIT License.
