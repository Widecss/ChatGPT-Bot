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
        self.locking = False

        self.user_id = user_id
        self.group_id = group_id

        self.current_user_message = None
        self.current_assistant_message = None

    def set_user_message(self, message) -> "Session":
        self.current_user_message = self.to_message(Role.USER, message)
        return self

    def set_assistant_message(self, message) -> "Session":
        self.current_assistant_message = self.to_message(Role.ASSISTANT, message)
        return self

    def start(self) -> "Session":
        self.locking = True
        return self

    def done(self) -> "Session":
        self.prompt.append(self.current_user_message)
        self.prompt.append(self.current_assistant_message)

        self.locking = False
        self.last_chat_time = time.time()
        return self

    def rollback(self):
        self.current_user_message = None
        self.current_assistant_message = None

    def get_messages(self):
        return self.prompt + [self.current_user_message]

    def is_out_date(self):
        if Timeout < 0:
            return False
        if self.locking:
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
        print("--[User]: " + message)

        session.start()
        session.set_user_message(message)

        try:
            response = await openai.ChatCompletion.acreate(
                model=ModelID,
                messages=session.get_messages()
            )
        except Exception:
            session.rollback()
            raise

        session.total_tokens = response["usage"]["total_tokens"]
        choices: list = response["choices"]
        sorted(choices, key=lambda k: k["index"])

        result = []
        for obj in response["choices"]:
            result.append(obj["message"]["content"])

        ans = "\n".join(result).strip()
        print("[AI]:" + ans)
        print("[Tokens]:" + str(session.total_tokens))

        session.set_assistant_message(ans)
        session.done()
        return ans
