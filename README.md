# PokeAPI Berries Statistics

## Project Description

This project implements a Poke-berries statistics API that provides statistical information about berries from the PokeAPI.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/allBerryStats` | Returns comprehensive statistics about all berries from PokeAPI, including names and growth time metrics (min, max, mean, median, variance, frequency distribution) |
| GET    | `/histogram`     | Returns a server-side rendered PNG chart showing the frequency distribution of berry growth times |
| GET    | `/docs`          | Interactive API documentation (Swagger UI) with endpoint testing capabilities |

## Architecture Decisions

**Flat Directory Structure**: The `src/` directory uses a flat layout with no nested packages. This approach suits the well-scoped requirements and avoids premature abstraction for a project of this size.

**Docker-First Development**: The application runs entirely in containers for consistency across development and deployment environments.

**Redis Caching**: Implements Redis caching to reduce PokeAPI calls and improve response times. The cache stores complete berry datasets with configurable TTL.

**No Authentication**: This is a development/demonstration project with no authentication layer implemented. Not suitable for production use without security enhancements.

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

## Verify cache is working
```bash
# First request (cache miss) - should be slow
curl -v -w "\nTotal response time: %{time_total}s\n" http://localhost:8000/allBerryStats

# Second request (cache hit) - should be fast
curl -v -w "\nTotal response time: %{time_total}s\n" http://localhost:8000/allBerryStats
```

```bash
docker exec -it pokeapi-redis redis-cli
```

```redis
> KEYS *
> TTL berries:all
```
