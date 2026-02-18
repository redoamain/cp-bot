from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from openpyxl import Workbook

from app.database.connection import get_cursor
from app.utils.helpers import fmt_date, safe_str
from datetime import datetime


def build_data(rows):
    data = [["Tanggal","Gudang","Kegiatan","Ket","IN","OUT","Saldo"]]

    saldo = 0
    total_in = 0
    total_out = 0

    for r in rows:
        tanggal = fmt_date(r[3])
        gudang = safe_str(r[0], 15)
        kegiatan = safe_str(r[4], 10)

        qty_in = int(r[7] or 0)
        qty_out = int(r[8] or 0)

        saldo += qty_in - qty_out
        total_in += qty_in
        total_out += qty_out

        data.append([
            tanggal,
            gudang,
            kegiatan,
            safe_str(r[11], 20),
            qty_in,
            qty_out,
            saldo
        ])

    # =========================
    # TAMBAH BARIS TOTAL
    # =========================
    data.append([
        "",
        "",
        "",
        "TOTAL",
        total_in,
        total_out,
        saldo
    ])

    return data



async def kartu_stok(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "/kartustok KODE [tgl1] [tgl2]"
        )
        return

    itemid = context.args[0]

    if len(context.args) >= 3:
        tgl1 = context.args[1]
        tgl2 = context.args[2]
    else:
        tgl1 = datetime.now().strftime('%Y-%m-01')
        tgl2 = datetime.now().strftime('%Y-%m-%d')

    cursor = get_cursor()

    cursor.execute("""
        EXEC rpKartuStockBrgLBOT
            @TGL1=?, @TGL2=?, @LOC='%',
            @ITEM='%', @PeriodeR=?,
            @kategori='%', @itemid=?
    """, tgl1, tgl2, 201905, itemid)

    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("Data kosong")
        return

    data = build_data(rows)

    # ===== IMAGE =====
    buffer = BytesIO()
    fig, ax = plt.subplots(figsize=(18, len(data)*0.4))
    ax.axis('off')

    table = ax.table(
        cellText=data[1:],
        colLabels=data[0],
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(8)

    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)

    keyboard = [[
        InlineKeyboardButton("📊 Excel",
            callback_data=f"ks|{itemid}|{tgl1}|{tgl2}|excel")
    ]]

    await update.message.reply_photo(
        photo=buffer,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def kartu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data_cb = query.data.split("|")

    itemid = data_cb[1]
    tgl1 = data_cb[2]
    tgl2 = data_cb[3]

    cursor = get_cursor()

    cursor.execute("""
        EXEC rpKartuStockBrgLBOT
            @TGL1=?, @TGL2=?, @LOC='%',
            @ITEM='%', @PeriodeR=?,
            @kategori='%', @itemid=?
    """, tgl1, tgl2, 201905, itemid)

    rows = cursor.fetchall()

    data = build_data(rows)

    wb = Workbook()
    ws = wb.active

    for row in data:
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    await query.message.reply_document(
        document=buffer,
        filename=f"kartu_stok_{itemid}.xlsx"
    )
