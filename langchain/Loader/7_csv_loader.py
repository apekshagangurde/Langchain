"""
CSVLoader — Loading a CSV File
====================================

What is CSVLoader?
  A Document Loader that reads a CSV file and returns ONE Document PER
  ROW. Each Document's page_content is that row formatted as
  "column_name: value" pairs, one per line.

When to use it:
  - Your source data is tabular (a product catalog, FAQ sheet, pricing
    table, customer list, etc.) and each ROW is a self-contained unit
    of meaning worth retrieving on its own.

Limitations:
  - Each row becomes its own Document — relationships ACROSS rows
    (totals, trends, comparisons) are lost unless you pre-process them.
  - Very wide CSVs (many columns) produce long, repetitive Documents
    since every column name is repeated in every row.
  - No type handling — every value becomes plain text (e.g. price "9"
    is just the string "9", not a number).
"""

import os

from langchain_community.document_loaders import CSVLoader

sample_path = os.path.join(os.path.dirname(__file__), "sample.csv")
loader = CSVLoader(sample_path)
documents = loader.load()

print(f"Num documents: {len(documents)}")          # 1 per row
for i, doc in enumerate(documents, start=1):
    print(f"Row {i} content : {doc.page_content!r}")
    print(f"Row {i} metadata: {doc.metadata}")       # includes 'source', 'row'
