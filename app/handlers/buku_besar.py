from telegram import Update
from telegram.ext import ContextTypes
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from io import BytesIO
from datetime import datetime
from app.database.connection import get_cursor
from app.utils.helpers import fmt_date

async def buku_besar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # ================= VALIDASI FORMAT =================
        if len(context.args) != 2:
            await update.message.reply_text(
                "Format:\n"
                "/bukubesar TGL1 TGL2\n\n"
                "Contoh:\n"
                "/bukubesar 2025-12-16 2025-12-31"
            )
            return

        # ================= PARSE TANGGAL =================
        try:
            tgl1 = datetime.strptime(context.args[0], "%Y-%m-%d").strftime("%Y-%m-%d")
            tgl2 = datetime.strptime(context.args[1], "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            await update.message.reply_text("Format tanggal harus YYYY-MM-DD")
            return

        acc1 = "1101"
        acc2 = "7301"

        loading_msg = await update.message.reply_text("⏳ Sedang generate laporan Buku Besar...")

        cursor = get_cursor()

        # ================= EXEC STORE PROCEDURE =================
        cursor.execute("""
            SET NOCOUNT ON;
            EXEC dbo.rpBBPembantuL
                @Tgl1 = ?,
                @Tgl2 = ?,
                @Acc1 = ?,
                @Acc2 = ?,
                @ju = 0,
                @Curr = '%',
                @lawantransksi = 1
        """, (tgl1, tgl2, acc1, acc2))

        # Lewati semua result set sampai mendapatkan dataset utama
        while True:
            if cursor.description:
                break
            if not cursor.nextset():
                break

        rows = cursor.fetchall()
        if not rows:
            await update.message.reply_text("Tidak ada data Buku Besar")
            return

        # ================= BUAT WORKBOOK =================
        wb = Workbook()
        ws = wb.active
        ws.title = "Buku Besar"

        # ================= HEADER TETAP =================
        header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")

        # Row 1 - Judul
        ws.merge_cells("A1:K1")
        ws["A1"] = "BUKU BESAR"
        ws["A1"].font = Font(size=16, bold=True)
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        for col in range(1, 12):
            ws.cell(row=1, column=col).fill = header_fill

        # Row 2 - Nama Perusahaan
        ws.merge_cells("A2:K2")
        ws["A2"] = "PT CITI PLUMB"
        ws["A2"].font = Font(size=13, bold=True)
        ws["A2"].alignment = Alignment(horizontal="center", vertical="center")

        # Row 3 - Spasi (tetap dipertahankan, tidak akan masuk area filter data)
        ws.merge_cells("A3:K3")

        # Row 4 - Periode
        ws.merge_cells("A4:K4")
        ws["A4"] = f"Periode : {tgl1} s/d {tgl2}"
        ws["A4"].font = Font(size=11, italic=True)
        ws["A4"].alignment = Alignment(horizontal="center")

        # ================= HEADER TABEL =================
        start_row = 7
        ws.merge_cells(f"A{start_row}:A{start_row+1}")
        ws.merge_cells(f"B{start_row}:B{start_row+1}")
        ws.merge_cells(f"C{start_row}:C{start_row+1}")
        ws.merge_cells(f"D{start_row}:D{start_row+1}")
        ws.merge_cells(f"E{start_row}:E{start_row+1}")
        ws.merge_cells(f"F{start_row}:G{start_row}")
        ws.merge_cells(f"H{start_row}:I{start_row}")
        ws.merge_cells(f"J{start_row}:J{start_row+1}")
        ws.merge_cells(f"K{start_row}:K{start_row+1}")

        ws[f"A{start_row}"] = "Tanggal"
        ws[f"B{start_row}"] = "No. Bukti"
        ws[f"C{start_row}"] = "Remark"
        ws[f"D{start_row}"] = "COA Transaksi"
        ws[f"E{start_row}"] = "Curr"
        ws[f"F{start_row}"] = "Debet"
        ws[f"H{start_row}"] = "Credit"
        ws[f"J{start_row}"] = "Saldo"
        ws[f"K{start_row}"] = "Saldo(Rp)"
        ws[f"F{start_row+1}"] = "Total"
        ws[f"G{start_row+1}"] = "Total(Rp)"
        ws[f"H{start_row+1}"] = "Total"
        ws[f"I{start_row+1}"] = "Total(Rp)"

        for row in ws[f"A{start_row}:K{start_row+1}"]:
            for cell in row:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")

        # ================= UTILITY =================
        def safe_num(val):
            try:
                return float(val)
            except:
                return 0.0

        # ================= MULAI MENULIS DATA =================
        grand_debet = grand_debetrp = grand_credit = grand_creditrp = 0

        current_acc = None
        total_debet = total_debetrp = total_credit = total_creditrp = 0
        saldo = 0

        for i, r in enumerate(rows):
            acc = r[2]
            accname = r[3]

            # Jika berganti akun
            if current_acc != acc:
                # Sebelum pindah, tulis total akun sebelumnya (jika ada)
                if current_acc is not None:
                    # Total per akun (tanpa baris kosong)
                    ws.append([
                        "", "", "TOTAL ACCOUNT", "", "",
                        "", total_debetrp, "", total_creditrp, "", ""
                    ])
                    # Set bold untuk baris total
                    for col in range(1, 12):
                        ws.cell(row=ws.max_row, column=col).font = Font(bold=True)

                # Header akun baru
                ws.append([f"ACCOUNT : {acc} - {accname}", "", "", "", "", "", "", "", "", "", ""])
                ws.cell(row=ws.max_row, column=1).font = Font(bold=True)

                # Reset total per akun
                total_debet = total_debetrp = total_credit = total_creditrp = 0
                saldo = 0
                current_acc = acc

            # ===== Baca data baris =====
            tanggal = fmt_date(r[1])
            nobukti = r[0]
            remark = r[4]
            curr = r[5]
            lawantransaksi = r[13]
            beginrp = float(r[8] or 0)
            debet = safe_num(r[9])
            debetrp = float(r[10] or 0)
            credit = safe_num(r[11])
            creditrp = float(r[12] or 0)

            # Akumulasi per akun
            total_debet += debet
            total_debetrp += debetrp
            total_credit += credit
            total_creditrp += creditrp

            # Grand total semua akun
            grand_debet += debet
            grand_debetrp += debetrp
            grand_credit += credit
            grand_creditrp += creditrp

            # Hitung saldo
            if "SALDO AWAL" in str(remark).upper():
                saldo = beginrp
            else:
                saldo += debetrp - creditrp

            # Tulis baris data
            ws.append([
                tanggal,
                nobukti,
                remark,
                lawantransaksi,
                curr,
                0,
                debetrp,
                0,
                creditrp,
                0,
                saldo
            ])

        # ===== Total akun terakhir =====
        if current_acc is not None:
            ws.append([
                "", "", "TOTAL ACCOUNT", "", "",
                "", total_debetrp, "", total_creditrp, "", ""
            ])
            for col in range(1, 12):
                ws.cell(row=ws.max_row, column=col).font = Font(bold=True)

        # ===== GRAND TOTAL SEMUA AKUN =====
        ws.append([
            "", "", "GRAND TOTAL SEMUA ACCOUNT", "", "",
            grand_debet,
            grand_debetrp,
            grand_credit,
            grand_creditrp,
            "",
            ""
        ])
        grand_row = ws.max_row
        for col in range(1, 12):
            ws.cell(row=grand_row, column=col).font = Font(size=12, bold=True)

        # ===== AUTO WIDTH =====
        for col in range(1, ws.max_column + 1):
            max_len = 0
            col_letter = get_column_letter(col)
            for row in range(1, ws.max_row + 1):
                cell = ws.cell(row=row, column=col)
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max_len + 2

        # ===== KIRIM FILE =====
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)

        filename = f"BukuBesar_{acc1}-{acc2}_{tgl1}_sd_{tgl2}.xlsx"
        await loading_msg.edit_text("📊 Laporan selesai dibuat, mengirim file...")
        await update.message.reply_document(
            document=file_stream,
            filename=filename,
            caption=f"Buku Besar {acc1}-{acc2} {tgl1} sd {tgl2}"
        )
        await loading_msg.edit_text("✅ Buku Besar berhasil dikirim")

    except Exception as e:
        await update.message.reply_text(f"Error:\n{e}")