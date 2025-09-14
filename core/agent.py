from openai import AsyncOpenAI
from loguru import logger
from core.config_loader import config
from models.anime import AnimeRecList


class AnimeRecommenderAgent:
    # 接收llm客户端和model名称作为参数
    def __init__(self, client: AsyncOpenAI, model: str):
        self.llm = client
        self.model = model

        # 将Prompt模板的加载也放在初始化中，避免重复获取
        self.system_prompt = (
            config.prompts.anime_recommender.message.SystemMessage.content
        )
        self.user_prompt_template = (
            config.prompts.anime_recommender.message.UserMessage.content
        )

    async def get_recommendation(self, user_anime_list: list[str]) -> AnimeRecList | None:
        try:
            # 使用self.user_prompt_template
            user_prompt = self.user_prompt_template.format(
                user_anime_list=user_anime_list
            )

            completion = await self.llm.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=AnimeRecList,
            )
            return completion.choices[0].message.parsed

        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")
            return None
