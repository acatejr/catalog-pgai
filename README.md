# Forest Service Data Catalog

A semantic metadata search and discovery system for U.S. Forest Service data sources.

## Features

- **Multi-source ingestion**: Process metadata from EDW, FSGeoData, DataHub, and RDA
- **Semantic search**: Vector embeddings for intelligent dataset discovery
- **Natural language interface**: Conversational search using plain English
- **REST API**: Programmatic access to catalog functionality
- **PostgreSQL + pgvector**: Scalable vector similarity search

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Database

Ensure PostgreSQL is running with pgvector extension:

```bash
# Create database
createdb data_catalog

# Enable pgvector extension
psql data_catalog -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 3. Configure Environment

Create `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=data_catalog
DB_USER=postgres
DB_PASSWORD=your_password
```

### 4. Run Complete Setup

```bash
python main.py all
```

This will:
- Set up database schema
- Ingest metadata from all sources
- Build vector embeddings for search

## Usage

### Conversational Interface

```bash
python main.py interface
```

Example queries:
- "Find datasets about wildfire in Montana"
- "Show me climate data from RDA"
- "What watershed datasets are available?"

### REST API

```bash
python main.py api
```

API Documentation: http://localhost:8000/docs

### Individual Commands

```bash
python main.py setup          # Set up database schema
python main.py test           # Test database connection
python main.py ingest         # Ingest metadata
python main.py index          # Build embeddings
python main.py status         # Show system status
```

## Architecture

### Core Components

1. **Database Layer** (`database.py`)
   - PostgreSQL with pgvector extension
   - Unified schema for all metadata sources
   - Vector similarity indexes

2. **Ingestion Engine** (`ingestion.py`)
   - Parse JSON/XML metadata files
   - Map to unified schema models
   - Validate and store in database

3. **Vector Search** (`vector_search.py`)
   - Generate embeddings using sentence-transformers
   - Semantic similarity search
   - Hybrid text + vector search

4. **Natural Language Interface** (`natural_language.py`)
   - Parse user queries into structured intents
   - Extract entities, themes, locations
   - Conversational search experience

5. **REST API** (`api.py`)
   - FastAPI-based web service
   - Search, browse, and detail endpoints
   - Statistics and health monitoring

### Data Sources

- **EDW Services**: ArcGIS REST services (145+ datasets)
- **FSGeoData**: FGDC XML metadata (188+ files)
- **DataHub**: ArcGIS Hub catalog (geospatial datasets)
- **RDA**: Research Data Archive (50+ scientific datasets)

## API Endpoints

### Search
- `POST /search` - Semantic search with filters
- `GET /search` - GET endpoint for search

### Dataset Management
- `GET /datasets/{id}` - Get dataset details
- `GET /datasets/{id}/related` - Find similar datasets

### Metadata
- `GET /themes` - List all themes
- `GET /sources` - List data sources
- `GET /stats` - Catalog statistics

### System
- `GET /health` - Health check
- `POST /ingest/{source}` - Trigger ingestion

## Configuration

### Database Settings
- Host, port, database name, credentials via `.env` file
- Automatic connection pooling and retry logic

### Search Configuration
- Embedding model: `all-MiniLM-L6-v2` (configurable)
- Similarity threshold: 0.3 (adjustable)
- Result limits: 10 default, max 100

### Performance Tuning
- Batch processing for ingestion (100 records/batch)
- Vector indexes with IVFFLAT algorithm
- Full-text search with PostgreSQL tsvector

## Development

### Code Style
- Follow PEP8 via ruff formatting
- Type hints for all functions
- Rich console output for user feedback

### Testing
```bash
pytest tests/
```

### Linting
```bash
ruff check .
ruff format .
```

## Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py", "api"]
```

### Environment Variables
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `EMBEDDING_MODEL` - Override default sentence transformer
- `API_HOST`, `API_PORT` - API server configuration

## Troubleshooting

### Common Issues

1. **pgvector extension not found**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Embedding generation fails**
   ```bash
   pip install sentence-transformers
   ```

3. **API server won't start**
   ```bash
   pip install fastapi uvicorn
   ```

4. **Memory issues with large datasets**
   - Reduce batch size in ingestion
   - Increase PostgreSQL shared_buffers
   - Use streaming for large result sets

### Performance Optimization

- **Vector Search**: Use appropriate IVFFLAT parameters based on dataset size
- **Text Search**: Configure PostgreSQL text search dictionaries
- **Caching**: Enable query result caching for frequent searches
- **Indexing**: Regular VACUUM and ANALYZE on vector tables

### PGAI

```bash
uv add pgai

# From cli
uv run pgai install -d postgresql://user:pass@localhost:5432/mydb
```
