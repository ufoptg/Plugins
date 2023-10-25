from pyrogram import Client
from pyrogram.types import Message

from .config import Config, Symbols
from .database import db
from .logger import LOGS


class HellClient(Client):
    def __init__(self) -> None:
        self.users: list[Client] = []
        self.bot: Client = Client(
            name="HellBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="Hellbot.plugins.bot"),
        )

    async def start_user(self) -> None:
        sessions = await db.get_all_sessions()
        for i, session in enumerate(sessions):
            try:
                client = Client(
                    name=f"HellUser#{i + 1}",
                    api_id=Config.API_ID,
                    api_hash=Config.API_HASH,
                    session_name=session["user_id"],
                    plugins=dict(root="Hellbot.plugins.user"),
                )
                await client.start()
                me = await client.get_me()
                self.users.append(client)
                LOGS.info(
                    f"{Symbols.arrow_right * 2} Started User {i + 1}: '{me.first_name}' {Symbols.arrow_left * 2}"
                )
            except Exception as e:
                LOGS.error(f"{Symbols.cross_mark} {i + 1}: {e}")
                continue

    async def start_bot(self) -> None:
        await self.bot.start()
        me = await self.bot.get_me()
        LOGS.info(
            f"{Symbols.arrow_right * 2} Started HellBot Client: '{me.username}' {Symbols.arrow_left * 2}"
        )

    async def startup(self) -> None:
        LOGS.info(
            f"{Symbols.bullet * 3} Starting HellBot Client & User {Symbols.bullet * 3}"
        )
        await self.start_bot()
        await self.start_user()

    async def edit_or_reply(self, message: Message, text: str) -> Message:
        if message.from_user and message.from_user.id in Config.SUDO_USERS:
            if message.reply_to_message:
                return await message.reply_to_message.reply_text(text)
            return await message.reply_text(text)
        return await message.edit_text(text)

    async def log(self, tag: str, text: str, file: str = None) -> None:
        msg = f"**#{tag.upper()}**\n\n{text}"
        try:
            if file:
                await self.bot.send_document(Config.LOGGER_ID, file, caption=msg)
            else:
                await self.bot.send_message(
                    Config.LOGGER_ID, msg, disable_web_page_preview=True
                )
        except Exception as e:
            raise Exception(f"{Symbols.cross_mark} LogErr: {e}")


hellbot = HellClient()
