# Uploading Data

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| CSV | `.csv` | Comma-separated values |
| TSV | `.tsv` | Tab-separated values |
| Excel | `.xlsx`, `.xls` | Requires openpyxl |
| JSON | `.json` | Array of objects |
| Parquet | `.parquet` | Columnar format |

## Using Sample Datasets

DataLens AI comes with 4 built-in sample datasets. Select one from the sidebar dropdown to get started immediately.

## Upload Limits

- Maximum file size: **100 MB** (configurable)
- Maximum rows displayed: **10,000** (full dataset is queryable)

## Data Profiling

After uploading, DataLens AI automatically:

1. **Detects column types** — numeric, categorical, datetime, text, boolean
2. **Identifies semantic types** — currency, email, URL, phone, country, etc.
3. **Computes statistics** — min, max, mean, median, std, quartiles
4. **Scores data quality** — completeness, uniqueness, consistency (0-100)
5. **Discovers relationships** — correlations between numeric columns
6. **Suggests questions** — based on the data structure
