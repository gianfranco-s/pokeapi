from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pokeapi_base_url: str
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    redis_url: str = "redis://redis:6379/0"
