import os
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger
from core.agent import AnimeRecommenderAgent


def main():
    # 1. 集中管理配置和初始化
    load_dotenv()
    logger.add("app.log")

    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    MODEL = "openai/gpt-5-mini"  # 或者从config文件读取

    if not API_KEY:
        logger.error("API_KEY not found in environment variables.")
        return

    # 2. 创建一次客户端实例
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # 3. 将依赖项注入到Agent中
    agent = AnimeRecommenderAgent(client=client, model=MODEL)

    print("你好！我是你的专属动漫推荐助手Anco。")
    # ...
    while True:
        user_input = input("请输入你喜欢的动漫列表（用英文逗号分隔）: ")
        if user_input.lower() in ["退出", "exit", "quit"]:
            break

        anime_list = [anime.strip() for anime in user_input.split(",")]
        recommendations = agent.get_recommendation(anime_list)

        if recommendations:
            print("\n--- Anco的推荐 ---")
            for rec in recommendations.rec_list:
                print(f"动漫名称: {rec.anime_name}")
                print(f"推荐得分: {rec.score}")
                print("-" * 10)
        else:
            print("抱歉，暂时无法获取推荐。")


if __name__ == "__main__":
    main()