import os
import tldextract
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.error import BadRequest

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "@S1ecurity_Pro"
CHANNEL_LINK = "https://t.me/S1ecurity_Pro"
BOT_NAME = "تحقق PRO"

async def is_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except BadRequest:
        return False

def analyze_link(url):
    url_lower = url.lower()
    threats = [] 
    ext = tldextract.extract(url)
    domain = f"{ext.domain}.{ext.suffix}"
    
    if not url_lower.startswith("https://"):
        threats.append("البروتوكول غير مشفر HTTP")
    if "chatid=" in url_lower:
        threats.append("يحتوي على chatid لاستهداف حساب تيليجرام")
    if "c.html" in url_lower:
        threats.append("يحتوي على صفحة مزورة c.html")
    if "verify=" in url_lower:
        threats.append("يحتوي على verify للخداع")
    if domain == "faceboook.com":
        threats.append("انتحال نطاق فيسبوك faceboook.com")

    if threats:
        report = f"تقرير تحقق PRO: الرابط غير آمن\nالاسباب المرصودة:\n- " + "\n- ".join(threats)
        report += "\n\nالتوصية: تجنب فتح الرابط وعدم ادخال اي بيانات"
        return report
    else:
        report = f"تقرير تحقق PRO: الرابط آمن مبدئيا\nلم يتم رصد مؤشرات خطر واضحة\nتنبيه: هذا فحص اولي ولا يغني عن الحذر"
        return report

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_member(user_id, context):
        await update.message.reply_text(
            "👋 مرحبًا بك في بوت تحقق PRO\n"
            "أهلًا وسهلًا بك، يسعدنا خدمتك في نظام فحص الروابط الآمن.\n"
            "🔎 كيف تعمل الخدمة؟\n"
            "أرسل أي رابط تريد التحقق منه\n"
            "سيتم فحصه تلقائيًا من حيث الأمان والموثوقية\n"
            "وستصلك النتيجة فورًا (آمن / مشبوه / غير موثوق)"
        )
    else:
        keyboard = [[InlineKeyboardButton("الاشتراك في القناة", url=CHANNEL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "لاستخدام بوت تحقق PRO يجب الاشتراك في القناة الرسمية اولا.\n"
            "بعد الاشتراك ارسل امر start مرة اخرى.",
            reply_markup=reply_markup
        )

async def check_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [[InlineKeyboardButton("الاشتراك في القناة", url=CHANNEL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("الوصول مرفوض. يجب الاشتراك في قناة S1ecurity_Pro اولا.", reply_markup=reply_markup)
        return
    url = update.message.text
    if "http" not in url:
        await update.message.reply_text("يرجى ارسال رابط كامل يبدأ ب https://")
        return
    waiting_msg = await update.message.reply_text("جار الفحص يرجى الانتظار...")
    result = analyze_link(url)
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=waiting_msg.message_id)
    except BadRequest:
        pass
    await update.message.reply_text(result, disable_web_page_preview=True)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_link))
print(f"{BOT_NAME} يعمل الان...")
app.run_polling()