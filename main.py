import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from loguru import logger
from core.agent import AnimeRecommenderAgent
from fastapi import FastAPI, Request, Depends
import uvicorn
from models.schema import UserAnimeList
from contextlib import asynccontextmanager


# --- 1. 将初始化逻辑直接放入 lifespan，并实现“快速失败” ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("--------------Anco Beta Test Starting--------------")

    # 加载环境变量
    load_dotenv()
    logger.add("app.log")

    # 检查关键配置，如果缺失则直接抛出异常，阻止应用启动
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    if not api_key or not base_url:
        error_msg = "API_KEY or BASE_URL not found in environment variables. Application cannot start."
        logger.critical(error_msg)
        raise ValueError(error_msg)  # <<< CHANGE: 抛出异常，启动失败

    # --- 2. 使用 app.state 存储共享的 agent 实例 ---
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    model = "openai/gpt-4.1-mini"
    # 将 agent 实例附加到 app.state
    app.state.agent = AnimeRecommenderAgent(client=client, model=model)
    logger.info("Agent initialized successfully.")

    yield

    logger.info("--------------Anco Beta Test Stopped--------------")


app = FastAPI(lifespan=lifespan)


# --- 3. (可选但推荐) 使用依赖注入获取 agent ---
# 这个依赖函数让路径操作的依赖关系更清晰
def get_agent(request: Request) -> AnimeRecommenderAgent:
    return request.app.state.agent


# --- 5. 将路径操作改为 async，并使用 Depends ---
@app.post("/recommend")
async def recommend(
    user_anime_list: UserAnimeList,
    agent: AnimeRecommenderAgent = Depends(get_agent),  # <<< CHANGE: 使用依赖注入
):
    recommendation = await agent.get_recommendation(user_anime_list.user_anime_list)
    if not recommendation:
        return {"detail": "An internal error occurred."}
    return recommendation


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
