# Football Stats API

A comprehensive REST API for football statistics from top 5 European leagues and European competitions, built with FastAPI and Neo4j.

## Features

- **Home Page Data**: Top scorers, top assisters, recent matches, league standings preview
- **Leagues**: Complete standings, clubs, statistics, top scorers
- **Competitions**: Match schedules by round, participants, statistics
- **Teams**: Full team profile, squad, matches, statistics
- **Players**: Player profiles, advanced statistics, search and filtering
- **Analysis**: Player comparisons, statistical rankings, demographic analysis

## Tech Stack

- **FastAPI**: Modern Python web framework
- **Neo4j**: Graph database for complex relationships
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

## Installation

### Prerequisites

- Python 3.8+
- Neo4j Database (running instance)
- pip

### Setup

1. **Clone the repository** (or create the project structure as shown)

2. **Create virtual environment**:
```bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the root directory:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
API_HOST=0.0.0.0
API_PORT=8000
```

5. **Ensure Neo4j is running** with your football data loaded

## Running the API

### Development Mode
```bash
# From project root
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints Overview

### Home
- `GET /api/home` - Get all home page data

### Players
- `GET /api/players/` - List players with filters
- `GET /api/players/search?q={name}` - Search players
- `GET /api/players/{name}` - Player profile
- `GET /api/players/top-scorers` - Top goal scorers
- `GET /api/players/top-assisters` - Top assist providers
- `POST /api/players/compare` - Compare multiple players

### Teams
- `GET /api/teams/{name}` - Team details
- `GET /api/teams/{name}/players` - Team squad
- `GET /api/teams/{name}/matches` - Team matches
- `GET /api/teams/{name}/top-players?metric=goals` - Top players by metric
- `GET /api/teams/{name}/stats` - Team statistics

### Leagues
- `GET /api/leagues/` - List all leagues
- `GET /api/leagues/{name}` - League details
- `GET /api/leagues/{name}/standings` - League table
- `GET /api/leagues/{name}/clubs` - Clubs in league
- `GET /api/leagues/{name}/top-scorers` - League top scorers

### Competitions
- `GET /api/competitions/` - List all competitions
- `GET /api/competitions/{name}` - Competition details
- `GET /api/competitions/{name}/matches` - All matches
- `GET /api/competitions/{name}/participants` - Participating clubs

### Matches
- `GET /api/matches/recent` - Recent matches

### Analysis
- `GET /api/analysis/top-by-metric?metric=goals` - Top players by metric
- `GET /api/analysis/by-nationality?nation=ENG` - Stats by nationality
- `GET /api/analysis/by-position` - Stats by position
- `GET /api/analysis/by-age-group` - Stats by age group
- `POST /api/analysis/compare-players` - Detailed player comparison

## Project Structure

```
football-stats-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application and startup
│   ├── database.py             # Neo4j connection handler
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── players.py          # Player endpoints
│   │   ├── teams.py            # Team endpoints
│   │   ├── leagues.py          # League endpoints
│   │   ├── competitions.py     # Competition endpoints
│   │   ├── matches.py          # Match endpoints
│   │   └── analysis.py         # Analysis endpoints
│   └── services/
│       ├── __init__.py
│       └── neo4j_service.py    # Neo4j queries
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md
```

## Example Requests

### Get Home Page Data
```bash
curl http://localhost:8000/api/home
```

### Search Players
```bash
curl http://localhost:8000/api/players/search?q=Messi
```

### Get League Standings
```bash
curl http://localhost:8000/api/leagues/Premier%20League/standings
```

### Compare Players
```bash
curl -X POST http://localhost:8000/api/players/compare \
  -H "Content-Type: application/json" \
  -d '["Lionel Messi", "Cristiano Ronaldo"]'
```

## CORS Configuration

The API is configured to allow all origins by default for development. In production, update the CORS settings in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Health Check

```bash
curl http://localhost:8000/health
```

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

## Development

### Adding New Endpoints

1. Add the Cypher query in `app/services/neo4j_service.py`
2. Create or update the router in `app/routers/`
3. Add response models in `app/models/schemas.py` if needed

### Testing Queries

You can test Neo4j queries directly in the Neo4j Browser or using the Neo4j service methods.

## Notes

- All player statistics are from the 2022-23 season
- Some teams in matches may not exist as Club nodes (lower division teams)
- Competition matches include European competitions and FA Cup
- League matches are from the top 5 European leagues

## Troubleshooting

### Connection Issues
- Ensure Neo4j is running
- Check NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD in `.env`
- Verify Neo4j is accepting bolt connections

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Query Errors
- Check that your Neo4j database has the expected schema
- Verify node labels and relationship types match the documentation

## License

MIT License