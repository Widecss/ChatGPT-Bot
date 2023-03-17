# ChatGPT Bot
一个基于 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 的 Websocket 协议与 [OpenAI API](https://platform.openai.com/) 的 QQ Bot

搜了一圈都是 mirai，没找到使用 go-cqhttp 的，就自己写了个，满足基本功能

## 运行
- 启动 go-cqhttp，并配置好正向 Websocket 服务
- 安装 **requirements.txt** 依赖
- 修改配置文件 **config.json** 中的 [机构 ID](https://platform.openai.com/account/org-settings)，[Api Key](https://platform.openai.com/account/api-keys)，[模型 ID](https://platform.openai.com/docs/models/overview)
```
{
    "qq": {
        # bot 的 QQ 帐号
        "self_id": -1,

        # go-cqhttp 端开启的链接
        "ws_server_url": "ws://ip:port"
    },
    "chatgpt": {
        # openai 帐号设置里的机构号
        "organization": "",

        # openai 帐号设置里生成的 api key
        "api_key": "",

        # http 协议的 aiohttp 库代理，可留空
        "proxy": "",

        # 模型 ID，后面可以切换成 GPT-4
        "model_id": "gpt-3.5-turbo",

        # 该模型最大支持多少 token，GPT-3.5 是 4096
        "max_tokens": 4096,

        # 当用户多久不使用自动清空重置会话，单位秒，负数时关闭此功能
        "session_timeout": 300
    }
}
```
- 启动 **main.py**

## 使用
- 直接 **@Bot 后面接消息** 即可开启对话，按每一个 QQ 帐号独立对话
- 使用 **@Bot 重置** 手动重置自己的对话
- TODO

## 其他
如果有问题可以在 issue 中提出。