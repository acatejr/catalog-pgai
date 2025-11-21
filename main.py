from rich.console import Console
import json
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv
import os
import pgai
import fire

load_dotenv()

console = Console()
bs4 = BeautifulSoup()

DBNAME = os.environ.get("POSTGRES_DB")
DBUSER = os.environ.get("POSTGRES_USER")
DBPASS = os.environ.get("POSTGRES_PASSWORD")
DBHOST = os.environ.get("POSTGRES_HOST")
DBPORT = os.environ.get("POSTGRES_PORT", 5432)
DBURL = f"postgres://{DBUSER}:{DBPASS}@{DBHOST}:{DBPORT}/{DBNAME}"


def _strip_html_tags(text):
    """Removes HTML tags from text strings.

    Args:
        text (str): The input text containing HTML tags

    Returns:
        str: Cleaned text
    """

    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text()
    stripped_text = stripped_text.replace("\n", " ")
    return stripped_text


def _save_to_postgres(title, description):
    """Saves a document to the postgres database table

    Args:
        title (str): The document title
        description (str): The document description
    """

    conn = psycopg2.connect(
        dbname=DBNAME, user=DBUSER, password=DBPASS, host=DBHOST, port=DBPORT
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO document (title, description) VALUES (%s, %s)",
                (title, description),
            )
        conn.commit()
    finally:
        conn.close()


def _load_datahub_metadata():
    """Loads all metadata into the catalog.
    """

    metadata_file_name = "./data/metadata/datahub/metadata.json"

    with open(metadata_file_name, "r") as f:
        metadata = json.load(f)
        dataset = metadata["dataset"]
        for item in dataset:
            title = _strip_html_tags(item["title"])
            description = _strip_html_tags(item["description"])
            _save_to_postgres(title, description)


def load_docs():
    """Loads all metadata into the document table.
    """

    _load_datahub_metadata()

def clear_document_table():
    """Empties the document table.
    """

    conn = psycopg2.connect(
        dbname=DBNAME, user=DBUSER, password=DBPASS, host=DBHOST, port=DBPORT
    )
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE document RESTART IDENTITY CASCADE;")
        conn.commit()
    finally:
        conn.close()


def pgai_setup():
    """Required pgai setup.  Should only need to run this once against a database.
    """

    pgai.install(DBURL)


def main():
    fire.Fire({
        "clear-docs-tbl": clear_document_table,
        "load-docs": load_docs,
    })


if __name__ == "__main__":
    main()
