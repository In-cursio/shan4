import subprocess
import json

from pyrogram import Client, filters, enums
import sys, os 
from info import ADMINS
from pyrogram.errors import ChatAdminRequired, FloodWait 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest, Message
from pyrogram.types import ChatJoinRequest
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from database.users_chats_db import db
from utils import temp
    
@Client.on_chat_join_request()
async def join_reqs(_, join_req: ChatJoinRequest):
    user_id = join_req.from_user.id
    try:
        if join_req.chat.id == temp.REQ_CHANNEL1:
            await db.add_req_one(user_id)
        if join_req.chat.id == temp.REQ_CHANNEL2:
            await db.add_req_two(user_id)
    except Exception as e:
        print(f"Error adding join request: {e}")

@Client.on_message(filters.command("set_sub1") & filters.user(ADMINS))
async def add_fsub_chatt1(bot, m):
    if len(m.command) == 1:
        return await m.reply("Send Command With Force Sub Channel Id Like /set_sub -100123456789")
    raw_id = m.text.split(" ", 1)[1]
    if temp.REQ_CHANNEL1:
        old_channel_id = temp.REQ_CHANNEL1
        temp.REQ_CHANNEL1 = None
        bot.req_link1 = None
        await db.update_loadout('channel1', None, bot.me.id)
        await db.delete_all_one()
    try:
        chat = await bot.get_chat(int(raw_id))
    except ChatAdminRequired:
        return await m.reply("Channel Parameter Invalid. Iam Not Having Full Admin Rights In Your Channel. Please Add Admin With Full Admin Permeation")
    except PeerIdInvalid:
        return await m.reply("Bot Is Not Added In This Channel. Please Add With Full Admin Permeation")
    except Exception as e:
        return await m.reply(f'Error {e}')
    try:
        link = (await bot.create_chat_invite_link(chat_id=int(chat.id), creates_join_request=True)).invite_link
    except Exception as e:
        print(e)
        link = "None"
    await db.update_loadout('channel1', chat.id, bot.me.id)
    await db.delete_all_one()
    temp.REQ_CHANNEL1 = chat.id
    bot.req_link1 = link
    text = f"Success Fully Added:\n\nchat id: {chat.id}\nchat name: {chat.title}\nchat link: {link}"
    return await m.reply(text=text, disable_web_page_preview=True)

@Client.on_message(filters.command("set_sub2") & filters.user(ADMINS))
async def add_fsub_chatt2(bot, m):
    if len(m.command) == 1:
        return await m.reply("Send Command With Force Sub Channel Id Like /set_sub -100123456789")
    raw_id = m.text.split(" ", 1)[1]
    if temp.REQ_CHANNEL2:
        old_channel_id = temp.REQ_CHANNEL2
        temp.REQ_CHANNEL2 = None
        bot.req_link2 = None
        await db.update_loadout('channel2', None, bot.me.id)
        await db.delete_all_two()
    try:
        chat = await bot.get_chat(int(raw_id))
    except ChatAdminRequired:
        return await m.reply("Channel Parameter Invalid. Iam Not Having Full Admin Rights In Your Channel. Please Add Admin With Full Admin Permeation")
    except PeerIdInvalid:
        return await m.reply("Bot Is Not Added In This Channel. Please Add With Full Admin Permeation")
    except Exception as e:
        return await m.reply(f'Error {e}')
    try:
        link = (await bot.create_chat_invite_link(chat_id=int(chat.id), creates_join_request=True)).invite_link
    except Exception as e:
        print(e)
        link = "None"
    await db.update_loadout('channel2', chat.id, bot.me.id)
    await db.delete_all_two()
    temp.REQ_CHANNEL2 = chat.id
    bot.req_link2 = link
    text = f"Success Fully Added:\n\nchat id: {chat.id}\nchat name: {chat.title}\nchat link: {link}"
    return await m.reply(text=text, disable_web_page_preview=True)

@Client.on_message(filters.command("view_sub") & filters.user(ADMINS))
async def get_fsub_chats(bot, m):
    try:
        text = ""
        if temp.REQ_CHANNEL1:
            try:
                chat1 = await bot.get_chat(int(temp.REQ_CHANNEL1))
                title = chat1.title
            except Exception as e:
                title = "None"
            link1 = bot.req_link1 if hasattr(bot, 'req_link1') else "No invite link available"
            count1 = await db.get_all_one_count()
            
            text += (
                f"REQ CHANNEL 1:\n\n"
                f"Chat ID: {temp.REQ_CHANNEL1}\n"
                f"Chat Name: {title}\n"
                f"Chat Link: {link1}\n"
                f"Total Requests: {count1}\n\n"
            )
        else:
            text += "No channel found for REQ CHANNEL 1.\n\n"
        if temp.REQ_CHANNEL2:
            try:
                chat2 = await bot.get_chat(int(temp.REQ_CHANNEL2))
                title = chat2.title
            except Exception as e:
                title = "None"
            link2 = bot.req_link2 if hasattr(bot, 'req_link2') else "No invite link available"
            count2 = await db.get_all_two_count()     
            text += (
                f"REQ CHANNEL 2:\n\n"
                f"Chat ID: {temp.REQ_CHANNEL2}\n"
                f"Chat Name: {title}\n"
                f"Chat Link: {link2}\n"
                f"Total Requests: {count2}"
            )
        else:
            text += "No channel found for REQ CHANNEL 2."
        await m.reply_text(text, disable_web_page_preview=True, quote=True)
    
    except Exception as e:
        await m.reply_text(f"An error occurred: {str(e)}", quote=True)

@Client.on_message(filters.command("del_sub1") & filters.user(ADMINS))
async def del_fsub_chats1(bot, m):
    if not temp.REQ_CHANNEL1:
        return await m.reply("No channel is currently set.")
    old_channel_id = temp.REQ_CHANNEL1
    temp.REQ_CHANNEL1 = None
    bot.req_link1 = None
    await db.update_loadout('channel1', None, bot.me.id)
    await db.delete_all_one()
    text = f"Successfully removed the fsub channel:\n\nChat ID: {old_channel_id}"
    return await m.reply(text=text, disable_web_page_preview=True)
    
@Client.on_message(filters.command("del_sub2") & filters.user(ADMINS))
async def del_fsub_chats2(bot, m):
    if not temp.REQ_CHANNEL2:
        return await m.reply("No channel is currently set.")
    old_channel_id = temp.REQ_CHANNEL2
    temp.REQ_CHANNEL2 = None
    bot.req_link2 = None
    await db.update_loadout('channel2', None, bot.me.id)
    await db.delete_all_two()
    text = f"Successfully removed the fsub channel:\n\nChat ID: {old_channel_id}"
    return await m.reply(text=text, disable_web_page_preview=True)
    
