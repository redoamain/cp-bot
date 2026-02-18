from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from collections import defaultdict

from app.database.connection import get_connection


async def po_beli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # =========================
        # Periode
        # =========================
        if len(context.args) == 2:
            tgl1 = context.args[0]
            tgl2 = context.args[1]
        else:
            today = datetime.now()
            tgl1 = today.strftime('%Y-%m-01')
            tgl2 = today.strftime('%Y-%m-%d')

        # =========================
        # DB
        # =========================
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            EXEC rpMonitoringPO
                @tgl1 = ?,
                @tgl2 = ?,
                @no = '%',
                @item = '%',
                @company = '%',
                @tipe = '%',
                @userinput = 0
        """, tgl1, tgl2)

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        if not rows:
            await _reply(update, "Tidak ada data PO Pembelian")
            return

        # =========================
        # GROUPING
        # =========================
        po_data = defaultdict(lambda: {
            "orderdate": None,
            "supplier": "",
            "items": [],
            "total_po": 0,
            "total_datang": 0,
            "completed": 0,
            "canceled": 0
        })

        for r in rows:
            orderid = r[0]

            po_data[orderid]["orderdate"] = r[2]
            po_data[orderid]["supplier"] = r[5]
            po_data[orderid]["completed"] = r[21]
            po_data[orderid]["canceled"] = r[22]

            qty_po = int(r[9] or 0)
            qty_datang = int(r[14] or 0)

            po_data[orderid]["items"].append({
                "item": r[8],
                "po": qty_po,
                "datang": qty_datang
            })

            po_data[orderid]["total_po"] += qty_po
            po_data[orderid]["total_datang"] += qty_datang

        # =========================
        # FORMAT MESSAGE
        # =========================
        msg = (
            "<b>🛒 MONITORING PO PEMBELIAN</b>\n"
            f"Periode: {tgl1} s/d {tgl2}\n\n"
        )

        for orderid, d in po_data.items():

            # Status Logic
            if d["canceled"] == 1:
                status = "❌ BATAL"
            elif d["completed"] == 1:
                status = "✅ SELESAI"
            elif d["total_datang"] == 0:
                status = "⏳ BELUM DATANG"
            elif d["total_datang"] < d["total_po"]:
                status = "🚚 DATANG SEBAGIAN"
            else:
                status = "✅ LENGKAP"

            tanggal = (
                d["orderdate"].strftime("%d-%m-%Y")
                if isinstance(d["orderdate"], datetime)
                else "-"
            )

            msg += (
                f"{status}\n"
                f"🆔 <b>{orderid}</b>\n"
                f"📅 {tanggal}\n"
                f"🏭 {d['supplier']}\n"
                f"<b>Item:</b>\n"
            )

            for it in d["items"]:
                msg += (
                    f"• {it['item']}\n"
                    f"  PO     : {it['po']:,} PCS\n"
                    f"  Datang : {it['datang']:,} PCS\n"
                )

            msg += (
                f"\n<b>Total PO</b>     : {d['total_po']:,} PCS\n"
                f"<b>Total Datang</b> : {d['total_datang']:,} PCS\n"
                f"────────────────────\n"
            )

        # Anti limit telegram
        if len(msg) > 4000:
            msg = msg[:4000] + "\n\n...data dipotong..."

        await _reply(update, msg, html=True)

    except Exception as e:
        await _reply(update, f"Terjadi kesalahan:\n{str(e)}")


# =========================
# Universal Reply Helper
# =========================
async def _reply(update: Update, text: str, html: bool = False):
    if update.message:
        if html:
            await update.message.reply_html(text)
        else:
            await update.message.reply_text(text)
    elif update.callback_query:
        if html:
            await update.callback_query.message.reply_html(text)
        else:
            await update.callback_query.message.reply_text(text)
