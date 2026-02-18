from .start import start
from .stok import cek_stok
from .po_beli import po_beli
from .po_prod import po_prod
from .kartu_stok import kartu_stok, kartu_callback

def register_handlers(app):
    from telegram.ext import CommandHandler, CallbackQueryHandler

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stok", cek_stok))
    app.add_handler(CommandHandler("po_beli", po_beli))
    app.add_handler(CommandHandler("po_produksi", po_prod))
    app.add_handler(CommandHandler("kartustok", kartu_stok))
    app.add_handler(CallbackQueryHandler(kartu_callback, pattern="^ks"))
