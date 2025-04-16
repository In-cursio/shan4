import asyncio
import re, traceback
import ast
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from info import ADMINS, AUTO_DEL_MODE, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, AUTO_DEL, PM_DEL, BEFORE_REQ_TEXT
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, temp
from database.users_chats_db import db
from database.ia_filterdb import get_file_details, get_search_results, get_bad_files
from database.gfilters_mdb import find_gfilter, get_gfilters
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message(filters.text & filters.incoming & filters.group)
async def give_filter(client, message):
    ok = await global_filters(client, message)
    if ok == False:
        await auto_filter(client, message)       
        
@Client.on_message(filters.private & filters.incoming)
async def give_fpm(client, message):
    ok = await global_filters(client, message)
    if ok == False:
        await auto_filter(client, message)
  
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset, from_user1 = query.data.split("_")
    user_id = query.from_user.id
    if int(from_user1) != int(user_id):
        await query.answer(text="𝙏𝙝𝙞𝙨 𝙊𝙣𝙚 𝙄𝙨 𝙉𝙤𝙩 𝙔𝙤𝙪𝙧 𝙎𝙚𝙖𝙧𝙘𝙝 𝙄 𝙂𝙪𝙚𝙨𝙨🫸, 𝙎𝙚𝙖𝙧𝙘𝙝 𝙁𝙤𝙧 𝙔𝙤𝙪𝙧 𝙊𝙬𝙣 𝙁𝙞𝙡𝙚 🔍🗿")
        return
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("oKda", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    btn = [
        [
            InlineKeyboardButton(
                text=f"🎭[CT™]☞ {get_size(file.file_size)} ➽ {file.file_name}", callback_data=f'files#{file.file_id}'
            ),
        ]
        for file in files
    ]
    
    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}_{from_user1}"),
             InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{off_set}_{from_user1}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}_{from_user1}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{off_set}_{from_user1}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()                        
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id, from_user1 = query.data.split("#")
        user_id = query.from_user.id
        if int(from_user1) != int(user_id):
            await query.answer(text="𝙏𝙝𝙞𝙨 𝙊𝙣𝙚 𝙄𝙨 𝙉𝙤𝙩 𝙔𝙤𝙪𝙧 𝙎𝙚𝙖𝙧𝙘𝙝 𝙄 𝙂𝙪𝙚𝙨𝙨🫸, 𝙎𝙚𝙖𝙧𝙘𝙝 𝙁𝙤𝙧 𝙔𝙤𝙪𝙧 𝙊𝙬𝙣 𝙁𝙞𝙡𝙚 🔍🗿 ")
            return
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')        
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption = title if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"        
        try:
            #await query.answer(BEFORE_REQ_TEXT)
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
            return         
        except QueryIdInvalid:
            await query.answer("This query is no longer valid.", show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if temp.REQ_CHANNEL1 and not await is_requested_one(client, query):
            await query.answer("നിങ്ങൾ മുകളിൽ കാണുന്ന ചാനലിൽ ജോയിൻ ആയിട്ടില്ല❌ ഒന്നൂടെ ആയി നോക്കുക ശേഷം സിനിമ വരും✅\n\n𝗌𝗈𝗅𝗏𝖾 𝗂𝗌𝗌𝗎𝖾?-Gᴜʏs, Tʜᴇʀᴇ Aʀᴇ 2 Cʜᴀɴɴᴇʟs Tᴏ Jᴏɪɴ, Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ғɪʀsᴛ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴡᴀɪᴛ ғᴏʀ 5 sᴇᴄᴏɴᴅs , ᴀɴᴅ ᴛʜᴇɴ ᴊᴏɪɴ ᴛʜᴇ sᴇᴄᴏɴᴅ ᴄʜᴀɴɴᴇʟ , Tʜᴀɴᴋ Yᴏᴜ🤗", show_alert=True)
            return
        if temp.REQ_CHANNEL2 and not await is_requested_two(client, query):
            await query.answer("Update Channel 2 ഒന്നൂടെ ജോയിൻ ആവുക എന്നിട്ട് Try Again ക്ലിക്ക് ചെയ്യുക സിനിമ കിട്ടുന്നതാണ്🫶🏼\n\n𝗌𝗈𝗅𝗏𝖾 𝗂𝗌𝗌𝗎𝖾?-Gᴜʏs, Tʜᴇʀᴇ Aʀᴇ 2 Cʜᴀɴɴᴇʟs Tᴏ Jᴏɪɴ, Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ғɪʀsᴛ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴡᴀɪᴛ ғᴏʀ 5 sᴇᴄᴏɴᴅs , ᴀɴᴅ ᴛʜᴇɴ ᴊᴏɪɴ ᴛʜᴇ sᴇᴄᴏɴᴅ ᴄʜᴀɴɴᴇʟ , Tʜᴀɴᴋ Yᴏᴜ🤗", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.file_name
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"        
        await query.answer()
        xd = await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == "checksubp" else False            
        )
        replied = xd.id    
        da = await message.reply(DELETE_TXT, reply_to_message_id=replied)
        await asyncio.sleep(30)
        await message.delete()
        await da.delete()
        await asyncio.sleep(PM_DEL)
        await xd.delete()
    elif query.data == "pages":
        await query.answer("⚠️ 𝖧ᴇʏ !\n𝖲ᴇᴀʀᴄʜ 𝖸ᴏᴜʀ 𝖮ᴡɴ 𝖥ɪʟᴇ,\n\n𝖣ᴏɴ'ᴛ 𝖢ʟɪᴄᴋ 𝖮ᴛʜᴇʀ𝗌 𝖱ᴇ𝗌ᴜʟᴛ𝗌 😬", show_alert=True)
    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        print("loading..")
        await query.message.edit_text(f"<b>Fᴇᴛᴄʜɪɴɢ Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} ᴏɴ DB... Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        print("loading..ok")
        files_media1, files_media2, files_media3, total_media = await get_bad_files(keyword)        
        await query.message.edit_text(f"<b>Fᴏᴜɴᴅ {total_media} Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nFɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴘʀᴏᴄᴇss ᴡɪʟʟ sᴛᴀʀᴛ ɪɴ 5 sᴇᴄᴏɴᴅs!</b>")
        print("loading..")
        deleted = 0
        try:
                # Delete files from Media collection
            print("loading..1")
            for file in files_media1:
                file_ids = file.file_id
                file_name = file.file_name
                result = await Media2.collection.delete_one({
                    '_id': file_ids,
                })
                if result.deleted_count:
                    logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                deleted += 1
                print("delted..")
                if deleted % 100 == 0:
                    await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
                # Delete files from Mediaa collection
            for file in files_media2:
                file_ids = file.file_id
                file_name = file.file_name
                result = await Media3.collection.delete_one({
                    '_id': file_ids,
                })
                if result.deleted_count:
                    logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                deleted += 1
                if deleted % 100 == 0:
                    await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
            for file in files_media3:
                file_ids = file.file_id
                file_name = file.file_name
                result = await Media4.collection.delete_one({
                    '_id': file_ids,
                })
                if result.deleted_count:
                    logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                deleted += 1
                if deleted % 100 == 0:
                    await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        except Exception as e:
            logger.exception
            await query.message.edit_text(f'Eʀʀᴏʀ: {e}')
        else:
            await query.message.edit_text(f"<b>Pʀᴏᴄᴇss Cᴏᴍᴘʟᴇᴛᴇᴅ ғᴏʀ ғɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ !\n\nSᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}.</b>")
            
    elif query.data == "start":
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
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('Piracy Is Crime')    
    
async def auto_filter(client, msg, spoll=False):
    user_id = msg.from_user.id
    if not spoll:
        message = msg
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 150:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                reqst_gle = search.replace(" ", "+")
                button = [[
                           InlineKeyboardButton("🔍 𝗦𝗲𝗮𝗿𝗰𝗵 𝗧𝗵𝗲 𝗙𝗶𝗹𝗲 𝗡𝗮𝗺𝗲 𝗙𝗿𝗼𝗺 𝗚𝗼𝗼𝗴𝗹𝗲 🔎", url=f"https://www.google.com/search?q={reqst_gle}")
                ]]
                okd = await msg.reply(
                    text=f"<b>𝗛ᴇʏ {msg.from_user.mention} [😔](https://i.ibb.co/HDPJ5Np1/f87be38fcd9b.jpg),\nCᴏᴜʟᴅɴ'ᴛ Fɪɴᴅ Tʜᴇ Fɪʟᴇ Yᴏᴜ Rᴇqᴜᴇꜱᴛᴇᴅ.\nMᴀᴋᴇ Sᴜʀᴇ Tʜᴇ Cᴏʀʀᴇᴄᴛ Sᴩᴇʟʟɪɴɢ.\nTʀʏ Sᴇᴀʀᴄʜɪɴɢ</b> <code>{search}</code> <b>ᴏɴ Gᴏᴏɢʟᴇ!</b>",                                                  
                    reply_to_message_id=msg.id,
                    reply_markup=InlineKeyboardMarkup(button),
                    parse_mode=None,
                )
                if AUTO_DEL_MODE:
                    await client.schedule.add_job(okd.delete, 'date', run_date=datetime.now() + timedelta(seconds=15))
                    return
        else:
            return
    else:      
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'file'
    btn = [
        [
            InlineKeyboardButton(
                text=f"🎭[CT™]☞ {get_size(file.file_size)} ➽ {file.file_name}", callback_data=f'{pre}#{file.file_id}#{user_id}'
            ),
        ]
        for file in files
    ]
    if total_results <= 10:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    else:
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
                InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}_{user_id}")]
        )    
    cap = f"**🎪 ᴛɪᴛɪʟᴇ {search}\n\n┏ 🤴 ᴀsᴋᴇᴅʙʏ : {message.from_user.mention}\n┣⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ : <a href='https://t.me/{temp.U_NAME}'>Tᴏɴʏ Tᴏɴʏ Cʜᴏᴘᴘᴇʀ 🐻</a>\n┗🍁 ᴄʜᴀɴɴᴇʟ : <a href='https://t.me/CT_Arena'>Cinemathattakam</a>\n\nᴀꜰᴛᴇʀ 10 ᴍɪɴᴜᴛᴇꜱ ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇᴅ\n\n★ ᴘᴏᴡᴇʀᴇᴅ ʙʏ : {message.chat.title}\n\n<blockquote>Sᴇᴀʀᴄʜᴇᴅ Fɪʟᴇ : {search} | Tᴏᴛᴀʟ Rᴇsᴜʟᴛs : {total_results}</blockquote>**"    
    ok = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=None, disable_web_page_preview=True)
    if AUTO_DEL_MODE:
        await client.schedule.add_job(ok.delete, 'date', run_date=datetime.now() + timedelta(seconds=AUTO_DEL))
        
async def global_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            knd3 = await client.send_message(
                                group_id, 
                                reply_text, 
                                parse_mode=None,
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(60)
                            await knd3.delete()
                            await message.delete()

                        else:
                            button = eval(btn)
                            knd2 = await client.send_message(
                                group_id,
                                reply_text,
                                parse_mode=None,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(60)
                            await knd2.delete()
                            await message.delete()

                    elif btn == "[]":
                        knd1 = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id,
                            parse_mode=None,
                            disable_web_page_preview=True
                        )
                        await asyncio.sleep(60)
                        await knd1.delete()
                        await message.delete()

                    else:
                        button = eval(btn)
                        knd = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id,
                            parse_mode=None,
                            disable_web_page_preview=True
                        )
                        await asyncio.sleep(60)
                        await knd.delete()
                        await message.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
