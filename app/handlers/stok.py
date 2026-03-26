from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from app.database.connection import get_connection


async def cek_stok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(
                "Format:\n"
                "/stok KODEBARANG\n\n"
                "Contoh:\n"
                "/stok 01PPO006"
            )
            return

        itemid = context.args[0].upper()
        today = datetime.now()
        tgl = today.strftime('%Y-%m-%d')
        periode = 201905  # bisa nanti dibuat dinamis

        # ✅ Buka koneksi
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            EXEC dbo.rpStokPPIC
                @Tgl1     = ?,
                @Tgl2     = ?,
                @Loc      = '%',
                @PeriodeR = ?,
                @kategori = '%',
                @itemid   = ?
        """, tgl, tgl, periode, itemid)

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            await update.message.reply_text("Data stok tidak ditemukan")
            return

        stok_akhir = int(row[7] or 0)

        await update.message.reply_html(
            f"<b>📦 STOK BARANG</b>\n\n"
            f"Kode : <b>{row[0]}</b>\n"
            f"Nama : {row[1]}\n\n"
            f"<b>Stok Akhir : {stok_akhir:,} PCS</b>\n"
            f"Tanggal : {today.strftime('%d-%m-%Y')}"
        )

    except Exception as e:
        await update.message.reply_text(f"Terjadi kesalahan:\n{str(e)}")
