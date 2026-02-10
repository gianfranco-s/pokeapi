from pydantic import BaseModel, ConfigDict


class Berry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    growth_time: int


class BerryListItem(BaseModel):
    name: str
    url: str


class BerryListResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[BerryListItem]


class AllBerryStatsResponse(BaseModel):
    berries_names: list[str]
    min_growth_time: int
    median_growth_time: float
    max_growth_time: int
    variance_growth_time: float
    mean_growth_time: float
    frequency_growth_time: dict[int, int]
