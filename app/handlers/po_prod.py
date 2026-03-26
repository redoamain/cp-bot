from telegram import Update
from telegram.ext import ContextTypes
from collections import defaultdict
from datetime import datetime

from app.database.connection import get_connection


async def po_prod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                hd.OrderID,
                hd.OrderDate,
                hd.Remark,
                dt.ItemID,
                CAST(dt.Kgs AS INT) AS Qty
            FROM taPROrder hd
            JOIN taPROrderDt dt
              ON hd.OrderID = dt.OrderID
             AND hd.OrderType = dt.OrderType
            WHERE hd.Completed = '0'
              AND hd.OrderID LIKE 'AS%'
            ORDER BY hd.OrderDate DESC, hd.OrderID
        """)

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        if not rows:
            await _reply(update, "Tidak ada PO Produksi aktif")
            return

        # =========================
        # GROUPING
        # =========================
        data = defaultdict(lambda: {
            "tanggal": None,
            "remark": "",
            "items": []
        })

        for r in rows:
            orderid = r[0]

            data[orderid]["tanggal"] = r[1]
            data[orderid]["remark"] = r[2] or "-"
            data[orderid]["items"].append((r[3], int(r[4] or 0)))

        # =========================
        # FORMAT MESSAGE
        # =========================
        msg = "<b>🏭 PO PRODUKSI (ON PROCESS)</b>\n\n"

        for oid, val in data.items():

            tanggal = (
                val["tanggal"].strftime("%d-%m-%Y")
                if isinstance(val["tanggal"], datetime)
                else "-"
            )

            msg += (
                f"🆔 <b>{oid}</b>\n"
                f"📅 {tanggal}\n"
                f"📝 {val['remark']}\n"
                f"📦 Item:\n"
            )

            for itemid, qty in val["items"]:
                msg += f"   • {itemid} : {qty:,} PCS\n"

            msg += "──────────────────\n"

        # Antisipasi pesan terlalu panjang
        if len(msg) > 4000:
            msg = msg[:4000] + "\n\n...data dipotong..."

        await _reply(update, msg, html=True)

    except Exception as e:
        await _reply(update, f"Terjadi kesalahan:\n{str(e)}")


# =========================
# Helper reply universal
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
