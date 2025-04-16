from utils import temp
from utils import get_poster
from info import POST_CHANNELS
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
LANGUAGES = {
    'mal': 'Malayalam',
    'tam': 'Tamil', 
    'kan': 'Kannada', 
    'hin': 'Hindi', 
    'eng': 'English', 
    'tel': 'Telugu', 
    'kor': 'Korean',
    'chi': 'Chinese',
    'jap': 'Japanese',
    'multi': 'Multi-Language'
}

@Client.on_message(filters.command('getfile'))
async def getfile(client, message):
    try:
        query = message.text.split(" ", 1) 
        if len(query) < 2:
            return await message.reply_text("<b>Usage:</b> /getfile movie_name\n\nExample: /getfile Money Heist")
        file_name = query[1].strip() 
        movie_details = await get_poster(file_name)
        if not movie_details:
            return await message.reply_text(f"No results found for {file_name} on IMDB.")
        language_buttons = []
        for code, lang in LANGUAGES.items():
            language_buttons.append([InlineKeyboardButton(lang, callback_data=f"lang_{code}_{file_name}")])
        language_markup = InlineKeyboardMarkup(language_buttons)
        temp.current_movie = {
            'details': movie_details,
            'name': file_name
        }
        await message.reply_text(
            "Select the languages for this movie:",
            reply_markup=language_markup
        )
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@Client.on_callback_query(filters.regex(r'^lang_'))
async def language_selection(client, callback_query):
    _, lang_code, file_name = callback_query.data.split('_')
    if not hasattr(temp, 'selected_languages'):
        temp.selected_languages = []
    if lang_code == 'multi':
        temp.selected_languages = ['Multi-Language']
    elif lang_code in LANGUAGES:
        if LANGUAGES[lang_code] in temp.selected_languages:
            temp.selected_languages.remove(LANGUAGES[lang_code])
        else:
            if 'Multi-Language' in temp.selected_languages:
                temp.selected_languages.remove('Multi-Language')
            temp.selected_languages.append(LANGUAGES[lang_code])
    language_buttons = []
    for code, lang in LANGUAGES.items():
        button_text = f"✅ {lang}" if lang in temp.selected_languages else lang
        language_buttons.append([InlineKeyboardButton(button_text, callback_data=f"lang_{code}_{file_name}")])
    language_buttons.append([InlineKeyboardButton("Proceed", callback_data=f"proceed_{file_name}")])
    language_markup = InlineKeyboardMarkup(language_buttons)
    await callback_query.message.edit_text(
        "Select the languages for this movie:",
        reply_markup=language_markup
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r'^proceed_'))
async def preview_movie_details(client, callback_query):
    movie_details = temp.current_movie['details']
    file_name = temp.current_movie['name']
    selected_languages = ', '.join(temp.selected_languages) if hasattr(temp, 'selected_languages') else 'N/A'
    movie_title = movie_details.get('title', 'N/A')
    rating = movie_details.get('rating', 'N/A')
    genres = movie_details.get('genres', 'N/A')
    year = movie_details.get('year', 'N/A')
    preview_text = (
        f"✅ {movie_title} {year}\n\n"
        f"🎙 {selected_languages}\n\n"
        f"📽 Genre: {genres}"
    )
    confirm_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes, Post", callback_data=f"post_yes_{file_name}")],
        [InlineKeyboardButton("No, Cancel", callback_data=f"post_no_{file_name}")]
    ])
    await callback_query.message.edit_text(
        preview_text, 
        reply_markup=confirm_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r'^post_(yes|no)_'))
async def post_to_channels(client, callback_query):
    action, file_name = callback_query.data.split('_')[1], callback_query.data.split('_')[2]
    if action == "yes":
        movie_details = await get_poster(file_name)
        if not movie_details:
            return await callback_query.message.reply_text(f"No results found for {file_name} on IMDB.")
        movie_title = movie_details.get('title', 'N/A')
        rating = movie_details.get('rating', 'N/A')
        genres = movie_details.get('genres', 'N/A')
        year = movie_details.get('year', 'N/A')
        selected_languages = ', '.join(temp.selected_languages) if hasattr(temp, 'selected_languages') else 'N/A'
        custom_link = f"https://t.me/{temp.U_NAME}?start=getfile-{file_name.replace(' ', '-').lower()}"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Gᴇᴛ Fɪʟᴇ 📁", url=custom_link)
        ]])
        caption = (
            f"<b>✅ {movie_title} ({year})</b>\n\n"
            f"<b>🎙️ {selected_languages}</b>\n\n"
            f"<b>📽️ Genres: {genres}</b>"                      
        )
        for channel_id in POST_CHANNELS:
            try:
                await client.send_message(
                    chat_id=channel_id,
                text=caption,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception as e:
                await callback_query.message.reply_text(f"Error posting to channel {channel_id}: {str(e)}")
        await callback_query.message.edit_text("Movie details successfully posted to channels.")
    elif action == "no":
        await callback_query.message.edit_text("Movie details will not be posted to channels.")
