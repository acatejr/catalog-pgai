from dataclasses import dataclass
from typing import List
import numpy as np
from openai import AsyncOpenAI
import psycopg
from psycopg.rows import class_row
from pgvector.psycopg import register_vector_async
from psycopg_pool import AsyncConnectionPool
import os
from dotenv import load_dotenv
from pprint import pprint
from openai import AsyncClient, AsyncOpenAI
import asyncio

# import pgai
# from pgai.vectorizer import Worker
# from datasets import load_dataset
# import structlog
# import logging

load_dotenv()

DBNAME = os.environ.get("POSTGRES_DB")
DBUSER = os.environ.get("POSTGRES_USER")
DBPASS = os.environ.get("POSTGRES_PASSWORD")
DBHOST = os.environ.get("POSTGRES_HOST")
DBPORT = os.environ.get("POSTGRES_PORT", 5432)
DBURL = f"postgres://{DBUSER}:{DBPASS}@{DBHOST}:{DBPORT}/{DBNAME}"

@dataclass
class DocumentSearchResult:
    id: int
    title: str
    description: str
    chunk: str
    distance: float


async def _find_relevant_chunks(client: AsyncOpenAI, query: str, limit: int = 1) -> List[DocumentSearchResult]:
    # Generate embedding for the query using OpenAI's API
    response = await client.embeddings.create(
        model="text-embedding-ada-002",
        input=query,
        encoding_format="float",
    )

    embedding = np.array(response.data[0].embedding)

    # Create a connection pool to the database for efficient connection management
    # Using a connection pool is best practice for production applications
    async def setup_pgvector_psycopg(conn: psycopg.AsyncConnection):
        await register_vector_async(conn)

    pool = AsyncConnectionPool(DBURL, min_size=5, max_size=10, open=False, configure=setup_pgvector_psycopg)
    await pool.open()

    # Query the database for the most similar chunks using pgvector's cosine distance operator (<=>)
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=class_row(DocumentSearchResult)) as cur:
            await cur.execute("""
                SELECT d.id, d.title, d.description, d.chunk, d.embedding <=> %s as distance
                FROM document_embedding d
                ORDER BY distance
                LIMIT %s
            """, (embedding, limit))

            return await cur.fetchall()


# Add this function to read the prompt file
def _load_librarian_prompt() -> str:
    """Load the librarian prompt from the markdown file."""
    with open("librarian-prompt.md", "r") as f:
        return f.read()


async def run():
    """
    Main function that demonstrates the complete pgai workflow:
    1. Install pgai components in the database
    2. Set up the schema and vectorizer
    3. Load sample data
    4. Generate embeddings
    5. Perform vector similarity search
    6. Demonstrate RAG (Retrieval-Augmented Generation) with an LLM
    """

    # Perform a vector similarity search to find relevant articles
    client = AsyncClient()
    # results = await _find_relevant_chunks(client, "Is there soils data in this data catalog?")
    # print("Search results 1:")
    # pprint(results)

    # Search again to demonstrate that the new article is now searchable
#     results = await _find_relevant_chunks(client, "What is pgai?")
#     print("Search results 2:")
#     pprint(results)

    # Demonstrate RAG (Retrieval-Augmented Generation) by:
    # 1. Finding relevant chunks for a query
    # 2. Using those chunks as context for an LLM
    # 3. Getting a response that combines the retrieved information with the LLM's knowledge

    # Load the librarian system prompt
    librarian_prompt = _load_librarian_prompt()

    query = "What tables might have erosion data?"
    relevant_chunks = await _find_relevant_chunks(client, query)
    context = "\n\n".join(
        f"{chunk.title}:\n{chunk.description}"
        for chunk in relevant_chunks
    )

    # Use messages with system role for the librarian prompt
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": librarian_prompt},
            {"role": "user", "content": f"""Question: {query}

Available catalog data:

{context}"""}
        ]
    )
    print("RAG response:")
    print(response.choices[0].message.content)


asyncio.run(run())