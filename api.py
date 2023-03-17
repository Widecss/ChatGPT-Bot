"""

"""
import time

import openai

Organization = ""
ApiKey = ""
Proxy = ""

ModelID = ""

Timeout = 60 * 5
MaxTokens = -1


class Role:
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"


class Session:
    def __init__(self, user_id=None, group_id=None):
        self.prompt = [
            # self.to_message(Role.SYSTEM, SystemMessage),
            # self.to_message(Role.ASSISTANT, InitialMessage),
        ]
        self.last_chat_time = time.time()
        self.total_tokens = 0
        self.user_id = user_id
        self.group_id = group_id

    def add_user_message(self, message):
        self.prompt.append(self.to_message(Role.USER, message))

    def add_assistant_message(self, message):
        self.prompt.append(self.to_message(Role.ASSISTANT, message))
        self.last_chat_time = time.time()

    def is_out_date(self):
        if Timeout < 0:
            return False
        return time.time() - self.last_chat_time > Timeout

    def is_max_tokens(self):
        return time.time() - self.last_chat_time > Timeout

    @staticmethod
    def to_message(role, content):
        return {"role": role, "content": content}


class ChatGPT:

    def __init__(self):
        openai.organization = Organization
        openai.api_key = ApiKey
        openai.proxy = Proxy

    @staticmethod
    def create_session(user_id, group_id) -> Session:
        return Session(user_id, group_id)

    @staticmethod
    async def chat(session: Session, message: str) -> str:
        print("User: " + message)
        session.add_user_message(message)

        response = await openai.ChatCompletion.acreate(
            model=ModelID,
            messages=session.prompt
        )

        session.total_tokens = response["usage"]["total_tokens"]
        choices: list = response["choices"]
        sorted(choices, key=lambda k: k["index"])

        result = []
        for obj in response["choices"]:
            result.append(obj["message"]["content"])

        ans = "\n".join(result).strip()
        print("AI:" + ans)
        print("Tokens:" + str(session.total_tokens))
        session.add_assistant_message(ans)
        return ans
