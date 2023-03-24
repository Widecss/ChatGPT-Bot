"""
Main
"""
import asyncio
import json

import api
import cqhttp
import cqutil


class Config(dict):
    def get_config(self, classify, attribute, default_value=None):
        return self.get(classify, {}).get(attribute, default_value)


def read_config():
    with open("./config.json", encoding="utf-8") as file:
        config: Config = json.load(file, object_pairs_hook=lambda mapping: Config(mapping))

    cqutil.SelfID = config.get_config("qq", "self_id")

    cqhttp.ServerURL = config.get_config("qq", "ws_server_url")

    api.Organization = config.get_config("chatgpt", "organization")
    api.ApiKey = config.get_config("chatgpt", "api_key")
    api.Proxy = config.get_config("chatgpt", "proxy") if config.get_config("chatgpt", "proxy").strip() else None
    api.ModelID = config.get_config("chatgpt", "model_id")
    api.MaxTokens = config.get_config("chatgpt", "max_tokens")
    api.Timeout = config.get_config("chatgpt", "session_timeout")
    api.UseRequests = config.get_config("chatgpt", "use_requests", False)


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
