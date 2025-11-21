CREATE TABLE IF NOT EXISTS catalog_pgai.public.document (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    title TEXT NOT NULL,
    description TEXT NOT NULL
)


SELECT ai.create_vectorizer(
     'document'::regclass,
     loading => ai.loading_column(column_name=>'description'),
     destination => ai.destination_table(target_table=>'document_embedding'),
     embedding => ai.embedding_openai(model=>'text-embedding-ada-002', dimensions=>'1536')
)