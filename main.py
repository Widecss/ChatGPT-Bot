"""
Main
"""
import asyncio
import json

import cqhttp
import api
import cqutil


def read_config():
    with open("./config.json", encoding="utf-8") as file:
        config = json.load(file)

    cqutil.SelfID = config["qq"]["self_id"]

    cqhttp.ServerURL = config["qq"]["ws_server_url"]

    api.Organization = config["chatgpt"]["organization"]
    api.ApiKey = config["chatgpt"]["api_key"]
    api.Proxy = config["chatgpt"]["proxy"] if config["chatgpt"]["proxy"].strip() else None
    api.ModelID = config["chatgpt"]["model_id"]
    api.MaxTokens = config["chatgpt"]["max_tokens"]
    api.Timeout = config["chatgpt"]["session_timeout"]


async def main():
    read_config()

    chat = api.ChatGPT()
    qq = cqhttp.Client()

    loop = asyncio.get_running_loop()
    loop.create_task(qq.loop(chat))
    loop.create_task(qq.check_session_loop())

    print("启动完毕~")

    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Ctrl + C")
