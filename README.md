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

## How to Run

Instructions for running the application will be provided after implementation.