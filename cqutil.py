"""

"""

SelfID = -1
EchoID = 0


def get_user_id(data: dict):
    return data["sender"]["user_id"]


def get_group_id(data: dict):
    return data.get("group_id", None)


def get_message_without_at_and_whitespace(data: dict):
    _message = data.get("message", "")
    _prefix = at_me()

    if _message.startswith(_prefix):
        _message = _message[len(_prefix):]
    return _message.strip()


def at(user_id):
    return f"[CQ:at,qq={user_id}]"


def at_me():
    return at(SelfID)


def is_at(data: dict):
    return data.get("message", "").startswith(at_me())


def is_private_message(data: dict):
    return data.get("message_type", None) == "private"


def is_group_message(data: dict):
    return data.get("message_type", None) == "group"


def is_normal_message(data: dict):
    return data.get("sub_type", None) == "normal"


def is_friend_message(data: dict):
    return data.get("sub_type", None) == "friend"


def to_response(message: str, user_id: int, group_id: int):
    global EchoID
    EchoID = EchoID % 1000000 + 1

    params = {
        "group_id": group_id,
        "message": f"{at(user_id)}{message}"
    } if group_id else {
        "user_id": user_id,
        "message": message
    }

    return {
        "action": "send_msg",
        "params": params,
        "echo": str(EchoID)
    }
