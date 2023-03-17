"""

"""
import asyncio
import random
import time
import traceback

from aiohttp import WSMessage, ClientSession

from api import ChatGPT, Session

ServerURL = ""

SelfID = -1


class Client:
    def __init__(self):
        self.heartbeat_time = -1
        self.client = None
        self.chat_sessions = {}

    def to_response(self, message: str, user_id: int, group_id: int):
        params = {
            "group_id": group_id,
            "message": f"{self.at(user_id)} {message}"
        } if group_id else {
            "user_id": user_id,
            "message": message
        }
        return {
            "action": "send_msg",
            "params": params,
            "echo": str(random.randint(0, 100000))
        }

    async def send_message(self, message: str, user_id: int, group_id: int):
        if self.client is None:
            return
        data = self.to_response(message, user_id, group_id)
        await self.client.send_json(data)

    @staticmethod
    def at(user_id):
        return f"[CQ:at,qq={user_id}]"

    def at_me(self):
        return self.at(SelfID)

    def is_at(self, message: str):
        return message.startswith(self.at_me())

    async def handle(self, data: dict, api: ChatGPT) -> dict or None:
        # 群聊不是普通发言不触发
        if data.get("message_type", None) == "group":
            if data.get("sub_type", None) != "normal":
                return
        # 私聊不是好友不触发
        elif data.get("message_type", None) == "private":
            if data.get("sub_type", None) != "friend":
                return
        # 其他类型不触发
        else:
            return

        message: str = data["message"]
        # 群聊里没有 at 不触发
        if data.get("message_type", None) == "group" and not self.is_at(message):
            return

        message = message.removeprefix(self.at_me()).strip()

        user_id = data["sender"]["user_id"]
        group_id = data.get("group_id", None)

        # 重置指令
        if message == "重置":
            del self.chat_sessions[user_id]
            print("*对话已重置: " + str(user_id))
            return await self.send_message("【本次对话已重置】", user_id, group_id)

        # 如果不是第一次对话
        if user_id in self.chat_sessions.keys():
            session = self.chat_sessions[user_id]
            session.user_id = user_id
            session.group_id = group_id

            # 如果对话已经超出了限制
            if session.is_max_tokens():
                del self.chat_sessions[user_id]
                print("*已超过允许的最大对话内容，对话已重置: " + str(user_id))
                return await self.send_message("【已超过允许的最大对话内容，本次对话已重置】", user_id, group_id)
        # 第一次对话
        else:
            session = api.create_session(user_id, group_id)
            self.chat_sessions[user_id] = session

        try:
            response = await api.chat(session, message)
            await self.send_message(response, user_id, group_id)
        except Exception as e:
            await self.send_message(f"【与服务器通信出现异常，请重试：{e}】", user_id, group_id)

    async def check_heartbeat_loop(self):
        # 还没写完
        if time.time() - self.heartbeat_time > 300 and self.client is not None:
            await self.client.close()

    async def check_session_loop(self):
        while True:
            for key, value in list(self.chat_sessions.items()):
                value: Session
                if value.is_out_date():
                    del self.chat_sessions[key]
                    print("*太久没回复，已关闭对话: " + str(value.user_id))
                    await self.session_out_date(value)
            await asyncio.sleep(10)

    async def session_out_date(self, session: Session):
        if self.client is None:
            return

        await self.send_message("【太久没回复，已关闭本次对话】", session.user_id, session.group_id)

    async def loop_connect(self, api: ChatGPT, session: ClientSession):
        async with session.ws_connect(ServerURL) as client:
            self.client = client
            async for msg in client:
                msg: WSMessage
                data = msg.json()
                if data.get("meta_event_type", None) == "heartbeat":
                    self.heartbeat_time = data["time"]
                    continue

                await self.handle(data, api)
            self.client = None

    async def loop(self, api: ChatGPT):
        while True:
            try:
                async with ClientSession() as session:
                    await self.loop_connect(api, session)
            except Exception as e:
                traceback.print_exc()
                print(e)
                self.client = None
