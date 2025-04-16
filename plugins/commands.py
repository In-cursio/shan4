import os
import sys
import logging
import random
import asyncio
from .pm_filter import auto_filter
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from database.ia_filterdb import Media2, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, REQ_CHANNEL1, REQ_CHANNEL2, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, PM_DEL, PICS
from utils import get_size, is_subscribed, is_requested_one, is_requested_two, temp, check_loop_sub, check_loop_sub1, check_loop_sub2
import re
import json
import base64
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta

should_run_check_loop_sub = False
should_run_check_loop_sub1 = False
BATCH_FILES = {}

DELETE_TXT = """𝗪𝗮𝗿𝗻𝗶𝗻𝗴 ⚠️

𝖥𝗂𝗅𝖾𝗌 𝖲𝖾𝗇𝖽 𝖶𝗂𝗅𝗅 𝖡𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝖿𝗍𝖾𝗋 5 𝖬𝗂𝗇𝗎𝗍𝖾𝗌 𝖳𝗈 𝖠𝗏𝗈𝗂𝖽 𝖢𝗈𝗉𝗒𝗋𝗂𝗀𝗁𝗍. 𝖲𝗈 𝖲𝖺𝗏𝖾 𝖳𝗁𝖾 𝖥𝗂𝗅𝖾 𝖳𝗈 𝖲𝖺𝗏𝖾𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌."""

