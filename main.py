"""
猫猫AI网站注册插件 - AstrBot Plugin
通过AstrBot注册猫猫AI网站(🥜.🐱)的账号。
用户对bot说"注册"并提供密码，插件会调用网站后端的注册API完成注册。
注册的用户名为用户的QQ邮箱。
"""

import re
import hashlib
import httpx
from astrbot.api.star import Context, Star, register
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger

# 后端API地址（网站后端的Cloudflare Worker）
API_BASE_URL = "https://maomao-api.b35a90441d9dea81207b863b34b6516a.workers.dev"


@register(
    name="maomao_register",
    desc="通过AstrBot注册猫猫AI网站账号",
    version="1.0.0",
    author="maomaosamaqwq"
)
class MaomaoRegisterPlugin(Star):
    """猫猫AI网站注册插件"""

    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}

    @filter.command("注册")
    async def register(self, event: AstrMessageEvent):
        """注册猫猫AI网站账号。用法：注册 <密码>"""
        message_str = event.message_str.strip()

        # 解析参数
        parts = message_str.split(maxsplit=1)
        if len(parts) < 2:
            yield event.plain_result("用法：注册 <密码>\n示例：注册 123456")
            return

        password = parts[1].strip()
        if len(password) < 1:
            yield event.plain_result("密码不能为空喵~")
            return

        # 获取发送者的QQ号作为用户名
        sender_id = event.get_sender_id()
        if not sender_id:
            yield event.plain_result("无法获取你的QQ号，请稍后再试~")
            return

        # 用QQ号构造邮箱格式的用户名
        username = f"{sender_id}@qq.com"

        # 检查用户名是否合法（符合邮箱格式）
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', username):
            yield event.plain_result(f"生成的用户名格式异常：{username}")
            return

        yield event.plain_result("正在注册，请稍候~（>ω<）")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{API_BASE_URL}/register",
                    json={
                        "username": username,
                        "password": password
                    }
                )
                result = resp.json()

                if result.get("success"):
                    token = result.get("token", "")
                    yield event.plain_result(
                        f"🎉 注册成功！\n"
                        f"用户名：{username}\n"
                        f"Token：{token}\n\n"
                        f"你可以用这个账号登录网站啦~ 🐱"
                    )
                else:
                    error_msg = result.get("error", "未知错误")
                    yield event.plain_result(f"注册失败：{error_msg}")
        except httpx.TimeoutException:
            yield event.plain_result("注册超时，服务器暂时不可用。请稍后再试~")
        except Exception as e:
            logger.error(f"注册请求异常: {e}")
            yield event.plain_result(f"注册失败，请稍后重试。（{str(e)[:50]}）")

    @filter.command("重置密码")
    async def reset_password(self, event: AstrMessageEvent):
        """重置猫猫AI网站账号密码（目前需要联系管理员手动处理）"""
        yield event.plain_result(
            "重置密码功能暂未开放，请联系管理员处理喵~"
        )

    @filter.command("帮助")
    async def help_cmd(self, event: AstrMessageEvent):
        """显示插件帮助信息"""
        yield event.plain_result(
            "🐱 猫猫AI网站注册插件\n"
            "━━━━━━━━━━━━━━━━\n"
            "注册 <密码> - 注册网站账号（用户名为你的QQ邮箱）\n"
            "重置密码 - 重置密码（暂未开放）\n"
            "━━━━━━━━━━━━━━━━\n"
            "网站地址：🥜.🐱\n"
            "注册后即可在网站登录使用~"
        )
