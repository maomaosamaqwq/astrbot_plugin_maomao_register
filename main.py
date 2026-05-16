"""
猫猫AI网站注册插件 - AstrBot Plugin
为AstrBot的LLM提供注册猫猫AI网站账号的工具。
用户只需对bot说"我要注册"或者类似的话，LLM会自动调用注册工具。
"""

import re
import httpx
from astrbot.api.star import Context, Star, register
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger

# 后端API地址（网站后端的Cloudflare Worker）
API_BASE_URL = "https://api.仙狐大人.我爱你"


@register(
    name="maomao_register",
    desc="猫猫AI网站账号注册工具 - 用户对bot说注册，LLM会自动调用此工具",
    version="1.0.0",
    author="maomaosamaqwq"
)
class MaomaoRegisterPlugin(Star):
    """猫猫AI网站注册插件 - 提供LLM tool"""

    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}

    @filter.llm_tool(name="register_website_account",
                     description="注册猫猫AI网站账号。用户需要提供密码，用户名会自动使用用户的QQ邮箱。"
                                 "注册成功后返回用户名和Token。")
    async def register_website_account(self, event: AstrMessageEvent, password: str) -> str:
        """
        注册猫猫AI网站账号。

        Args:
            password(string): 用户设置的密码
        Returns:
            注册结果信息
        """
        if not password or len(password.strip()) < 1:
            return "密码不能为空，请让用户重新提供密码。"

        pwd = password.strip()
        sender_id = event.get_sender_id()
        if not sender_id:
            return "无法获取你的QQ号，可能是系统错误，请稍后再试。"

        username = f"{sender_id}@qq.com"

        # 校验邮箱格式
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', username):
            return f"生成的用户名格式异常：{username}，请联系管理员。"

        logger.info(f"正在注册账号: {username}")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{API_BASE_URL}/register",
                    json={
                        "username": username,
                        "password": pwd
                    }
                )
                result = resp.json()

                if result.get("success"):
                    token = result.get("token", "")
                    return (
                        f"🎉 注册成功！\n"
                        f"用户名：{username}\n"
                        f"Token：{token}\n\n"
                        f"现在可以用这个账号登录网站 🥜.🐱 开始聊天啦~"
                    )
                else:
                    error_msg = result.get("error", "未知错误")
                    return f"注册失败：{error_msg}"
        except httpx.TimeoutException:
            return "注册超时，服务器暂时不可用。请让用户稍后再试。"
        except Exception as e:
            logger.error(f"注册请求异常: {e}")
            return f"注册失败，请稍后重试。（{str(e)[:80]}）"