async def delete_messages(client, messages):
    for msg in messages:
        try:
            await msg.delete()
            print(f"Deleted message with ID: {msg.message_id}")
        except Exception as e:
            print(f"Failed to delete message with ID: {msg.message_id}. Error: {e}")


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('🤖 Updates', url='https://t.me/CT_Arena')
            ],
            [
                InlineKeyboardButton('ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help"),
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘs ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('🔍 Sᴇᴀʀᴄʜ Fɪʟᴇ 🔍 ', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🪄 Oᴡɴᴇʀ 🪄', url='https://t.me/Sathan_Of_Telegram')
            ],[
            InlineKeyboardButton('⚠️ Group 1 ⚠️', url='https://t.me/Cinemathattakam_Group'),
            InlineKeyboardButton('✨ Group 2 ✨', url='https://t.me/Cinemathattakam_Group1')
            ],[
            InlineKeyboardButton('🥇 Mᴀɪɴ Cʜᴀɴɴᴇʟ 🥇', url='https://t.me/CT_Arena')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if message.command[1].startswith('getfile'): #@stellar_labs
        data = message.command[1].split("-", 1)
        file_name = data[1].replace('-', ' ')
        message.text = file_name
        await auto_filter(client, message)
        return
    try:
        should_run_check_loop_sub = False
        should_run_check_loop_sub1 = False
        if temp.REQ_CHANNEL1 and not await is_requested_one(client, message):
            btn = [[
                InlineKeyboardButton(
                    "🪄 Jᴏɪɴ Cʜᴀɴɴᴇʟ 1 🪄", url=client.req_link1)
            ]]
            should_run_check_loop_sub1 = True
            try:
                if temp.REQ_CHANNEL2 and not await is_requested_two(client, message):
                    btn.append(
                          [
                        InlineKeyboardButton(
                            "🪅 Jᴏɪɴ Cʜᴀɴɴᴇʟ 2 🪅", url=client.req_link2)
                          ]
                    )
                    should_run_check_loop_sub = True
            except Exception as e:
                print(e)
            if message.command[1] != "subscribe":
                try:
                    kk, file_id = message.command[1].split("_", 1)
                    pre = 'checksubp' if kk == 'filep' else 'checksub' 
                    btn.append([InlineKeyboardButton("〄 Tʀʏ Aɢᴀɪɴ 〄", callback_data=f"{pre}#{file_id}")])
                except (IndexError, ValueError):
                    btn.append([InlineKeyboardButton("〄 Tʀʏ Aɢᴀɪɴ 〄", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
            sh = await client.send_message(
                chat_id=message.from_user.id,
                text='⭕️𝗣𝗹𝗲𝗮𝘀𝗲 𝗥𝗲𝗮𝗱 𝗧𝗵𝗲 𝗚𝗶𝘃𝗲𝗻 𝗜𝗻𝘀𝘁𝗿𝘂𝗰𝘁𝗶𝗼𝗻𝘀⭕️\n\n🔰 𝙄𝙣𝙤𝙧𝙙𝙚𝙧 𝙏𝙤 𝙂𝙚𝙩 𝙏𝙝𝙚 𝙍𝙚𝙤̨𝙪𝙚𝙨𝙩𝙚𝙙 𝙈𝙤𝙫𝙞𝙚 𝙁𝙞𝙡𝙚 \n𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝙏𝙤 𝙅𝙤𝙞𝙣 𝙏𝙝𝙚 𝙁𝙤𝙡𝙡𝙤𝙬𝙞𝙣𝙜 𝘾𝙝𝙖𝙣𝙣𝙚𝙡𝙨 \n𝘽𝙮 𝘾𝙡𝙞𝙘𝙠𝙞𝙣𝙜 𝙏𝙝𝙚 𝘽𝙪𝙩𝙩𝙤𝙣𝙨 𝙊𝙧𝙙𝙚𝙧𝙡𝙮 🔰\n\n**♻️ Sᴛᴇᴘ 1: Cʟɪᴄᴋ 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝟏\nWᴀɪᴛ 3 Sᴇᴄᴏɴᴅs\n♻️ Sᴛᴇᴘ 2: Cʟɪᴄᴋ 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝟐"**\n\n【🛞𝙉𝙤𝙩𝙚 : 𝙄𝙛 𝙊𝙣𝙡𝙮 𝙊𝙣𝙚 𝙅𝙤𝙞𝙣 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 𝘽𝙪𝙩𝙩𝙤𝙣 𝙏𝙝𝙚𝙣 𝙅𝙪𝙨𝙩 𝘾𝙡𝙞𝙘𝙠 𝙄𝙩 】\n\n**⭄ 𝗜 𝗪𝗶𝗹𝗹 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂 𝗧𝗵𝗲 𝗙𝗶𝗹𝗲 𝗔𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗰𝗮𝗹𝗹𝘆 ⥺**',
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN
                )
            if should_run_check_loop_sub:
                check = await check_loop_sub(client, message)
            elif should_run_check_loop_sub1:
                check = await check_loop_sub1(client, message)
            if check:     
                await sh.delete()                
            else:
                return 
    except Exception as e:
        return await message.reply(e)
    if temp.REQ_CHANNEL2 and not await is_requested_two(client, message):
        btn = [[
            InlineKeyboardButton(
                "Join channel", url=client.req_link2)
        ]]
        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton(" 🔄 Tʀʏ Aɢᴀɪɴ 🔄", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton(" 🔄 Tʀʏ Aɢᴀɪɴ 🔄", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        sh = await client.send_message(
            chat_id=message.from_user.id,
            text="Request To Join This Channel",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        check = await check_loop_sub2(client, message)
        if check:
            await sh.delete()
        else:
            return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘs ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('🔍 Sᴇᴀʀᴄʜ Fɪʟᴇ 🔍 ', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🪄 Oᴡɴᴇʀ 🪄', url='https://t.me/Sathan_Of_Telegram')
            ],[
            InlineKeyboardButton('⚠️ Group 1 ⚠️', url='https://t.me/Cinemathattakam_Group'),
            InlineKeyboardButton('✨ Group 2 ✨', url='https://t.me/Cinemathattakam_Group1')
            ],[
            InlineKeyboardButton('🥇 Mᴀɪɴ Cʜᴀɴɴᴇʟ 🥇', url='https://t.me/CT_Arena')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(
            text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                fileid=file_id,
                protect_content=True if pre == 'filep' else False,
                )
            filetype = msg.media
            file = getattr(msg, filetype)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('No such file exist.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption=title if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    try:
        ok = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if pre == 'filep' else False,
            )
    except Exception as e:
        print(e)
    replied = ok.id        
    await message.delete()    
    await client.schedule.add_job(ok.delete, 'date', run_date=datetime.now() + timedelta(seconds=PM_DEL))

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to the file with /delete that you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not a supported file format')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    # Check if the file exists in Media collection
    result_media1 = await Media2.collection.find_one({'_id': file_id})   
        
    if result_media1:
        # Delete from Media collection
        await Media2.collection.delete_one({'_id': file_id})    
    else:
        # File not found in both collections
        await msg.edit('File not found in the database')
        return

    await msg.edit('File is successfully deleted from the database')
    
@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
       reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media2.collection.drop()
    await message.answer('Piracy Is Crime')
    await message.message.edit('Succesfully Deleted All The Indexed Files.')

@Client.on_message(filters.command('restart') & filters.user(ADMINS))
async def restart(b, m):
    if os.path.exists(".git"):
        os.system("git pull")

    oo = await m.reply_text("Restarting...")
    await oo.delete()
    try:
        os.remove("TelegramBot.txt")
    except:
        pass
    os.execl(sys.executable, sys.executable, "bot.py")

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Gɪᴠᴇ ᴍᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ғɪʟᴇs.</b>")
    btn = [[
       InlineKeyboardButton("Yᴇs, Cᴏɴᴛɪɴᴜᴇ !", callback_data=f"killfilesdq#{keyword}")
       ],[
       InlineKeyboardButton("Nᴏ, Aʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ !", callback_data="close_data")
    ]]
    await message.reply_text(
        text="<b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ? Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ?\n\nNᴏᴛᴇ:- Tʜɪs ᴄᴏᴜʟᴅ ʙᴇ ᴀ ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )
    
@Client.on_message(filters.command("delete_duplicate") & filters.user(ADMINS))
async def delete_duplicate_files(client, message):
    ok = await message.reply("prosessing...")
    deleted_count = 0
    batch_size = 0
    async def remove_duplicates(collection1, unique_files, ok, deleted_count, batch_size):                        
        async for duplicate_file in collection1.find():
            file_size = duplicate_file["file_size"]
            file_id = duplicate_file["file_id"]
            if file_size in unique_files and unique_files[file_size] != file_id:
                result_media1 = await collection1.find_one({'_id': file_id})                
                if result_media1:
                    await collection1.collection.delete_one({'_id': file_id})               
                    deleted_count += 1                
                    if deleted_count % 100 == 0:
                        batch_size += 1
                        await ok.edit(f'<b>Processing: Deleted {deleted_count} files in {batch_size} batches.</b>')
        return deleted_count, batch_size
    # Get all four collections
    media1_collection = Media2
        
    # Get all files from each collection
    all_files = await media1_collection.find({}, {"file_id": 1, "file_size": 1}).to_list(length=None)
   
    unique_files = {}
    for file_info in all_files:
        file_id = file_info["file_id"]
        file_size = file_info["file_size"]
        if file_size not in unique_files:
           unique_files[file_size] = file_id

    # Delete duplicate files from each collection
    deleted_count, batch_size = await remove_duplicates(media1_collection, unique_files, ok, deleted_count, batch_size)
    deleted_count = deleted_count
    
    # Send a final message indicating the total number of duplicates deleted
    await message.reply(f"Deleted {deleted_count} duplicate files. in {batch_size} batches")
