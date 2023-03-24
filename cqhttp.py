"""

"""
import asyncio
import time
import traceback

from aiohttp import WSMessage, ClientSession

import cqutil
from api import ChatGPT, Session

ServerURL = ""


class Requester:
    def __init__(self):
        self.heartbeat_time = -1
        self.client = None

    async def check_heartbeat_loop(self):
        # 还没写完
        if time.time() - self.heartbeat_time > 300 and self.client is not None:
            await self.client.close()

    async def on_handle(self, data: dict, api: ChatGPT) -> dict or None:
        raise NotImplementedError

    async def send_message(self, message: str, user_id: int, group_id: int):
        if self.client is None:
            return
        data = cqutil.to_response(message, user_id, group_id)
        await self.client.send_json(data)

    async def loop_connect(self, api: ChatGPT, session: ClientSession):
        async with session.ws_connect(ServerURL) as client:
            self.client = client
            async for msg in client:
                msg: WSMessage
                data = msg.json()
                if data.get("meta_event_type", None) == "heartbeat":
                    self.heartbeat_time = data["time"]
                    continue

                await self.on_handle(data, api)
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


class Client(Requester):
    def __init__(self):
        super().__init__()
        self.chat_sessions = {}

    async def on_handle(self, data: dict, api: ChatGPT) -> dict or None:
        # 群聊不是普通发言不触发
        if cqutil.is_group_message(data):
            if not cqutil.is_normal_message(data):
                return
        # 私聊不是好友不触发
        elif cqutil.is_private_message(data):
            if not cqutil.is_friend_message(data):
                return
        # 其他类型不触发
        else:
            return

        # 群聊里没有 at 不触发
        if cqutil.is_group_message(data) and not cqutil.is_at(data):
            return

        message: str = cqutil.get_message_without_at_and_whitespace(data)
        user_id = cqutil.get_user_id(data)
        group_id = cqutil.get_group_id(data)

        if not message:
            return await self.send_message("【请发送一些文字】", user_id, group_id)

        # 重置指令
        if message == "重置":
            return await self.command_reset(group_id, user_id)

        # 修改指令
        if message == "修改":
            return await self.command_change(group_id, user_id)

        try:
            session = await self.get_session(group_id, user_id, api)
            response = await api.chat(session, message)
            await self.send_message(response, user_id, group_id)

            # 最大时清空
            if session.is_max_tokens():
                if user_id in self.chat_sessions.keys():
                    del self.chat_sessions[user_id]

                print("*已超过允许的最大对话内容，对话已重置: " + str(user_id))
                await self.send_message("【已超过允许的最大对话内容，本次对话已重置】", user_id, group_id)
            # 存储
            else:
                self.chat_sessions[user_id] = session
        except Exception as e:
            await self.send_message(f"【与服务器通信出现异常，请重试：{e}】", user_id, group_id)
            traceback.print_exc()

    async def get_session(self, group_id, user_id, api):
        # 如果不是第一次对话
        if user_id in self.chat_sessions.keys():
            session = self.chat_sessions[user_id]
        # 第一次对话
        else:
            session = api.create_session(user_id, group_id)

        session.user_id = user_id
        session.group_id = group_id
        return session

    async def command_reset(self, group_id, user_id):
        if user_id not in self.chat_sessions.keys():
            return await self.send_message("【你还没有开始对话呢...】", user_id, group_id)

        del self.chat_sessions[user_id]
        print("*对话已重置: " + str(user_id))
        return await self.send_message("【本次对话已重置】", user_id, group_id)

    async def command_change(self, group_id, user_id):
        if user_id not in self.chat_sessions.keys():
            return await self.send_message("【你还没有开始对话呢...】", user_id, group_id)

        if self.chat_sessions[user_id].rollback():
            print("*对话已返回至上一轮: " + str(user_id))
            return await self.send_message("【本次对话已返回至上一轮】", user_id, group_id)
        else:
            print("*仅允许返回一次: " + str(user_id))
            return await self.send_message("【本次对话已返回过， 仅允许返回一次】", user_id, group_id)

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
