from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pokeapi_base_url: str
