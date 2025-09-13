from pydantic import BaseModel, Field
from core.config_loader import get_desc


class AnimeRec(BaseModel):
    anime_name: str = Field(description=get_desc("anime_model.AnimeRec.anime_name"))
    score: int = Field(description=get_desc("anime_model.AnimeRec.score"))


class AnimeRecList(BaseModel):
    rec_list: list[AnimeRec] = Field(
        description=get_desc("anime_model.AnimeRecList.rec_list")
    )
    alternatives: list[AnimeRec] = Field(
        description=get_desc("anime_model.AnimeRecList.alternatives")
    )
