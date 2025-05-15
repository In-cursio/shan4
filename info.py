import re
from os import environ

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
SESSION = environ.get('SESSION', 'Media_searcher')
API_ID = int(environ.get('API_ID', '1436542'))
API_HASH = environ.get('API_HASH', 'ace9d0fb8f46300776a985ca357bdfff')
BOT_TOKEN="7543937424:AAGYKTAmCj85N-48R92mkTfbmHwrRCNmKAY"

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = False 
PICS = (environ.get('PICS', 'https://envs.sh/IxE.jpg?biuvm=1 https://envs.sh/IxD.jpg?aXHs4=1 https://envs.sh/IV-.jpg?Z20Yt=1 https://envs.sh/ozN.jpg?text=ilovSTARLEY https://envs.sh/ozH.jpg?text=ilovSTARLEY https://envs.sh/ozg.jpg?text=ilovSTARLEY')).split()
POST_CHANNELS = list(map(int, (channel.strip() for channel in environ.get('POST_CHANNELS', '-1001829897427').split(','))))

# Admins, Channels & Users
OWNER_ID = environ.get('OWNER_ID', '800422840')
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '5732252796 800422840 6874351976 6047510747').split()] 
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1001541833234 -1002468466489 -1001183379468 -1001765720202').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL', '-1001288505726')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# MongoDB information
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Chopperfiles')
DATABASE_URI2 = environ.get('DATABASE_URI2', "mongodb+srv://chopperv2db2:chopperv2db2@cluster0.8fcg1hf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://chopperv2db1:chopperv2db1@cluster0.vfxwmoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_URI3 = environ.get('DATABASE_URI3', "mongodb+srv://chopperv2db3:chopperv2db3@cluster0.gysrhid.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_URI4 = environ.get('DATABASE_URI4', "mongodb+srv://chopperv2db4:chopperv2db4@cluster0.hpj5c9h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# FSUB
BEFORE_REQ_TEXT = environ.get('BEFORE_REQ_TEXT', "Sending file...")
auth_channel = environ.get('AUTH_CHANNEL')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
# Set to False inside the bracket if you don't want to use Request Channel else set it to Channel ID
REQ_CHANNEL1=environ.get("REQ_CHANNEL1", None)
REQ_CHANNEL1 = (int(REQ_CHANNEL1) if REQ_CHANNEL1 and id_pattern.search(REQ_CHANNEL1) else False) if REQ_CHANNEL1 is not None else None
REQ_CHANNEL2 = environ.get("REQ_CHANNEL2", None)
REQ_CHANNEL2 = (int(REQ_CHANNEL2) if REQ_CHANNEL2 and id_pattern.search(REQ_CHANNEL2) else False) if REQ_CHANNEL2 is not None else None
JOIN_REQS_DB = environ.get("JOIN_REQS_DB", DATABASE_URI)
DELETE_TIMEOUT = int(environ.get('DELETE_TIMEOUT', 2*60*60)) # 2 hours in seconds

# Others
AUTO_DEL = int(120)
AUTO_DEL_MODE=True
PM_DEL = int(120)

LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002584403070'))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', '@CT_Arena')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "True")), True)
IMDB = is_enabled((environ.get('IMDB', "True")), False)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "True")), True)
CUSTOM_FILE_CAPTION = "<b>📂Fɪʟᴇɴᴀᴍᴇ :</b> <code>{file_name}</code>\n\n<b>╔═════•✧❅✦❅✧•═════╗\n▣ <a href=https://t.me/cinemathattakam_Group>[CT™] 📽സിനിമ തട്ടകം</a>\n▣ <a href=https://t.me/CT_Arena>[CT™] 📽സിനിമ തട്ടകം</a>\n╚═════•✧❅✦❅✧•═════╝</b>\n\n<pre>𝗪𝗮𝗿𝗻𝗶𝗻𝗴 ⚠️</pre>\n<blockquote>𝖥𝗂𝗅𝖾𝗌 𝖲𝖾𝗇𝖽 𝖶𝗂𝗅𝗅 𝖡𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝖿𝗍𝖾𝗋 5 𝖬𝗂𝗇𝗎𝗍𝖾𝗌 𝖳𝗈 𝖠𝗏𝗈𝗂𝖽 𝖢𝗈𝗉𝗒𝗋𝗂𝗀𝗁𝗍.𝖲𝗈 𝖲𝖺𝗏𝖾 𝖳𝗁𝖾 𝖥𝗂𝗅𝖾 𝖳𝗈 𝖲𝖺𝗏𝖾𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌</blockquote>"
BATCH_FILE_CAPTION = CUSTOM_FILE_CAPTION
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", "<b>Query: {query}</b> \n‌IMDb Data:\n\n🏷 Title: <a href={url}>{title}</a>\n🎭 Genres: {genres}\n📆 Year: <a href={url}/releaseinfo>{year}</a>\n🌟 Rating: <a href={url}/ratings>{rating}</a>")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", 10)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "False")), False)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "False")), False)

LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"
