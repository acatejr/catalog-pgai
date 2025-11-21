# Catalog Design

## Input

Answer each question:

1. Analyze one of the xml data/metadata/fsgeodata.
2. Analyze one of the json files in data/metadata/datahub
3. Analyze one of the json files in data/metadata/edw_services
4. Analyze one of the json files in data/metadata/rda
5. After analysis of 1 example of each metadata source suggest a method or plan for building a data catalog that uses the analyzed metadata so that the catalog can be queried much like a person interacts with a librarian at a library. For example, a user might ask What kinds of fire data exist?. Or, the user might ask for the data schema of a data table.  A user might also ask the librarian where to find a particular data set.
6. Can an LLM model be leveraged to enhance this application?  If so, how?
7. Derive SQL/DDL shemas of the tables that are referred to in the xml and json files?
8. Using Pydantic develop python data classes that might be a uniformed representation of the metadata
9. What database should be used to support this application? Postgresql with pgvector? Chromadb? DuckDB? MongoDB?
10. How would pgai affect this plan?
11. Make sure to create python code as part of the output markdown.

## Output

Save the output of this entire conversation/plan to catalog-convo.md in markdown format, overrite the original file.
