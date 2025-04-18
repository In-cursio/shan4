import logging
import logging.config
import sys
import os
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, REQ_CHANNEL1, REQ_CHANNEL2, LOG_CHANNEL, DATABASE_URI, DATABASE_NAME, OWNER_ID
from utils import temp, load_datas
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from aiohttp import web
from plugins.web_support import web_server
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

PORT = "8080" 
# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger('apscheduler').setLevel(logging.ERROR)

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=100,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self, **kwargs):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        me = await self.get_me()
        await load_datas(me.id)
        self.schedule = AsyncIOScheduler()
        self.schedule.start()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username     
        if temp.REQ_CHANNEL1:  
            try:
                _link = await self.create_chat_invite_link(chat_id=int(temp.REQ_CHANNEL1), creates_join_request=True)
                self.req_link1 = _link.invite_link
                print(f"Invite Link One set as {self.req_link1}")
            except Exception as e:
                logging.info(f"Make Sure REQ_CHANNEL 1 ID is correct or {e}")
        if temp.REQ_CHANNEL2:
            try:
                _link = await self.create_chat_invite_link(chat_id=int(temp.REQ_CHANNEL2), creates_join_request=True)
                self.req_link2 = _link.invite_link
                print(f"Invite Link Two set as {self.req_link2}")
            except Exception as e:
                logging.info(f"Make Sure REQ_CHANNEL 2 ID is correct or {e}")

        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()     
        
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        await self.send_message(chat_id=int(OWNER_ID), text="restarted ❤️‍🩹")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")
    
    async def iter_messages(self, chat_id: Union[int, str], limit: int, offset: int = 0,) -> Optional[AsyncGenerator["types.Message", None]]:                     
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1


app = Bot()
app.run()
