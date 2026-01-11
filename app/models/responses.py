from typing import List, Union
from pydantic import BaseModel


class CoverImageModel(BaseModel):
    cover_image_color: str
    cover_image: str
    banner_image: str


class AnimeItem(BaseModel):
    id: int
    title: str
    episodes: int
    status: str
    coverImage: CoverImageModel
    format: str
    popularity: int
    averageScore: int
    trending: int
    releaseDate: Union[int, str]


class PageInfo(BaseModel):
    lastPage: int
    currentPage: int


class PagedResponse(BaseModel):
    pageInfo: PageInfo
    data: List[AnimeItem]