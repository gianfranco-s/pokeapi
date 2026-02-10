# PokeAPI Berries Statistics

## Project Description

This project implements a Poke-berries statistics API that provides statistical information about berries from the PokeAPI.

## Endpoints

### GET /allBerryStats

Returns comprehensive statistics about all berries, including their names and various growth time metrics.

**Response Format:**

```json
{
    "berries_names": [...],
    "min_growth_time": 0, // integer
    "median_growth_time": 0.0, // float
    "max_growth_time": 0, // integer
    "variance_growth_time": 0.0, // float
    "mean_growth_time": 0.0, // float
    "frequency_growth_time": { // object mapping growth_time to frequency
        "growth_time": frequency,
        ...
    }
}
```

This endpoint fetches data from the external PokeAPI berries endpoint: https://pokeapi.co/docs/v2#berries

## Architecture Decisions

The directory structure is intentionally kept flat (`src/` with no nested packages). The project requirements are well-scoped and unlikely to change. The upstream PokeAPI documentation explicitly states the data is static and the API won't change in the near future. A flat layout avoids premature abstraction and keeps navigation straightforward for a project of this size.

## How to Run

Intended usage is docker-based.

```bash
docker compose -f docker/docker-compose.yml up --build
```

The API will be available at `http://localhost:8000`.

- `http://localhost:8000/allBerryStats` — berry growth time statistics (JSON)
- `http://localhost:8000/histogram` — growth time frequency chart (PNG)
- `http://localhost:8000/docs` — interactive API documentation (Swagger UI)


## Tests

```bash
docker buildx build -f docker/Dockerfile.tests -t pokeapi-tests .
docker run --rm pokeapi-tests
```
