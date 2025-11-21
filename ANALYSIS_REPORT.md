# Data Catalog Design - Comprehensive Analysis Report

## Executive Summary

This report provides a complete analysis of four metadata sources from the USDA Forest Service and proposes a unified, conversational data catalog system enhanced with Large Language Models (LLMs). The analysis covers:

1. **fsgeodata**: 186 XML files following FGDC metadata standards
2. **datahub**: 529 JSON datasets following DCAT/Project Open Data v1.1 standards
3. **edw_services**: 143 JSON ArcGIS REST API service definitions
4. **rda**: 976 JSON research datasets with DOI identifiers

---

## Table of Contents

1. [Metadata Source Analysis](#metadata-source-analysis)
2. [Unified Metadata Model](#unified-metadata-model)
3. [Conversational Data Catalog Design](#conversational-data-catalog-design)
4. [LLM Enhancement Strategy](#llm-enhancement-strategy)
5. [SQL DDL Schemas](#sql-ddl-schemas)
6. [Pydantic Data Models](#pydantic-data-models)
7. [Implementation Recommendations](#implementation-recommendations)

---

## 1. Metadata Source Analysis

### 1.1 fsgeodata (XML/FGDC Standard)

**Format**: FGDC-STD-001-1998 XML metadata

**Key Characteristics**:
- Federal Geographic Data Committee standard compliance
- Comprehensive geospatial metadata
- 7 main hierarchical sections: idinfo, dataqual, spdoinfo, spref, eainfo, distinfo, metainfo
- Extensive attribute documentation with enumerated domains
- 200+ activity/attribute codes

**Data Categories**:
- Activity data (Actv_*): Forest management activities, fuel treatments, timber harvest
- Boundary data (Bdy*): Administrative, ownership, designation, survey boundaries
- Fire data: Fire occurrences, perimeters, statistics
- Range data: Allotments, pastures, key monitoring areas
- Hydrology data: Watersheds, stream characteristics, climate data
- Transportation data: Roads, trails, linear referencing systems

**Organizational Hierarchy**:
```
Region (01-10) → Forest (RRFF) → District (RRFFDD)
```

**Key Identifiers**:
- **CN**: Control Number (Oracle-generated unique ID)
- **SUID**: Subunit ID (Region+Forest+District+FACTS ID+Subunit)
- **ORG**: Organization code (RRFFDD format)

**System Integration**:
- FACTS (Forest Activity Tracking System)
- FIRESTAT (Fire statistics)
- IRWIN (Integrated Reporting of Wildland-Fire Information)
- RIMS (Rangeland Information Management System)
- EDW (Enterprise Data Warehouse)

### 1.2 datahub (JSON/DCAT Standard)

**Format**: Project Open Data v1.1 / DCAT JSON-LD

**Key Characteristics**:
- 529 datasets from USFS ArcGIS Hub
- Full DCAT compliance with semantic web compatibility
- Consistent Creative Commons BY 4.0 licensing
- All datasets tagged as "geospatial"
- ArcGIS item IDs in identifiers

**Structure**:
```json
{
  "@context": "https://project-open-data.cio.gov/v1.1/schema/catalog.jsonld",
  "@type": "dcat:Catalog",
  "dataset": [...]
}
```

**Core Fields** (18 standard fields per dataset):
- identifier, landingPage, title, description
- keyword (array), issued, modified
- publisher, contactPoint (nested objects)
- accessLevel, spatial, license
- programCode, bureauCode, theme
- progressCode, distribution (array)

**Distribution Types** (23 unique):
- ISO-19139 metadata (XML)
- ArcGIS GeoService (REST API)
- ArcGIS Hub Dataset (web page)
- OGC WMS/WFS (web services)
- Downloadable formats (CSV, Shapefile, GeoJSON, KML, Geodatabase)

**Spatial Format**: Bounding box as string: "minX,minY,maxX,maxY"

### 1.3 edw_services (JSON/ArcGIS REST API)

**Format**: ArcGIS REST API Map Service definitions

**Key Characteristics**:
- 143 operational map services
- Real-time data access through REST APIs
- Multi-layer hierarchical structure
- Time-enabled services for temporal data
- Scale-dependent layer visibility

**Service Structure**:
```
Service
├── currentVersion, cimVersion
├── serviceDescription, mapName
├── capabilities, supportedQueryFormats
├── layers[] (Feature Layer, Group Layer)
├── tables[] (Related data tables)
├── spatialReference
├── extent (initial, full)
└── timeInfo (temporal services)
```

**Layer Structure**:
- id (layer identifier)
- name (layer name)
- parentLayerId (hierarchical organization)
- geometryType (Point, Polyline, Polygon)
- minScale/maxScale (visibility range)
- defaultVisibility

**Geometry Types**:
- esriGeometryPoint (fire occurrences, facilities)
- esriGeometryPolyline (roads, streams, boundaries)
- esriGeometryPolygon (boundaries, treatments, allotments)

**Coordinate Systems**:
- NAD 1983 (wkid: 4269) - Geographic
- Web Mercator (wkid: 102100/3857) - Projected

**Temporal Services**:
- timeInfo with extent in milliseconds
- defaultTimeInterval and units
- Time-enabled for fire occurrence (1992-2020), activities, treatments

### 1.4 rda (JSON/Research Data Archive)

**Format**: Project Open Data v1.1 / DCAT (research-focused)

**Key Characteristics**:
- 976 research datasets
- DOI identifiers: `https://doi.org/10.2737/RDS-YYYY-NNNN`
- Forest Service Research Data Archive
- Creative Commons BY 2.0 licensing
- Long-term research and experimental data

**Research Focus Areas**:
- Forest ecology and hydrology
- Climate and meteorology
- Fire science
- Wildlife ecology
- Vegetation dynamics
- LiDAR and geospatial research
- Environmental impact studies

**Unique Attributes**:
- Experimental sites (Marcell, Fraser, Glacier Lakes, Manitou, Priest River, Black Hills)
- Edition versioning (RDS-2006-0003, RDS-2006-0003-2)
- Detailed methodology descriptions
- Funding acknowledgments (JFSP, SERDP)
- Small geographic extents (site-specific)
- Multi-year/decade temporal coverage

**Publisher Structure**:
```json
{
  "publisher": {
    "name": "Forest Service Research Data Archive",
    "subOrganizationOf": {
      "@type": "org:Organization",
      "name": "U.S. Forest Service"
    }
  }
}
```

---

## 2. Unified Metadata Model

### 2.1 Core Entity Model

#### Dataset (Core Entity)

**Universal Properties**:
```
- dataset_id (UUID, primary key)
- source_system (fsgeodata|datahub|edw_services|rda)
- source_identifier (original ID from source)
- title (string, required)
- description (text, required)
- abstract (text, optional - detailed description)
- purpose (text, optional)
- keywords (array of strings)
- themes (array - mapped to controlled vocabulary)
```

**Temporal Properties**:
```
- created_date (timestamp)
- modified_date (timestamp)
- publication_date (timestamp)
- temporal_extent_start (date)
- temporal_extent_end (date)
- update_frequency (enum: daily|weekly|monthly|annually|asNeeded|none)
```

**Spatial Properties**:
```
- spatial_extent (geometry - bounding box)
- coordinate_system (string - EPSG code)
- spatial_resolution (string)
- geographic_coverage (array - place names)
```

**Access Properties**:
```
- access_level (enum: public|restricted|private)
- license (string - URL or identifier)
- license_type (enum: CC-BY-2.0|CC-BY-4.0|publicDomain|other)
- distribution_formats (array - CSV, GeoJSON, REST API, etc.)
- primary_url (string - landing page)
- api_endpoints (array of URLs)
```

**Organizational Properties**:
```
- publisher_org (string)
- publisher_suborg (string)
- contact_name (string)
- contact_email (string)
- bureau_code (string)
- program_code (string)
- region_code (string - 01-10)
- forest_code (string)
- district_code (string)
```

**Quality Properties**:
```
- completeness (text)
- accuracy (text)
- data_source (text)
- lineage (text - processing history)
- quality_score (float - calculated)
```

#### Service (Extends Dataset for EDW Services)

**Service-Specific Properties**:
```
- service_type (enum: MapService|FeatureService|ImageService)
- service_version (string)
- capabilities (array - Map, Query, Data, etc.)
- max_record_count (integer)
- supported_formats (array - JSON, geoJSON, PBF)
- time_enabled (boolean)
- layer_count (integer)
```

#### Layer (Child of Service)

**Layer Properties**:
```
- layer_id (integer, within service context)
- service_id (foreign key to Service)
- layer_name (string)
- layer_type (enum: FeatureLayer|GroupLayer|Table)
- parent_layer_id (integer, self-referencing)
- geometry_type (enum: Point|Polyline|Polygon|None)
- min_scale (float)
- max_scale (float)
- default_visibility (boolean)
- feature_count (integer)
```

#### ResearchDataset (Extends Dataset for RDA)

**Research-Specific Properties**:
```
- doi (string - digital object identifier)
- experimental_site (string)
- edition_number (integer)
- funding_programs (array)
- methodology (text)
- related_editions (array of DOIs)
- data_collection_period_start (date)
- data_collection_period_end (date)
- scientific_objectives (text)
```

### 2.2 Supporting Entities

#### Keyword

```
- keyword_id (UUID)
- term (string, unique)
- category (enum: theme|place|temporal|taxon|instrument)
- controlled_vocabulary (string - source thesaurus)
- definition (text)
```

#### Organization

```
- org_id (UUID)
- org_code (string - e.g., "0117")
- org_name (string)
- org_type (enum: region|forest|district|researchStation)
- parent_org_id (foreign key, self-referencing)
- hierarchy_level (integer)
```

#### Distribution

```
- distribution_id (UUID)
- dataset_id (foreign key)
- distribution_type (enum: download|api|webService|webPage|metadata)
- format (string - CSV, GeoJSON, REST API, etc.)
- media_type (string - MIME type)
- access_url (string)
- conforms_to (string - standard URL)
- size_bytes (bigint)
```

### 2.3 Relationship Model

```
Dataset 1:N Distribution
Dataset N:M Keyword (through DatasetKeyword)
Dataset N:1 Organization (publisher)
Service 1:N Layer
Service IS-A Dataset
ResearchDataset IS-A Dataset
Layer N:1 Layer (parent_layer)
ResearchDataset N:M ResearchDataset (editions)
```

### 2.4 Unified Schema JSON Example

```json
{
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "source_system": "fsgeodata",
  "source_identifier": "S_USA.Activity_HazFuelTrt_PL",
  "title": "Hazardous Fuel Treatments - Polygon",
  "description": "Activities of hazardous fuel treatment reduction that are polygons...",
  "keywords": ["Vegetation Management", "Fuel Treatment", "Ecosystem Restoration"],
  "themes": ["fire_management", "vegetation", "land_management"],
  "created_date": "2016-02-12T00:00:00Z",
  "modified_date": "2025-10-24T03:25:55Z",
  "temporal_extent_start": "1960-01-01",
  "temporal_extent_end": null,
  "update_frequency": "daily",
  "spatial_extent": {
    "type": "Polygon",
    "coordinates": [[[-151.56, 0.0004], [-51.81, 0.0004], [-51.81, 85.41], [-151.56, 85.41], [-151.56, 0.0004]]]
  },
  "coordinate_system": "EPSG:4269",
  "access_level": "public",
  "license": "https://www.usa.gov/government-works",
  "distribution_formats": ["ArcGIS REST API", "Shapefile", "GeoJSON"],
  "primary_url": "http://data.fs.usda.gov/geodata/edw/datasets.php",
  "publisher_org": "U.S. Forest Service",
  "publisher_suborg": "Chief Information Office, Enterprise Data Warehouse",
  "contact_email": "SM.FS.data@usda.gov",
  "bureau_code": "005:96",
  "data_source": "NRM FACTS",
  "quality_score": 0.95
}
```

---

## 3. Conversational Data Catalog Design

### 3.1 Query Patterns for Natural Language Interactions

#### Pattern 1: Discovery Queries

**Example**: *"What kinds of fire data exist?"*

**Query Understanding**:
- Intent: DISCOVER
- Domain: fire
- Entity Type: dataset
- Scope: all

**System Response Strategy**:
1. Search keywords and themes for "fire"
2. Group by data category (occurrence, perimeter, treatment, hazard)
3. Provide summary counts and examples
4. Offer drill-down options

**Response Template**:
```
I found 47 fire-related datasets across these categories:

1. **Fire Occurrence** (15 datasets)
   - National Fire Occurrence Database (1992-2020)
   - Historical fire locations by year
   - Fire statistics and causes

2. **Fire Perimeters** (8 datasets)
   - Final fire perimeters with acreage
   - MTBS (Monitoring Trends in Burn Severity)
   - RAVG (Rapid Assessment of Vegetation Condition)

3. **Hazardous Fuel Treatments** (12 datasets)
   - Prescribed burn areas
   - Mechanical treatments
   - Fuel reduction activities

4. **Wildfire Hazard** (7 datasets)
   - Wildfire Hazard Potential maps
   - Fire weather indices
   - Burn probability models

5. **Fire Retardant** (5 datasets)
   - Avoidance areas (aquatic/terrestrial)
   - Hydrographic restrictions

Would you like to explore any specific category?
```

#### Pattern 2: Schema Queries

**Example**: *"Show me the schema for Activity_HazFuelTrt_PL"*

**Query Understanding**:
- Intent: SCHEMA
- Entity: Activity_HazFuelTrt_PL
- Detail Level: full structure

**System Response Strategy**:
1. Exact match on title/identifier
2. Extract attribute definitions from eainfo
3. Organize by category (spatial, administrative, activity, temporal)
4. Include data types and domain values

**Response Template**:
```
Schema for **Hazardous Fuel Treatments - Polygon** (Activity_HazFuelTrt_PL)

**Spatial Fields**:
- OBJECTID (Integer): Internal feature number
- SHAPE (Geometry): Polygon geometry
- GIS_ACRES (Double): Calculated area in acres

**Identification**:
- SUID (Text): Subunit ID - Region+Forest+District+FACTS ID+Subunit
- CN (Text): Control Number (unique identifier)
- ORG (Text): Organizational unit (Region+Forest+District)

**Activity Information**:
- ACTIVITY_CODE (Text): 4-digit activity code
  - 1111: Broadcast Burning
  - 1130: Burning of Piled Material
  - 1160: Thinning for Hazardous Fuels Reduction
  - [45+ more codes]
- ACTIVITY_NAME (Text): Activity description
- ACTIVITY_QUANTITY (Double): Acres treated
- ACTIVITY_UOM (Text): Unit of measure

**Temporal**:
- DATE_PLANNED (Date): Planned start date
- DATE_ACCOMPLISHED (Date): Completion date
- FY_PLANNED (Integer): Fiscal year planned
- FY_ACCOMPLISHED (Integer): Fiscal year completed

**Administrative**:
- REGION_CODE (Text): 2-digit region (01-10)
- ADMIN_FOREST_CODE (Text): 2-digit forest code
- DISTRICT_CODE (Text): 2-digit district code
- ADMIN_ORG_ID (Text): Full org code (RRFFDD)

**Data Quality**:
- DATA_SOURCE (Text): Spatial accuracy code (00-48)
- REV_DATE (Date): Last revision date
- ETL_MODIFIED (Date): ETL timestamp

Total: 80+ fields. Would you like details on specific fields or domain values?
```

#### Pattern 3: Location Queries

**Example**: *"Where can I find datasets about the Nez Perce-Clearwater National Forests?"*

**Query Understanding**:
- Intent: LOCATE
- Location: Nez Perce-Clearwater National Forests
- Scope: all datasets

**System Response Strategy**:
1. Fuzzy match on forest names
2. Look up forest code (0117)
3. Search by organization code, keywords, geographic coverage
4. Spatial intersection with forest boundary

**Response Template**:
```
Found 38 datasets for **Nez Perce-Clearwater National Forests** (Forest Code: 0117, Region 01):

**Administrative & Boundaries** (5 datasets):
- Forest boundaries and ranger districts
- Administrative units
- Ownership data

**Activities & Management** (15 datasets):
- Hazardous fuel treatments
- Timber harvest activities
- Range allotments and pastures

**Natural Resources** (12 datasets):
- Fire occurrence and perimeters
- Invasive species locations
- Wildlife habitat data

**Infrastructure** (6 datasets):
- Road systems (MVUM)
- Trails network
- Recreation sites

All datasets can be filtered by specific ranger districts:
- Clearwater (011701)
- Nez Perce (011702)
- Moose Creek (011703)
- [+ additional districts]

Would you like to see datasets for a specific district or activity type?
```

#### Pattern 4: Comparison Queries

**Example**: *"Compare fire occurrence data between Region 1 and Region 5"*

**Query Understanding**:
- Intent: COMPARE
- Domain: fire occurrence
- Locations: Region 1, Region 5
- Metric: implicit (count, acres, trends)

**System Response Strategy**:
1. Filter fire occurrence datasets by region
2. Extract temporal coverage
3. Calculate summary statistics
4. Provide visualization-ready data

**Response Template**:
```
**Fire Occurrence Comparison: Region 1 (Northern) vs Region 5 (Pacific Southwest)**

**Dataset Availability**:
- Both regions: National Fire Occurrence Database (1992-2020)
- Regional specific: Fire statistics by forest

**Region 1 (Northern)**:
- Forests: 12 national forests
- Fire occurrences (1992-2020): ~45,000 fires
- Total acres burned: ~8.2 million acres
- Primary causes: Lightning (45%), Equipment (18%), Debris burning (12%)

**Region 5 (Pacific Southwest)**:
- Forests: 18 national forests
- Fire occurrences (1992-2020): ~78,000 fires
- Total acres burned: ~12.6 million acres
- Primary causes: Lightning (38%), Arson (22%), Equipment (15%)

**Key Differences**:
- Region 5 has 73% more fire occurrences
- Region 5 has 54% more acres burned
- Region 5 has higher percentage of human-caused fires
- Region 1 has higher percentage of lightning-caused fires

**Available Datasets**:
1. Fire Occurrence Points (annual layers)
2. Fire Perimeters (polygons)
3. Fire Statistics (tabular)
4. Burn Severity (MTBS)

Would you like detailed data for specific years or forests?
```

#### Pattern 5: Related Data Queries

**Example**: *"What other datasets are related to wilderness areas?"*

**Query Understanding**:
- Intent: DISCOVER_RELATED
- Seed Concept: wilderness areas
- Relationship: conceptual similarity

**System Response Strategy**:
1. Find wilderness boundary datasets
2. Semantic expansion (protected areas, recreation, wildlife)
3. Spatial relationships (data within wilderness boundaries)
4. Management relationships (activities affecting wilderness)

**Response Template**:
```
**Datasets Related to Wilderness Areas**:

**Direct Wilderness Data** (8 datasets):
- Wilderness boundaries and status
- Recommended wilderness areas
- Wild and Scenic Rivers
- Roadless areas (inventoried)
- Wilderness study areas

**Recreation & Access** (12 datasets):
- Trail systems within wilderness
- Trailheads and access points
- Recreation opportunity spectrum
- Outfitter and guide permits
- Campsite locations

**Wildlife & Ecology** (18 datasets):
- Threatened and endangered species habitats
- Critical habitat designations
- Wildlife observation data
- Vegetation mapping

**Management Activities** (14 datasets):
- Wilderness management plans
- Impact assessment data (pack stock, campsites)
- Fire management (natural ignitions)
- Invasive species monitoring

**Research Data** (22 datasets from RDA):
- Long-term ecological monitoring
- Wilderness visitor studies
- Environmental impact studies
- Climate change research

**Boundaries & Context** (7 datasets):
- National forest boundaries
- Ranger districts
- Proclamation boundaries
- Land ownership

Would you like to explore a specific category or search within a particular wilderness area?
```

### 3.2 Search and Retrieval Strategies

#### Vector Similarity Search

**Implementation**:
- Embed dataset titles, descriptions, and keywords using sentence-transformers
- Store vectors in vector database (e.g., pgvector, Pinecone, Weaviate)
- Enable semantic search beyond keyword matching

**Example**:
```
Query: "areas with prescribed burning"
Matches:
1. Hazardous Fuel Treatments (cosine similarity: 0.92)
2. Fire Management Activities (0.89)
3. Wildfire Hazard Potential (0.76)
4. Vegetation Treatment Areas (0.71)
```

#### Faceted Search

**Facets**:
- **Domain**: fire, vegetation, water, wildlife, recreation, boundaries, infrastructure
- **Data Type**: vector, raster, tabular, service
- **Geometry**: point, line, polygon
- **Temporal Coverage**: by decade, year, season
- **Spatial Coverage**: by region, forest, state
- **Update Frequency**: daily, weekly, monthly, annually, static
- **Access Level**: public, restricted
- **Format**: REST API, Shapefile, GeoJSON, CSV, WMS, etc.

**UI Implementation**:
```
[Fire] (127)
  ├─ Occurrence (45)
  ├─ Perimeters (28)
  ├─ Treatments (34)
  └─ Hazard (20)

[Temporal]
  ├─ Current (2020+) (89)
  ├─ Historical (1960-2019) (234)
  └─ Long-term monitoring (45)

[Region]
  ├─ Region 01 (134)
  ├─ Region 02 (98)
  ├─ Region 03 (87)
  ...
```

#### Hybrid Search (Keyword + Vector)

**Approach**:
1. Keyword search with BM25 scoring
2. Vector similarity search with cosine distance
3. Combine scores with weighted average
4. Re-rank based on popularity, recency, quality

**Score Calculation**:
```python
final_score = (
    0.4 * keyword_score +
    0.4 * vector_score +
    0.1 * popularity_score +
    0.1 * recency_score
)
```

#### Spatial Search

**Query Types**:
- **Bounding box**: Find datasets intersecting a rectangle
- **Point buffer**: Find datasets within radius of a point
- **Polygon intersection**: Find datasets overlapping a polygon
- **Named place**: Geocode location and search by extent

**PostGIS Implementation**:
```sql
SELECT d.dataset_id, d.title,
       ST_Area(ST_Intersection(d.spatial_extent, :query_geom)) /
       ST_Area(d.spatial_extent) AS overlap_ratio
FROM datasets d
WHERE ST_Intersects(d.spatial_extent, :query_geom)
ORDER BY overlap_ratio DESC
LIMIT 20;
```

### 3.3 Indexing Approach for Efficient Queries

#### Full-Text Search Index

**PostgreSQL (with pg_trgm extension)**:
```sql
CREATE INDEX idx_dataset_title_gin ON datasets USING gin(title gin_trgm_ops);
CREATE INDEX idx_dataset_description_gin ON datasets USING gin(description gin_trgm_ops);
CREATE INDEX idx_dataset_keywords_gin ON datasets USING gin(keywords);
```

**Elasticsearch Index Mapping**:
```json
{
  "mappings": {
    "properties": {
      "dataset_id": {"type": "keyword"},
      "title": {
        "type": "text",
        "analyzer": "english",
        "fields": {
          "keyword": {"type": "keyword"},
          "suggest": {"type": "completion"}
        }
      },
      "description": {"type": "text", "analyzer": "english"},
      "keywords": {"type": "keyword"},
      "themes": {"type": "keyword"},
      "spatial_extent": {"type": "geo_shape"},
      "temporal_extent": {"type": "date_range"},
      "publisher_org": {"type": "keyword"},
      "region_code": {"type": "keyword"},
      "source_system": {"type": "keyword"},
      "quality_score": {"type": "float"}
    }
  }
}
```

#### Spatial Index

**PostGIS**:
```sql
CREATE INDEX idx_spatial_extent_gist ON datasets USING gist(spatial_extent);
CREATE INDEX idx_org_region ON datasets(region_code, forest_code, district_code);
```

#### Temporal Index

```sql
CREATE INDEX idx_temporal_coverage ON datasets
USING btree(temporal_extent_start, temporal_extent_end);

CREATE INDEX idx_modified_date ON datasets(modified_date DESC);
```

#### Composite Indexes for Common Queries

```sql
-- Fire data by region and year
CREATE INDEX idx_fire_region_year ON datasets(region_code, temporal_extent_start)
WHERE 'fire' = ANY(themes);

-- Recent updates by category
CREATE INDEX idx_theme_modified ON datasets(themes, modified_date DESC);
```

#### Vector Index

**Using pgvector**:
```sql
CREATE EXTENSION vector;

CREATE TABLE dataset_embeddings (
  dataset_id UUID PRIMARY KEY REFERENCES datasets(dataset_id),
  embedding vector(384),  -- sentence-transformers dimension
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_embedding_ivfflat ON dataset_embeddings
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 4. LLM Enhancement Strategy

### 4.1 Natural Language Query Understanding

#### Intent Classification

**Intents**:
- DISCOVER: Find datasets by topic/theme
- SCHEMA: Get structure and field definitions
- LOCATE: Find data by geographic location
- COMPARE: Compare datasets or statistics
- RELATE: Find related/similar datasets
- DOWNLOAD: Access or retrieve data
- METADATA: Get detailed metadata
- TEMPORAL: Filter by time period
- QUALITY: Assess data quality/completeness

**Few-Shot Prompt**:
```
Classify the user's intent. Choose from: DISCOVER, SCHEMA, LOCATE, COMPARE, RELATE, DOWNLOAD, METADATA, TEMPORAL, QUALITY

Examples:
User: "What fire data is available?"
Intent: DISCOVER | Domain: fire

User: "Show me the fields in the road dataset"
Intent: SCHEMA | Entity: road dataset

User: "Find datasets about Region 5"
Intent: LOCATE | Location: Region 5

User: "Compare fire occurrence in 2020 vs 2021"
Intent: COMPARE | Domain: fire | Temporal: 2020, 2021

Now classify:
User: "{user_query}"
Intent:
```

#### Entity Extraction

**Named Entity Recognition**:
- **Geographic**: Regions (01-10), Forest names, State names, Place names
- **Temporal**: Years, date ranges, decades, seasons
- **Domain**: Fire, vegetation, water, wildlife, recreation, boundaries
- **Dataset Names**: Explicit mentions of datasets/layers
- **Organizations**: Forest Service, Research Station, Bureau names

**Using LLM with Structured Output**:
```
Extract entities from the user query. Return JSON.

User query: "Show me wildfire data for Nez Perce forest from 2015 to 2020"

Extract:
{
  "geographic_entities": ["Nez Perce forest"],
  "temporal_entities": ["2015 to 2020"],
  "domain_entities": ["wildfire"],
  "dataset_entities": [],
  "intent": "LOCATE",
  "filters": {
    "forest_name": "Nez Perce",
    "start_year": 2015,
    "end_year": 2020,
    "domain": "fire"
  }
}
```

### 4.2 Metadata Enrichment and Tagging

#### Automatic Categorization

**Theme Extraction**:
- Use LLM to read descriptions and assign themes
- Map to controlled vocabulary
- Generate hierarchical tags

**Prompt Template**:
```
Read this dataset description and assign relevant themes from the controlled vocabulary.

Description: "{description}"

Controlled Vocabulary:
- fire_management: fire_occurrence, fire_perimeter, fire_hazard, fuel_treatment
- vegetation: forest_inventory, vegetation_classification, invasive_species
- water: hydrology, watersheds, water_quality, aquatic_habitat
- wildlife: wildlife_habitat, species_inventory, threatened_endangered
- recreation: trails, campgrounds, recreation_sites, visitor_use
- boundaries: administrative, ownership, designation, survey

Assign themes (select all that apply):
```

#### Quality Scoring

**Factors**:
- Completeness of metadata (18 factors)
- Recency of updates
- Spatial accuracy indicators
- Temporal coverage
- Documentation quality

**LLM-Based Assessment**:
```
Assess the data quality based on this metadata:

Metadata:
- Description: {description}
- Last Updated: {modified_date}
- Data Source: {data_source}
- Accuracy: {accuracy}
- Completeness: {completeness}

Rate on scale 0-1:
1. Metadata completeness (0-1):
2. Data currency (0-1):
3. Spatial accuracy (0-1):
4. Documentation quality (0-1):
5. Overall quality score (average):
```

#### Keyword Expansion

**Synonym Generation**:
```
Original keywords: ["fire occurrence", "wildfire", "FIRESTAT"]

Generate related keywords and synonyms:
- fire incident
- wildland fire
- forest fire
- fire event
- fire ignition
- fire start
- fire report
```

**Implementation**:
```python
def expand_keywords(original_keywords: List[str]) -> List[str]:
    prompt = f"""
    Generate synonyms and related terms for these keywords:
    {', '.join(original_keywords)}

    Return a JSON list of expanded keywords.
    """
    response = llm.generate(prompt)
    expanded = json.loads(response)
    return list(set(original_keywords + expanded))
```

### 4.3 Query Suggestion and Refinement

#### Auto-Complete Suggestions

**Approaches**:
1. Prefix matching on indexed titles/keywords
2. Popular query logs
3. LLM-generated suggestions based on partial input

**Example**:
```
User types: "fire data for reg"

Suggestions:
- fire data for Region 1
- fire data for Region 5
- fire occurrence data for region
- fire perimeter data for region
- fire hazard potential regional maps
```

#### Query Refinement

**Scenario**: User query is too broad or ambiguous

**LLM Prompt**:
```
The user query is: "{query}"

Search returned 847 results, which is too many. Suggest 3-5 refinement options:

1. Narrow by time period
2. Narrow by geography
3. Narrow by data type
4. Narrow by specific topic

Generate specific refinement suggestions:
```

**Example Output**:
```
Your search for "fire data" returned 847 datasets.

Would you like to narrow your search by:

1. **Time Period**
   - Last 5 years (2020-2024)
   - Last decade (2015-2024)
   - Historical (before 2000)

2. **Data Type**
   - Fire occurrence (point locations)
   - Fire perimeters (polygons)
   - Fire hazard models (rasters)
   - Fire treatment activities

3. **Geographic Area**
   - Specific region (1-10)
   - Specific state
   - Specific forest

4. **Specific Topic**
   - Fire causes and statistics
   - Burn severity
   - Fuel treatments
   - Fire weather
```

#### Clarification Questions

**When to Ask**:
- Ambiguous locations (multiple forests with similar names)
- Unclear temporal scope
- Multiple valid interpretations

**Example**:
```
User: "Show me road data"

LLM Response:
"I found several types of road datasets. Which are you interested in?

1. **National Forest System Roads (NFSR)** - Official road system with maintenance levels
2. **Road Core** - Basic road centerlines
3. **Motor Vehicle Use Maps (MVUM)** - Roads open to public motor vehicle use
4. **Forest Development Roads** - Includes decommissioned roads

Or would you like to see all road-related datasets?"
```

### 4.4 Data Discovery Recommendations

#### Collaborative Filtering

**"Users who viewed this dataset also viewed..."**

**Implementation**:
```sql
WITH dataset_cooccurrence AS (
  SELECT
    s1.dataset_id AS dataset_a,
    s2.dataset_id AS dataset_b,
    COUNT(*) AS cooccurrence_count
  FROM search_logs s1
  JOIN search_logs s2 ON s1.session_id = s2.session_id
  WHERE s1.dataset_id < s2.dataset_id
  GROUP BY s1.dataset_id, s2.dataset_id
)
SELECT dataset_b, cooccurrence_count
FROM dataset_cooccurrence
WHERE dataset_a = :current_dataset_id
ORDER BY cooccurrence_count DESC
LIMIT 5;
```

#### Content-Based Recommendations

**Similarity Factors**:
- Vector similarity (embeddings)
- Shared keywords/themes
- Geographic overlap
- Temporal overlap
- Same source system
- Related data types

**LLM-Enhanced Recommendations**:
```
The user is viewing: "Hazardous Fuel Treatments - Polygon"

Description: "{description}"
Keywords: {keywords}
Region: {region}
Temporal: {temporal_extent}

Recommend 5 related datasets that would be useful to someone analyzing fuel treatments.
Consider:
- Fire occurrence data (to analyze treatment effectiveness)
- Vegetation data (pre/post treatment condition)
- Topography (terrain influence on treatments)
- Budget data (treatment costs)
- Planning documents

For each recommendation, explain why it's relevant.
```

#### Context-Aware Recommendations

**User Profile Factors**:
- Previous searches
- Downloaded datasets
- Saved/bookmarked items
- Organization affiliation
- Common workflows

**Example**:
```
Based on your recent activity (viewing fire occurrence and perimeter data for Region 6),
you might also be interested in:

1. **Wildfire Hazard Potential - Region 6**
   Why: Provides context for where fires occurred relative to predicted hazard

2. **Vegetation Burn Severity (RAVG) - Region 6**
   Why: Shows fire effects and intensity for perimeters you viewed

3. **Fire Weather Indices - Pacific Northwest**
   Why: Weather conditions during fire season in your region of interest

4. **Fuel Treatment Locations - Region 6**
   Why: See where treatments occurred before fires to assess effectiveness

5. **Post-Fire Recovery Monitoring Data**
   Why: Research datasets tracking vegetation recovery after fires
```

### 4.5 Schema Explanation in Plain Language

#### Field Definitions

**LLM Translation**:
```
Technical definition:
"SUID: Subunit ID. Concatenation of the Region, Forest, District, FACTS ID,
and Subunit codes. Format: RRFFDD + 10-digit FACTS ID + 3-digit subunit.
Example: 0111021A51466541016"

Plain language explanation:
"SUID is a unique identifier that tells you exactly where an activity took place.
It combines:
- The region number (first 2 digits)
- The forest number (next 2 digits)
- The district number (next 2 digits)
- A project ID (next 10 characters)
- A sub-area within the project (last 3 digits)

Think of it like a detailed address for forest management activities."
```

#### Domain Value Explanations

**Example: ACTIVITY_CODE**

**Technical**:
```
1111: Broadcast Burning - Covers a majority of the unit
```

**Plain Language (LLM-Generated)**:
```
**Broadcast Burning (1111)**

What it means: A controlled fire that burns across most of an area

Why it's done:
- Reduce hazardous fuels (dead trees, brush, leaves)
- Mimic natural fire cycles
- Improve forest health
- Prevent larger, uncontrolled wildfires

How it works:
- Fire is intentionally set within defined boundaries
- Covers majority or all of the treatment area
- Carefully controlled with fire crews present

When it's used:
- Under specific weather conditions
- With proper permits and approvals
- Part of forest management plans

Related codes:
- 1112: Jackpot Burning (scattered piles only)
- 1113: Underburn (low intensity under trees)
- 1130: Pile Burning (burning of collected material)
```

#### Data Usage Guidance

**LLM-Generated Use Cases**:
```
Dataset: Fire Occurrence Database

Common questions this data can answer:
1. "Where do fires start most frequently?"
2. "What are the main causes of fires in my area?"
3. "How has fire activity changed over time?"
4. "When during the year do most fires occur?"
5. "How large are typical fires in different regions?"

Analysis examples:
- Create heat maps of fire density
- Analyze seasonal patterns
- Compare human vs. lightning-caused fires
- Track trends over decades
- Identify high-risk areas

Limitations to be aware of:
- Not all fires are included (size threshold)
- Location accuracy varies
- Discovery date vs. actual start may differ
- Cause determination may be uncertain

Best combined with:
- Fire perimeter data (for fire size/shape)
- Vegetation data (for fuel types)
- Weather data (for fire conditions)
- Topography (for fire spread patterns)
```

---

## 5. SQL DDL Schemas

### 5.1 Core Tables

#### datasets

```sql
CREATE TABLE datasets (
    -- Primary Key
    dataset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source Information
    source_system VARCHAR(50) NOT NULL
        CHECK (source_system IN ('fsgeodata', 'datahub', 'edw_services', 'rda')),
    source_identifier VARCHAR(500) NOT NULL,
    source_url TEXT,

    -- Basic Metadata
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    abstract TEXT,
    purpose TEXT,

    -- Temporal Metadata
    created_date TIMESTAMP,
    modified_date TIMESTAMP,
    publication_date TIMESTAMP,
    temporal_extent_start DATE,
    temporal_extent_end DATE,
    update_frequency VARCHAR(50)
        CHECK (update_frequency IN ('daily', 'weekly', 'monthly', 'annually', 'asNeeded', 'irregular', 'none', 'unknown')),

    -- Spatial Metadata
    spatial_extent GEOMETRY(Polygon, 4326),
    coordinate_system VARCHAR(50),
    spatial_resolution VARCHAR(100),

    -- Access Metadata
    access_level VARCHAR(20) NOT NULL DEFAULT 'public'
        CHECK (access_level IN ('public', 'restricted', 'private')),
    license_url TEXT,
    license_type VARCHAR(50),
    primary_url TEXT,

    -- Organizational Metadata
    publisher_org VARCHAR(200),
    publisher_suborg VARCHAR(200),
    contact_name VARCHAR(200),
    contact_email VARCHAR(200),
    bureau_code VARCHAR(20),
    program_code VARCHAR(20),
    region_code VARCHAR(2),
    forest_code VARCHAR(4),
    district_code VARCHAR(6),

    -- Quality Metadata
    completeness TEXT,
    accuracy TEXT,
    data_source VARCHAR(200),
    lineage TEXT,
    quality_score DECIMAL(3,2) CHECK (quality_score >= 0 AND quality_score <= 1),

    -- Search Optimization
    search_vector tsvector,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(source_system, source_identifier)
);

-- Indexes
CREATE INDEX idx_datasets_source ON datasets(source_system);
CREATE INDEX idx_datasets_title ON datasets USING gin(title gin_trgm_ops);
CREATE INDEX idx_datasets_description ON datasets USING gin(description gin_trgm_ops);
CREATE INDEX idx_datasets_spatial ON datasets USING gist(spatial_extent);
CREATE INDEX idx_datasets_temporal ON datasets(temporal_extent_start, temporal_extent_end);
CREATE INDEX idx_datasets_modified ON datasets(modified_date DESC);
CREATE INDEX idx_datasets_org ON datasets(region_code, forest_code, district_code);
CREATE INDEX idx_datasets_search ON datasets USING gin(search_vector);
CREATE INDEX idx_datasets_quality ON datasets(quality_score DESC);

-- Trigger for search vector
CREATE OR REPLACE FUNCTION datasets_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(NEW.abstract, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_datasets_search_vector
BEFORE INSERT OR UPDATE ON datasets
FOR EACH ROW EXECUTE FUNCTION datasets_search_vector_update();

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### services

```sql
CREATE TABLE services (
    -- Inherits from datasets
    service_id UUID PRIMARY KEY REFERENCES datasets(dataset_id) ON DELETE CASCADE,

    -- Service-Specific Metadata
    service_type VARCHAR(50) CHECK (service_type IN ('MapService', 'FeatureService', 'ImageService')),
    service_version VARCHAR(50),
    cim_version VARCHAR(50),
    map_name VARCHAR(200),
    capabilities TEXT[], -- Array: Map, Query, Data, etc.
    supported_formats TEXT[], -- Array: JSON, geoJSON, PBF, etc.
    supported_extensions TEXT[], -- Array: KmlServer, WMSServer, etc.

    -- Service Configuration
    supports_dynamic_layers BOOLEAN DEFAULT false,
    single_fused_map_cache BOOLEAN DEFAULT false,
    export_tiles_allowed BOOLEAN DEFAULT false,
    max_record_count INTEGER,
    max_image_height INTEGER,
    max_image_width INTEGER,

    -- Temporal Configuration
    time_enabled BOOLEAN DEFAULT false,
    time_extent_start BIGINT, -- milliseconds since epoch
    time_extent_end BIGINT,
    default_time_interval INTEGER,
    default_time_interval_units VARCHAR(50),
    has_live_data BOOLEAN DEFAULT false,

    -- Extent Information (in service's spatial reference)
    initial_extent_xmin DOUBLE PRECISION,
    initial_extent_ymin DOUBLE PRECISION,
    initial_extent_xmax DOUBLE PRECISION,
    initial_extent_ymax DOUBLE PRECISION,
    full_extent_xmin DOUBLE PRECISION,
    full_extent_ymin DOUBLE PRECISION,
    full_extent_xmax DOUBLE PRECISION,
    full_extent_ymax DOUBLE PRECISION,

    -- Spatial Reference
    wkid INTEGER,
    latest_wkid INTEGER,

    -- Counts
    layer_count INTEGER,
    table_count INTEGER,

    -- Metadata
    copyright_text TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_services_type ON services(service_type);
CREATE INDEX idx_services_capabilities ON services USING gin(capabilities);
CREATE INDEX idx_services_time ON services(time_enabled, time_extent_start, time_extent_end);
```

#### layers

```sql
CREATE TABLE layers (
    layer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID NOT NULL REFERENCES services(service_id) ON DELETE CASCADE,

    -- Layer Identity
    layer_index INTEGER NOT NULL, -- ID within service (0, 1, 2, ...)
    layer_name VARCHAR(500) NOT NULL,
    layer_type VARCHAR(50) CHECK (layer_type IN ('Feature Layer', 'Group Layer', 'Table')),

    -- Hierarchy
    parent_layer_id UUID REFERENCES layers(layer_id) ON DELETE CASCADE,
    hierarchy_level INTEGER DEFAULT 0,

    -- Feature Information
    geometry_type VARCHAR(50) CHECK (geometry_type IN ('Point', 'Polyline', 'Polygon', 'Multipoint', 'None')),
    feature_count INTEGER,

    -- Visibility Configuration
    default_visibility BOOLEAN DEFAULT true,
    min_scale DOUBLE PRECISION,
    max_scale DOUBLE PRECISION,

    -- Capabilities
    supports_dynamic_legends BOOLEAN DEFAULT true,

    -- Description
    description TEXT,
    definition_expression TEXT, -- SQL filter

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(service_id, layer_index)
);

CREATE INDEX idx_layers_service ON layers(service_id);
CREATE INDEX idx_layers_parent ON layers(parent_layer_id);
CREATE INDEX idx_layers_type ON layers(layer_type, geometry_type);
CREATE INDEX idx_layers_name ON layers USING gin(layer_name gin_trgm_ops);
```

#### research_datasets

```sql
CREATE TABLE research_datasets (
    -- Inherits from datasets
    research_id UUID PRIMARY KEY REFERENCES datasets(dataset_id) ON DELETE CASCADE,

    -- DOI
    doi VARCHAR(200) UNIQUE NOT NULL,

    -- Research-Specific
    experimental_site VARCHAR(200),
    edition_number INTEGER DEFAULT 1,
    methodology TEXT,
    scientific_objectives TEXT,

    -- Data Collection Period
    data_collection_start DATE,
    data_collection_end DATE,

    -- Funding
    funding_programs TEXT[], -- Array of funding sources

    -- Related Editions
    previous_edition_doi VARCHAR(200),
    superseded_by_doi VARCHAR(200),

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_research_doi ON research_datasets(doi);
CREATE INDEX idx_research_site ON research_datasets(experimental_site);
CREATE INDEX idx_research_funding ON research_datasets USING gin(funding_programs);
CREATE INDEX idx_research_collection_period ON research_datasets(data_collection_start, data_collection_end);
```

### 5.2 Supporting Tables

#### keywords

```sql
CREATE TABLE keywords (
    keyword_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term VARCHAR(200) UNIQUE NOT NULL,
    category VARCHAR(50) CHECK (category IN ('theme', 'place', 'temporal', 'taxon', 'instrument', 'other')),
    controlled_vocabulary VARCHAR(200), -- e.g., "ISO 19115 Topic Categories"
    definition TEXT,
    use_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_keywords_term ON keywords USING gin(term gin_trgm_ops);
CREATE INDEX idx_keywords_category ON keywords(category);
CREATE INDEX idx_keywords_vocab ON keywords(controlled_vocabulary);
CREATE INDEX idx_keywords_use_count ON keywords(use_count DESC);
```

#### dataset_keywords

```sql
CREATE TABLE dataset_keywords (
    dataset_id UUID REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    keyword_id UUID REFERENCES keywords(keyword_id) ON DELETE CASCADE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (dataset_id, keyword_id)
);

CREATE INDEX idx_dataset_keywords_dataset ON dataset_keywords(dataset_id);
CREATE INDEX idx_dataset_keywords_keyword ON dataset_keywords(keyword_id);
```

#### themes

```sql
CREATE TABLE themes (
    theme_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_code VARCHAR(100) UNIQUE NOT NULL,
    theme_name VARCHAR(200) NOT NULL,
    parent_theme_id UUID REFERENCES themes(theme_id),
    hierarchy_level INTEGER DEFAULT 0,
    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert hierarchical themes
INSERT INTO themes (theme_code, theme_name, hierarchy_level) VALUES
('fire_management', 'Fire Management', 0),
('fire_occurrence', 'Fire Occurrence', 1),
('fire_perimeter', 'Fire Perimeters', 1),
('fire_hazard', 'Fire Hazard', 1),
('fuel_treatment', 'Fuel Treatments', 1),
('vegetation', 'Vegetation', 0),
('forest_inventory', 'Forest Inventory', 1),
('vegetation_classification', 'Vegetation Classification', 1),
('invasive_species', 'Invasive Species', 1),
('water', 'Water Resources', 0),
('hydrology', 'Hydrology', 1),
('watersheds', 'Watersheds', 1),
('water_quality', 'Water Quality', 1),
('aquatic_habitat', 'Aquatic Habitat', 1),
('wildlife', 'Wildlife', 0),
('wildlife_habitat', 'Wildlife Habitat', 1),
('species_inventory', 'Species Inventory', 1),
('threatened_endangered', 'Threatened & Endangered Species', 1),
('recreation', 'Recreation', 0),
('trails', 'Trails', 1),
('campgrounds', 'Campgrounds', 1),
('recreation_sites', 'Recreation Sites', 1),
('visitor_use', 'Visitor Use', 1),
('boundaries', 'Boundaries', 0),
('administrative', 'Administrative Boundaries', 1),
('ownership', 'Ownership', 1),
('designation', 'Designated Areas', 1),
('survey', 'Survey & Cadastral', 1);

-- Update parent relationships
UPDATE themes SET parent_theme_id = (SELECT theme_id FROM themes WHERE theme_code = 'fire_management')
WHERE theme_code IN ('fire_occurrence', 'fire_perimeter', 'fire_hazard', 'fuel_treatment');

UPDATE themes SET parent_theme_id = (SELECT theme_id FROM themes WHERE theme_code = 'vegetation')
WHERE theme_code IN ('forest_inventory', 'vegetation_classification', 'invasive_species');

-- (Continue for other hierarchies...)

CREATE INDEX idx_themes_parent ON themes(parent_theme_id);
CREATE INDEX idx_themes_code ON themes(theme_code);
```

#### dataset_themes

```sql
CREATE TABLE dataset_themes (
    dataset_id UUID REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    theme_id UUID REFERENCES themes(theme_id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 1.0 CHECK (relevance_score >= 0 AND relevance_score <= 1),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (dataset_id, theme_id)
);

CREATE INDEX idx_dataset_themes_dataset ON dataset_themes(dataset_id);
CREATE INDEX idx_dataset_themes_theme ON dataset_themes(theme_id);
CREATE INDEX idx_dataset_themes_relevance ON dataset_themes(relevance_score DESC);
```

#### organizations

```sql
CREATE TABLE organizations (
    org_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_code VARCHAR(10) UNIQUE NOT NULL, -- e.g., "01", "0117", "011702"
    org_name VARCHAR(200) NOT NULL,
    org_type VARCHAR(50) CHECK (org_type IN ('agency', 'region', 'forest', 'district', 'research_station', 'other')),
    parent_org_id UUID REFERENCES organizations(org_id),
    hierarchy_level INTEGER DEFAULT 0,

    -- Contact Information
    headquarters_city VARCHAR(100),
    headquarters_state VARCHAR(2),
    phone VARCHAR(20),
    email VARCHAR(200),
    website TEXT,

    -- Spatial
    boundary_geom GEOMETRY(MultiPolygon, 4326),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Forest Service organizational hierarchy
INSERT INTO organizations (org_code, org_name, org_type, hierarchy_level) VALUES
('USFS', 'U.S. Forest Service', 'agency', 0);

INSERT INTO organizations (org_code, org_name, org_type, hierarchy_level, parent_org_id) VALUES
('01', 'Northern Region', 'region', 1, (SELECT org_id FROM organizations WHERE org_code = 'USFS')),
('02', 'Rocky Mountain Region', 'region', 1, (SELECT org_id FROM organizations WHERE org_code = 'USFS')),
('03', 'Southwestern Region', 'region', 1, (SELECT org_id FROM organizations WHERE org_code = 'USFS')),
('04', 'Intermountain Region', 'region', 1, (SELECT org_id FROM organizations WHERE org_code = 'USFS')),
('05', 'Pacific Southwest Region', 'region', 1, (SELECT org_id FROM organizations WHERE org_code = 'USFS')),
('06', 'Pacific Northwest Region', 'region', 1, (SELECT org_id FROM organizations WHERE org_code = 'USFS')),
('08', 'Southern Region', 'region', 1, (SELECT org_id FROM organizations WHERE org_code = 'USFS')),
('09', 'Eastern Region', 'region', 1, (SELECT org_id FROM organizations WHERE org_code = 'USFS')),
('10', 'Alaska Region', 'region', 1, (SELECT org_id FROM organizations WHERE org_code = 'USFS'));

-- Example forests in Region 01
INSERT INTO organizations (org_code, org_name, org_type, hierarchy_level, parent_org_id) VALUES
('0117', 'Nez Perce-Clearwater National Forests', 'forest', 2, (SELECT org_id FROM organizations WHERE org_code = '01'));

-- Example districts
INSERT INTO organizations (org_code, org_name, org_type, hierarchy_level, parent_org_id) VALUES
('011701', 'Clearwater Ranger District', 'district', 3, (SELECT org_id FROM organizations WHERE org_code = '0117')),
('011702', 'Nez Perce Ranger District', 'district', 3, (SELECT org_id FROM organizations WHERE org_code = '0117'));

CREATE INDEX idx_orgs_code ON organizations(org_code);
CREATE INDEX idx_orgs_parent ON organizations(parent_org_id);
CREATE INDEX idx_orgs_type ON organizations(org_type);
CREATE INDEX idx_orgs_name ON organizations USING gin(org_name gin_trgm_ops);
CREATE INDEX idx_orgs_boundary ON organizations USING gist(boundary_geom);
```

#### distributions

```sql
CREATE TABLE distributions (
    distribution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,

    distribution_type VARCHAR(50) CHECK (distribution_type IN ('download', 'api', 'webService', 'webPage', 'metadata')),
    format VARCHAR(100), -- CSV, GeoJSON, Shapefile, REST API, etc.
    media_type VARCHAR(100), -- MIME type
    access_url TEXT NOT NULL,
    conforms_to TEXT, -- Standard URL (e.g., ISO-19139)

    title VARCHAR(300),
    description TEXT,

    -- Size and Performance
    size_bytes BIGINT,
    compression VARCHAR(50),

    -- Availability
    is_primary BOOLEAN DEFAULT false,
    status VARCHAR(20) CHECK (status IN ('active', 'deprecated', 'unavailable')) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_distributions_dataset ON distributions(dataset_id);
CREATE INDEX idx_distributions_type ON distributions(distribution_type);
CREATE INDEX idx_distributions_format ON distributions(format);
CREATE INDEX idx_distributions_primary ON distributions(dataset_id, is_primary) WHERE is_primary = true;
CREATE INDEX idx_distributions_status ON distributions(status);
```

### 5.3 Search and Analytics Tables

#### dataset_embeddings

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE dataset_embeddings (
    dataset_id UUID PRIMARY KEY REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    embedding vector(384), -- Dimension depends on model (384 for all-MiniLM-L6-v2)
    model_name VARCHAR(100) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vector similarity index (IVFFlat for fast approximate search)
CREATE INDEX idx_embedding_ivfflat ON dataset_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- For exact search (slower but accurate)
-- CREATE INDEX idx_embedding_hnsw ON dataset_embeddings
-- USING hnsw (embedding vector_cosine_ops);
```

#### search_logs

```sql
CREATE TABLE search_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    user_id UUID, -- nullable for anonymous users

    -- Query Information
    query_text TEXT NOT NULL,
    query_intent VARCHAR(50), -- DISCOVER, SCHEMA, LOCATE, etc.
    parsed_entities JSONB, -- Extracted entities

    -- Results
    result_count INTEGER,
    result_dataset_ids UUID[], -- Array of returned dataset IDs

    -- User Interaction
    clicked_dataset_id UUID REFERENCES datasets(dataset_id),
    click_rank INTEGER, -- Position in results (1, 2, 3, ...)
    time_to_click INTERVAL, -- Time from search to click

    -- Context
    client_ip INET,
    user_agent TEXT,
    referrer TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_logs_session ON search_logs(session_id);
CREATE INDEX idx_search_logs_user ON search_logs(user_id);
CREATE INDEX idx_search_logs_query ON search_logs USING gin(to_tsvector('english', query_text));
CREATE INDEX idx_search_logs_clicked ON search_logs(clicked_dataset_id);
CREATE INDEX idx_search_logs_created ON search_logs(created_at DESC);
```

#### dataset_views

```sql
CREATE TABLE dataset_views (
    view_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    user_id UUID,

    view_duration INTERVAL,
    scrolled_to_bottom BOOLEAN DEFAULT false,
    downloaded BOOLEAN DEFAULT false,
    bookmarked BOOLEAN DEFAULT false,

    referrer_dataset_id UUID REFERENCES datasets(dataset_id), -- If navigated from another dataset

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dataset_views_dataset ON dataset_views(dataset_id);
CREATE INDEX idx_dataset_views_user ON dataset_views(user_id);
CREATE INDEX idx_dataset_views_session ON dataset_views(session_id);
CREATE INDEX idx_dataset_views_created ON dataset_views(created_at DESC);
```

#### dataset_statistics

```sql
CREATE TABLE dataset_statistics (
    dataset_id UUID PRIMARY KEY REFERENCES datasets(dataset_id) ON DELETE CASCADE,

    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    bookmark_count INTEGER DEFAULT 0,
    search_appearance_count INTEGER DEFAULT 0,
    search_click_count INTEGER DEFAULT 0,
    average_click_rank DECIMAL(5,2),

    last_viewed_at TIMESTAMP,
    last_downloaded_at TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dataset_stats_views ON dataset_statistics(view_count DESC);
CREATE INDEX idx_dataset_stats_downloads ON dataset_statistics(download_count DESC);
CREATE INDEX idx_dataset_stats_popularity ON dataset_statistics((view_count + download_count * 5) DESC);
```

---

## 6. Pydantic Data Models

### 6.1 Core Models

```python
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, EmailStr, UUID4, field_validator
from pydantic_geojson import FeatureCollectionModel, PolygonModel


# Enums

class SourceSystem(str, Enum):
    """Source metadata system"""
    FSGEODATA = "fsgeodata"
    DATAHUB = "datahub"
    EDW_SERVICES = "edw_services"
    RDA = "rda"


class UpdateFrequency(str, Enum):
    """Dataset update frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"
    AS_NEEDED = "asNeeded"
    IRREGULAR = "irregular"
    NONE = "none"
    UNKNOWN = "unknown"


class AccessLevel(str, Enum):
    """Data access level"""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PRIVATE = "private"


class LicenseType(str, Enum):
    """License types"""
    CC_BY_2_0 = "CC-BY-2.0"
    CC_BY_4_0 = "CC-BY-4.0"
    PUBLIC_DOMAIN = "publicDomain"
    GOVERNMENT_WORKS = "governmentWorks"
    OTHER = "other"


class ServiceType(str, Enum):
    """ArcGIS service types"""
    MAP_SERVICE = "MapService"
    FEATURE_SERVICE = "FeatureService"
    IMAGE_SERVICE = "ImageService"


class LayerType(str, Enum):
    """Layer types"""
    FEATURE_LAYER = "Feature Layer"
    GROUP_LAYER = "Group Layer"
    TABLE = "Table"


class GeometryType(str, Enum):
    """Geometry types"""
    POINT = "Point"
    POLYLINE = "Polyline"
    POLYGON = "Polygon"
    MULTIPOINT = "Multipoint"
    NONE = "None"


class DistributionType(str, Enum):
    """Distribution types"""
    DOWNLOAD = "download"
    API = "api"
    WEB_SERVICE = "webService"
    WEB_PAGE = "webPage"
    METADATA = "metadata"


class KeywordCategory(str, Enum):
    """Keyword categories"""
    THEME = "theme"
    PLACE = "place"
    TEMPORAL = "temporal"
    TAXON = "taxon"
    INSTRUMENT = "instrument"
    OTHER = "other"


class QueryIntent(str, Enum):
    """User query intents"""
    DISCOVER = "DISCOVER"
    SCHEMA = "SCHEMA"
    LOCATE = "LOCATE"
    COMPARE = "COMPARE"
    RELATE = "RELATE"
    DOWNLOAD = "DOWNLOAD"
    METADATA = "METADATA"
    TEMPORAL = "TEMPORAL"
    QUALITY = "QUALITY"


# Supporting Models

class SpatialExtent(BaseModel):
    """Spatial bounding box"""
    west: float = Field(..., description="Western longitude", ge=-180, le=180)
    south: float = Field(..., description="Southern latitude", ge=-90, le=90)
    east: float = Field(..., description="Eastern longitude", ge=-180, le=180)
    north: float = Field(..., description="Northern latitude", ge=-90, le=90)

    @field_validator('east')
    @classmethod
    def validate_extent(cls, v, info):
        if info.data.get('west') and v < info.data['west']:
            raise ValueError('East must be greater than west')
        return v

    def to_bbox(self) -> List[float]:
        """Convert to bounding box array [west, south, east, north]"""
        return [self.west, self.south, self.east, self.north]

    def to_wkt(self) -> str:
        """Convert to WKT polygon"""
        return (f"POLYGON(({self.west} {self.south}, {self.east} {self.south}, "
                f"{self.east} {self.north}, {self.west} {self.north}, {self.west} {self.south}))")


class TemporalExtent(BaseModel):
    """Temporal coverage"""
    start: Optional[date] = Field(None, description="Start date")
    end: Optional[date] = Field(None, description="End date")

    @field_validator('end')
    @classmethod
    def validate_temporal(cls, v, info):
        if v and info.data.get('start') and v < info.data['start']:
            raise ValueError('End date must be after start date')
        return v


class Organization(BaseModel):
    """Organization information"""
    org_id: Optional[UUID4] = None
    org_code: str = Field(..., description="Organization code (e.g., '01', '0117')")
    org_name: str = Field(..., description="Organization name")
    org_type: str = Field(..., description="Organization type")
    parent_org_id: Optional[UUID4] = None
    hierarchy_level: int = Field(0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "org_code": "0117",
                "org_name": "Nez Perce-Clearwater National Forests",
                "org_type": "forest",
                "hierarchy_level": 2
            }
        }


class ContactPoint(BaseModel):
    """Contact information"""
    name: str
    email: EmailStr
    phone: Optional[str] = None


class Keyword(BaseModel):
    """Keyword/tag"""
    keyword_id: Optional[UUID4] = None
    term: str
    category: Optional[KeywordCategory] = None
    controlled_vocabulary: Optional[str] = None
    definition: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "term": "fire occurrence",
                "category": "theme",
                "controlled_vocabulary": "ISO 19115 Topic Categories"
            }
        }


class Distribution(BaseModel):
    """Data distribution/access point"""
    distribution_id: Optional[UUID4] = None
    distribution_type: DistributionType
    format: Optional[str] = Field(None, description="Format (CSV, GeoJSON, etc.)")
    media_type: Optional[str] = Field(None, description="MIME type")
    access_url: HttpUrl = Field(..., description="Access URL")
    conforms_to: Optional[HttpUrl] = Field(None, description="Standard conformance URL")
    title: Optional[str] = None
    description: Optional[str] = None
    size_bytes: Optional[int] = Field(None, ge=0)
    is_primary: bool = False
    status: str = "active"

    class Config:
        json_schema_extra = {
            "example": {
                "distribution_type": "api",
                "format": "ArcGIS REST API",
                "media_type": "application/json",
                "access_url": "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_FireOccurrence/MapServer",
                "is_primary": True
            }
        }


class QualityMetadata(BaseModel):
    """Data quality information"""
    completeness: Optional[str] = None
    accuracy: Optional[str] = None
    data_source: Optional[str] = None
    lineage: Optional[str] = None
    quality_score: Optional[float] = Field(None, ge=0, le=1)


# Core Models

class Dataset(BaseModel):
    """Unified dataset model"""
    # Identity
    dataset_id: UUID4 = Field(default_factory=lambda: __import__('uuid').uuid4())
    source_system: SourceSystem
    source_identifier: str
    source_url: Optional[HttpUrl] = None

    # Basic Metadata
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    abstract: Optional[str] = None
    purpose: Optional[str] = None

    # Keywords and Themes
    keywords: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)

    # Temporal
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    temporal_extent: Optional[TemporalExtent] = None
    update_frequency: Optional[UpdateFrequency] = None

    # Spatial
    spatial_extent: Optional[SpatialExtent] = None
    coordinate_system: Optional[str] = Field(None, description="EPSG code")
    spatial_resolution: Optional[str] = None
    geographic_coverage: List[str] = Field(default_factory=list, description="Place names")

    # Access
    access_level: AccessLevel = AccessLevel.PUBLIC
    license_url: Optional[HttpUrl] = None
    license_type: Optional[LicenseType] = None
    primary_url: Optional[HttpUrl] = None
    distributions: List[Distribution] = Field(default_factory=list)

    # Organization
    publisher_org: Optional[str] = None
    publisher_suborg: Optional[str] = None
    contact_point: Optional[ContactPoint] = None
    bureau_code: Optional[str] = None
    program_code: Optional[str] = None
    region_code: Optional[str] = Field(None, pattern=r"^0[1-6,8-9]|10$")
    forest_code: Optional[str] = None
    district_code: Optional[str] = None

    # Quality
    quality: Optional[QualityMetadata] = None

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "source_system": "fsgeodata",
                "source_identifier": "S_USA.Activity_HazFuelTrt_PL",
                "title": "Hazardous Fuel Treatments - Polygon",
                "description": "Activities of hazardous fuel treatment reduction...",
                "keywords": ["Vegetation Management", "Fuel Treatment"],
                "themes": ["fire_management", "fuel_treatment"],
                "access_level": "public",
                "publisher_org": "U.S. Forest Service",
                "region_code": "01"
            }
        }


class Service(Dataset):
    """ArcGIS service (extends Dataset)"""
    service_type: ServiceType
    service_version: Optional[str] = None
    cim_version: Optional[str] = None
    map_name: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    supported_formats: List[str] = Field(default_factory=list)
    supported_extensions: List[str] = Field(default_factory=list)

    # Configuration
    supports_dynamic_layers: bool = False
    single_fused_map_cache: bool = False
    export_tiles_allowed: bool = False
    max_record_count: Optional[int] = None
    max_image_height: Optional[int] = None
    max_image_width: Optional[int] = None

    # Temporal
    time_enabled: bool = False
    time_extent_start: Optional[int] = None
    time_extent_end: Optional[int] = None
    default_time_interval: Optional[int] = None
    default_time_interval_units: Optional[str] = None
    has_live_data: bool = False

    # Counts
    layer_count: Optional[int] = None
    table_count: Optional[int] = None

    copyright_text: Optional[str] = None


class Layer(BaseModel):
    """Service layer"""
    layer_id: UUID4 = Field(default_factory=lambda: __import__('uuid').uuid4())
    service_id: UUID4
    layer_index: int = Field(..., ge=0)
    layer_name: str
    layer_type: LayerType
    parent_layer_id: Optional[UUID4] = None
    hierarchy_level: int = Field(0, ge=0)

    geometry_type: Optional[GeometryType] = None
    feature_count: Optional[int] = Field(None, ge=0)

    default_visibility: bool = True
    min_scale: Optional[float] = None
    max_scale: Optional[float] = None

    supports_dynamic_legends: bool = True
    description: Optional[str] = None
    definition_expression: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ResearchDataset(Dataset):
    """Research dataset (extends Dataset)"""
    doi: str = Field(..., pattern=r"^https://doi.org/10\.2737/RDS-\d{4}-\d{4}(-\d)?$")
    experimental_site: Optional[str] = None
    edition_number: int = Field(1, ge=1)
    methodology: Optional[str] = None
    scientific_objectives: Optional[str] = None
    data_collection_period: Optional[TemporalExtent] = None
    funding_programs: List[str] = Field(default_factory=list)
    previous_edition_doi: Optional[str] = None
    superseded_by_doi: Optional[str] = None


# Search and Query Models

class ParsedQuery(BaseModel):
    """Parsed natural language query"""
    original_query: str
    intent: Optional[QueryIntent] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(1.0, ge=0, le=1)


class SearchResult(BaseModel):
    """Search result item"""
    dataset: Dataset
    score: float = Field(..., ge=0, le=1)
    highlights: Dict[str, List[str]] = Field(default_factory=dict)
    explanation: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    parsed_query: Optional[ParsedQuery] = None
    total_results: int
    results: List[SearchResult]
    facets: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)
    execution_time_ms: float


# Transformation Functions

def fgdc_xml_to_dataset(xml_dict: Dict[str, Any]) -> Dataset:
    """Transform FGDC XML metadata to Dataset model"""
    idinfo = xml_dict.get('metadata', {}).get('idinfo', {})
    citation = idinfo.get('citation', {}).get('citeinfo', {})

    # Extract spatial extent
    spdom = idinfo.get('spdom', {}).get('bounding', {})
    spatial_extent = None
    if spdom:
        spatial_extent = SpatialExtent(
            west=float(spdom.get('westbc', 0)),
            south=float(spdom.get('southbc', 0)),
            east=float(spdom.get('eastbc', 0)),
            north=float(spdom.get('northbc', 0))
        )

    # Extract keywords
    keywords_section = idinfo.get('keywords', {}).get('theme', [])
    if not isinstance(keywords_section, list):
        keywords_section = [keywords_section]
    keywords = []
    for theme in keywords_section:
        themekeys = theme.get('themekey', [])
        if not isinstance(themekeys, list):
            themekeys = [themekeys]
        keywords.extend(themekeys)

    return Dataset(
        source_system=SourceSystem.FSGEODATA,
        source_identifier=citation.get('title', ''),
        title=citation.get('title', ''),
        description=idinfo.get('descript', {}).get('abstract', ''),
        purpose=idinfo.get('descript', {}).get('purpose'),
        keywords=keywords,
        spatial_extent=spatial_extent,
        publisher_org=citation.get('origin', ''),
        primary_url=citation.get('onlink'),
        access_level=AccessLevel.PUBLIC,
        quality=QualityMetadata(
            completeness=xml_dict.get('metadata', {}).get('dataqual', {}).get('complete'),
            accuracy=xml_dict.get('metadata', {}).get('dataqual', {}).get('posacc', {}).get('horizpa', {}).get('horizpar'),
            lineage=xml_dict.get('metadata', {}).get('dataqual', {}).get('lineage', {}).get('procstep', {}).get('procdesc')
        )
    )


def dcat_json_to_dataset(dcat_dict: Dict[str, Any], source: SourceSystem) -> Dataset:
    """Transform DCAT JSON metadata to Dataset model"""

    # Parse spatial extent string: "minX,minY,maxX,maxY"
    spatial_extent = None
    if 'spatial' in dcat_dict:
        coords = [float(x) for x in dcat_dict['spatial'].split(',')]
        if len(coords) == 4:
            spatial_extent = SpatialExtent(
                west=coords[0], south=coords[1],
                east=coords[2], north=coords[3]
            )

    # Parse distributions
    distributions = []
    for dist in dcat_dict.get('distribution', []):
        distributions.append(Distribution(
            distribution_type=DistributionType.WEB_PAGE if dist.get('format') == 'Web Page' else DistributionType.API,
            format=dist.get('format'),
            media_type=dist.get('mediaType'),
            access_url=dist.get('accessURL'),
            conforms_to=dist.get('conformsTo'),
            title=dist.get('title')
        ))

    # Parse dates
    modified_date = None
    if 'modified' in dcat_dict:
        try:
            modified_date = datetime.fromisoformat(dcat_dict['modified'].replace('Z', '+00:00'))
        except:
            pass

    return Dataset(
        source_system=source,
        source_identifier=dcat_dict.get('identifier', ''),
        source_url=dcat_dict.get('identifier'),
        title=dcat_dict.get('title', ''),
        description=dcat_dict.get('description', ''),
        keywords=dcat_dict.get('keyword', []),
        themes=dcat_dict.get('theme', []),
        modified_date=modified_date,
        spatial_extent=spatial_extent,
        access_level=AccessLevel(dcat_dict.get('accessLevel', 'public')),
        license_url=dcat_dict.get('license'),
        primary_url=dcat_dict.get('landingPage'),
        distributions=distributions,
        publisher_org=dcat_dict.get('publisher', {}).get('name'),
        contact_point=ContactPoint(
            name=dcat_dict.get('contactPoint', {}).get('fn', 'Unknown'),
            email=dcat_dict.get('contactPoint', {}).get('hasEmail', '').replace('mailto:', '')
        ) if 'contactPoint' in dcat_dict else None,
        bureau_code=dcat_dict.get('bureauCode', [None])[0],
        program_code=dcat_dict.get('programCode', [None])[0]
    )


def arcgis_service_to_service(service_dict: Dict[str, Any]) -> Service:
    """Transform ArcGIS REST API service JSON to Service model"""

    # Determine service type from capabilities or endpoint
    service_type = ServiceType.MAP_SERVICE
    if 'FeatureServer' in service_dict.get('serviceDescription', ''):
        service_type = ServiceType.FEATURE_SERVICE
    elif 'ImageServer' in service_dict.get('serviceDescription', ''):
        service_type = ServiceType.IMAGE_SERVICE

    # Extract capabilities
    capabilities = service_dict.get('capabilities', '').split(',')

    # Count layers
    layers = service_dict.get('layers', [])
    tables = service_dict.get('tables', [])

    return Service(
        source_system=SourceSystem.EDW_SERVICES,
        source_identifier=service_dict.get('mapName', ''),
        title=service_dict.get('documentInfo', {}).get('Title', service_dict.get('mapName', '')),
        description=service_dict.get('serviceDescription', ''),
        keywords=service_dict.get('documentInfo', {}).get('Keywords', '').split(','),
        service_type=service_type,
        service_version=str(service_dict.get('currentVersion', '')),
        cim_version=service_dict.get('cimVersion'),
        map_name=service_dict.get('mapName'),
        capabilities=capabilities,
        supported_formats=service_dict.get('supportedQueryFormats', '').split(','),
        supports_dynamic_layers=service_dict.get('supportsDynamicLayers', False),
        max_record_count=service_dict.get('maxRecordCount'),
        time_enabled='timeInfo' in service_dict,
        layer_count=len(layers),
        table_count=len(tables),
        copyright_text=service_dict.get('copyrightText'),
        access_level=AccessLevel.PUBLIC,
        publisher_org="U.S. Forest Service",
        publisher_suborg="Enterprise Data Warehouse"
    )


# Example Usage
if __name__ == "__main__":
    # Create a sample dataset
    dataset = Dataset(
        source_system=SourceSystem.FSGEODATA,
        source_identifier="S_USA.Activity_HazFuelTrt_PL",
        title="Hazardous Fuel Treatments - Polygon",
        description="Activities of hazardous fuel treatment reduction that are polygons...",
        keywords=["Vegetation Management", "Fuel Treatment", "Ecosystem Restoration"],
        themes=["fire_management", "fuel_treatment"],
        spatial_extent=SpatialExtent(west=-151.56, south=0.0004, east=-51.81, north=85.41),
        coordinate_system="EPSG:4269",
        access_level=AccessLevel.PUBLIC,
        publisher_org="U.S. Forest Service",
        region_code="01",
        distributions=[
            Distribution(
                distribution_type=DistributionType.API,
                format="ArcGIS REST API",
                media_type="application/json",
                access_url="https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_HazFuelTrt/MapServer",
                is_primary=True
            )
        ]
    )

    # Serialize to JSON
    print(dataset.model_dump_json(indent=2))

    # Validate
    print(f"\nValidation successful: {dataset.title}")
```

---

## 7. Implementation Recommendations

### 7.1 Architecture Overview

**Recommended Stack**:
- **Database**: PostgreSQL 15+ with PostGIS and pgvector extensions
- **Search Engine**: Elasticsearch 8.x or OpenSearch 2.x
- **Vector Database**: pgvector (embedded in PostgreSQL) or dedicated (Pinecone, Weaviate)
- **API Framework**: FastAPI (Python) or Express.js (Node.js)
- **LLM**: OpenAI GPT-4 or Anthropic Claude (API), with local fallback (Llama 2/3)
- **Frontend**: React with TypeScript, Leaflet/OpenLayers for maps
- **Caching**: Redis for query caching and session management
- **Message Queue**: RabbitMQ or Apache Kafka for ETL pipelines

**System Components**:
```
┌─────────────────┐
│  User Interface │ (React + Maps)
└────────┬────────┘
         │
┌────────▼────────┐
│   API Gateway   │ (FastAPI/Express)
└────┬───┬───┬────┘
     │   │   │
     │   │   └────────┐
     │   │            │
┌────▼───▼──────┐ ┌──▼──────────┐
│ Search Engine │ │ Vector Store│
│ (Elasticsearch)│ │ (pgvector)  │
└───────────────┘ └─────────────┘
     │                  │
┌────▼──────────────────▼───┐
│   PostgreSQL + PostGIS    │
└──────────┬────────────────┘
           │
┌──────────▼────────────┐
│   LLM Service Layer   │
│ (Query Understanding, │
│  Metadata Enrichment) │
└──────────┬────────────┘
           │
┌──────────▼────────────┐
│    ETL Pipelines      │
│  (Data Ingestion)     │
└───────────────────────┘
```

### 7.2 Data Ingestion Pipeline

**ETL Process**:

1. **Extract**: Read from source metadata files
   - XML parser for fsgeodata (FGDC)
   - JSON parser for datahub, edw_services, rda (DCAT)

2. **Transform**: Map to unified model
   - Use Pydantic models for validation
   - Normalize spatial extents
   - Harmonize keywords and themes
   - Generate embeddings

3. **Load**: Insert into PostgreSQL
   - Bulk insert with transactions
   - Update Elasticsearch index
   - Update vector database

**Example Pipeline Code**:
```python
import asyncio
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET
import json

from models import Dataset, fgdc_xml_to_dataset, dcat_json_to_dataset
from database import db_session, elasticsearch_client
from embeddings import generate_embedding


async def ingest_fsgeodata(xml_path: Path) -> Dataset:
    """Ingest FGDC XML metadata"""
    tree = ET.parse(xml_path)
    xml_dict = xml_tree_to_dict(tree.getroot())
    dataset = fgdc_xml_to_dataset(xml_dict)

    # Generate embedding
    embedding_text = f"{dataset.title} {dataset.description}"
    dataset.embedding = await generate_embedding(embedding_text)

    return dataset


async def ingest_datahub(json_path: Path) -> List[Dataset]:
    """Ingest DCAT JSON metadata"""
    with open(json_path) as f:
        dcat_catalog = json.load(f)

    datasets = []
    for dcat_dataset in dcat_catalog['dataset']:
        dataset = dcat_json_to_dataset(dcat_dataset, SourceSystem.DATAHUB)
        embedding_text = f"{dataset.title} {dataset.description}"
        dataset.embedding = await generate_embedding(embedding_text)
        datasets.append(dataset)

    return datasets


async def ingest_all():
    """Main ingestion orchestrator"""
    tasks = []

    # Ingest fsgeodata
    fsgeodata_dir = Path("data/metadata/fsgeodata")
    for xml_file in fsgeodata_dir.glob("*.xml"):
        tasks.append(ingest_fsgeodata(xml_file))

    # Ingest datahub
    tasks.append(ingest_datahub(Path("data/metadata/datahub/metadata.json")))

    # Process concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Flatten and filter results
    datasets = []
    for result in results:
        if isinstance(result, list):
            datasets.extend(result)
        elif isinstance(result, Dataset):
            datasets.append(result)
        elif isinstance(result, Exception):
            print(f"Error: {result}")

    # Bulk insert
    await bulk_insert_datasets(datasets)
    print(f"Ingested {len(datasets)} datasets")


if __name__ == "__main__":
    asyncio.run(ingest_all())
```

### 7.3 Query Processing Flow

**Natural Language Query → Results**:

```
User Query: "Show me fire data for Region 5 from the last 10 years"
     │
     ▼
┌────────────────────┐
│ Intent Classifier  │ → Intent: DISCOVER
│ (LLM / Fine-tuned) │ → Domain: fire
└─────────┬──────────┘ → Location: Region 5
          │            → Temporal: last 10 years
          ▼
┌────────────────────┐
│ Entity Extractor   │ → {region: "05",
│  (NER / LLM)       │ →  themes: ["fire"],
└─────────┬──────────┘ →  start_year: 2015}
          │
          ▼
┌────────────────────┐
│ Query Builder      │ → SQL + Elasticsearch DSL
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Hybrid Search      │
│ - Keyword (BM25)   │
│ - Vector (cosine)  │
│ - Spatial (PostGIS)│
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Re-ranking         │ → Combine scores
│ - Relevance        │ → Apply boosting
│ - Recency          │ → Diversity
│ - Popularity       │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Response Generator │ → Facets
│ (LLM-enhanced)     │ → Suggestions
└─────────┬──────────┘ → Explanations
          │
          ▼
      Results JSON
```

### 7.4 API Endpoints

**REST API Design**:

```python
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from models import Dataset, SearchResponse, QueryIntent

app = FastAPI(title="USFS Data Catalog API", version="1.0.0")


@app.get("/api/datasets", response_model=SearchResponse)
async def search_datasets(
    q: str = Query(..., description="Search query"),
    themes: Optional[List[str]] = Query(None, description="Filter by themes"),
    region: Optional[str] = Query(None, pattern=r"^0[1-6,8-9]|10$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> SearchResponse:
    """
    Search datasets using natural language or structured queries.

    Examples:
    - /api/datasets?q=fire+data+region+5
    - /api/datasets?q=hazardous+fuel+treatments&region=01&limit=10
    """
    # Parse query with LLM
    parsed_query = await parse_query(q)

    # Build search
    results = await hybrid_search(
        query=q,
        parsed_query=parsed_query,
        filters={
            "themes": themes,
            "region_code": region,
            "temporal_start": start_date,
            "temporal_end": end_date
        },
        limit=limit,
        offset=offset
    )

    return results


@app.get("/api/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str):
    """Get detailed metadata for a specific dataset"""
    dataset = await db.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Log view
    await log_dataset_view(dataset_id)

    return dataset


@app.get("/api/datasets/{dataset_id}/schema")
async def get_dataset_schema(dataset_id: str):
    """Get field schema for a dataset"""
    schema = await db.get_dataset_schema(dataset_id)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")

    # Generate plain language explanations with LLM
    enhanced_schema = await enhance_schema_with_llm(schema)

    return enhanced_schema


@app.get("/api/datasets/{dataset_id}/related")
async def get_related_datasets(
    dataset_id: str,
    limit: int = Query(5, ge=1, le=20)
):
    """Get datasets related to this one"""
    related = await find_related_datasets(dataset_id, limit=limit)
    return related


@app.post("/api/query/parse")
async def parse_natural_language_query(query: str):
    """Parse a natural language query and return structured filters"""
    parsed = await parse_query(query)
    return parsed


@app.get("/api/suggest")
async def autocomplete_suggestions(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50)
):
    """Get autocomplete suggestions"""
    suggestions = await get_suggestions(q, limit=limit)
    return suggestions


@app.get("/api/facets")
async def get_facets(q: Optional[str] = None):
    """Get faceted counts for filtering"""
    facets = await get_faceted_counts(query=q)
    return facets


@app.get("/api/organizations")
async def list_organizations(
    org_type: Optional[str] = None,
    parent_org_code: Optional[str] = None
):
    """List organizations (regions, forests, districts)"""
    orgs = await db.list_organizations(
        org_type=org_type,
        parent_org_code=parent_org_code
    )
    return orgs


@app.get("/api/themes")
async def list_themes():
    """Get hierarchical theme taxonomy"""
    themes = await db.get_theme_hierarchy()
    return themes


@app.get("/api/stats")
async def get_statistics():
    """Get catalog statistics"""
    stats = await db.get_catalog_stats()
    return {
        "total_datasets": stats["dataset_count"],
        "by_source": stats["by_source"],
        "by_theme": stats["by_theme"],
        "by_region": stats["by_region"],
        "last_updated": stats["last_updated"]
    }
```

### 7.5 Deployment Strategy

**Phase 1: Foundation (Months 1-3)**
- Set up PostgreSQL with PostGIS and pgvector
- Implement core data models and ingestion pipelines
- Ingest all four metadata sources
- Basic search API (keyword only)
- Simple web UI for testing

**Phase 2: Search Enhancement (Months 4-6)**
- Integrate Elasticsearch
- Implement hybrid search (keyword + vector)
- Add spatial search capabilities
- Implement faceted navigation
- Enhanced UI with maps and filters

**Phase 3: LLM Integration (Months 7-9)**
- Integrate LLM for query understanding
- Implement intent classification and entity extraction
- Add query suggestions and refinements
- Automated metadata enrichment
- Plain language schema explanations

**Phase 4: Advanced Features (Months 10-12)**
- Recommendation system
- User personalization
- Analytics dashboard
- API rate limiting and authentication
- Performance optimization

**Phase 5: Production Hardening (Ongoing)**
- Load testing and optimization
- Security audits
- Monitoring and alerting
- Documentation and training
- Continuous metadata updates

### 7.6 Success Metrics

**Usage Metrics**:
- Unique visitors per month
- Search queries per day
- Dataset views and downloads
- API requests per day
- Average session duration

**Quality Metrics**:
- Search success rate (% queries with clicks)
- Average result relevance (click position)
- Query refinement rate (% queries refined)
- Zero-result queries (%)
- User satisfaction score (surveys)

**Data Metrics**:
- Total datasets indexed
- Metadata completeness score (average)
- Data freshness (% updated in last 30 days)
- Coverage by source system
- Geographic coverage

**Performance Metrics**:
- Query response time (p50, p95, p99)
- API availability (%)
- Embedding generation throughput
- Database query performance
- Cache hit rate

---

## Conclusion

This comprehensive analysis and design provides a complete blueprint for building an intelligent, conversational data catalog for USDA Forest Service metadata. The unified model accommodates all four source systems while enabling powerful natural language search, LLM-enhanced metadata enrichment, and user-friendly data discovery.

**Key Takeaways**:

1. **Unified Model**: Successfully integrates 1,791+ datasets from four diverse metadata sources
2. **Standards Compliance**: Maintains FGDC, DCAT, and ArcGIS REST API standard compatibility
3. **LLM Enhancement**: Leverages LLMs for query understanding, metadata enrichment, and schema explanation
4. **Conversational Interface**: Supports natural language queries with intelligent parsing and suggestions
5. **Scalable Architecture**: PostgreSQL + Elasticsearch + vector search enables sub-second query response
6. **Extensible Design**: Pydantic models and SQL schemas support easy addition of new sources

**Next Steps**:
1. Review and approve unified metadata model
2. Set up development environment and infrastructure
3. Begin Phase 1 implementation (foundation)
4. Pilot with subset of users for feedback
5. Iterate based on usage patterns and user needs
