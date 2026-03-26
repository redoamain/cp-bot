from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


# =========================
# MENU UTAMA
# =========================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Cek Stok", callback_data="menu_stok"),
            InlineKeyboardButton("📊 Kartu Stok", callback_data="menu_kartu")
        ],
        [
            InlineKeyboardButton("🛒 PO Pembelian", callback_data="menu_po"),
            InlineKeyboardButton("🏭 PO Produksi", callback_data="menu_poprod")
        ]
    ])


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 <b>INVENTORY MONITORING BOT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Silakan pilih menu di bawah:"
    )

    await update.message.reply_html(
        text,
        reply_markup=main_menu_keyboard()
    )


# =========================
# CALLBACK MENU
# =========================
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    # =========================
    # CEK STOK MENU
    # =========================
    if query.data == "menu_stok":

        text = (
            "📦 <b>CEK STOK</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Gunakan perintah:\n"
            "<code>/stok KODEBARANG</code>\n\n"
            "Contoh:\n"
            "<code>/stok 01PPO006</code>"
        )

        keyboard = [
            [InlineKeyboardButton("⬅️ Kembali", callback_data="menu_main")]
        ]

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    # =========================
    # KARTU STOK MENU
    # =========================
    elif query.data == "menu_kartu":

        text = (
            "📊 <b>KARTU STOK</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Gunakan perintah:\n"
            "<code>/kartustok KODE [tgl1] [tgl2]</code>\n\n"
            "Contoh:\n"
            "<code>/kartustok 01PPO006 2026-01-01 2026-02-01</code>"
        )

        keyboard = [
            [InlineKeyboardButton("⬅️ Kembali", callback_data="menu_main")]
        ]

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    # =========================
    # PO PEMBELIAN MENU
    # =========================
    elif query.data == "menu_po":

        text = (
            "🛒 <b>PO PEMBELIAN</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Gunakan perintah:\n"
            "<code>/po 2026-01-01 2026-02-01</code>"
        )

        keyboard = [
            [InlineKeyboardButton("⬅️ Kembali", callback_data="menu_main")]
        ]

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    # =========================
    # PO PRODUKSI MENU
    # =========================
    elif query.data == "menu_poprod":

        text = (
            "🏭 <b>PO PRODUKSI</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Gunakan perintah:\n"
            "<code>/poproduksi</code>"
        )

        keyboard = [
            [InlineKeyboardButton("⬅️ Kembali", callback_data="menu_main")]
        ]

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    # =========================
    # KEMBALI KE MENU UTAMA
    # =========================
    elif query.data == "menu_main":

        text = (
            "👋 <b>INVENTORY MONITORING BOT</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Silakan pilih menu di bawah:"
        )

        await query.message.edit_text(
            text,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
