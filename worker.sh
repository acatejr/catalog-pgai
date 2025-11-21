#!/opt/homebrew/bin/bash

uv run pgai vectorizer worker -d "postgres://<user>:<pass>!@0.0.0.0:5432/catalog_pgai"