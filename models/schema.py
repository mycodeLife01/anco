from pydantic import BaseModel, Field

class UserAnimeList(BaseModel):
    user_anime_list: list[str] = Field(description="用户喜欢的动漫列表")