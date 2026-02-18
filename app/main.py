from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from app.config.settings import BOT_TOKEN
from app.handlers.kartu_stok import kartu_stok, kartu_callback
from app.handlers.start import start, menu_callback
from app.handlers.po_beli import po_beli
from app.handlers.po_prod import po_prod
from app.handlers.stok import cek_stok
from app.handlers.buku_besar import buku_besar
def create_app():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(CommandHandler("stok", cek_stok))
    app.add_handler(CommandHandler("po_beli", po_beli))
    app.add_handler(CommandHandler("po_produksi", po_prod))
    app.add_handler(CommandHandler("menu", menu_callback))
    app.add_handler(CommandHandler("kartustok", kartu_stok))
    app.add_handler(CommandHandler("bukubesar", buku_besar))
    app.add_handler(CallbackQueryHandler(kartu_callback, pattern="^ks"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))


    return app
