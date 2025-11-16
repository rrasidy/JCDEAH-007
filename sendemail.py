import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("send_agg_email")

OUTPUT_DIR = r"C:\Users\Robert\Downloads\output_aggregations"

EXPECTED_FILES = {
    "agg1_total_trip_per_hari": "agg1_total_trip_per_hari.csv",
    "agg2_total_trip_per_hari_per_service": "agg2_total_trip_per_hari_per_service.csv",
    "agg3_rata2_jarak_per_hari": "agg3_rata2_jarak_per_hari.csv",
    "agg4_revenue_per_hari": "agg4_revenue_per_hari.csv",
    "agg5_rata2_penumpang_per_hari": "agg5_rata2_penumpang_per_hari.csv",
}

def build_agg_descriptions() -> dict:
    return {
        "agg1_total_trip_per_hari": (
            "Total Trip per Hari - berisi jumlah total perjalanan yang terjadi pada setiap hari. "
            "Data ini memberikan gambaran mengenai tingkat aktivitas transportasi harian "
            "serta pola permintaan layanan taksi."
        ),
        "agg2_total_trip_per_hari_per_service": (
            "Total Trip per Hari per Service - berisi jumlah perjalanan per hari yang dipisahkan "
            "berdasarkan jenis layanan (misalnya Yellow Taxi dan Green Taxi). Informasi ini "
            "bermanfaat untuk membandingkan performa masing-masing jenis armada."
        ),
        "agg3_rata2_jarak_per_hari": (
            "Rata-Rata Jarak Tempuh per Hari - berisi nilai rata-rata jarak tempuh perjalanan "
            "pada setiap hari. Agregasi ini membantu memahami pola mobilitas penumpang, "
            "apakah perjalanan cenderung berjarak pendek atau panjang."
        ),
        "agg4_revenue_per_hari": (
            "Revenue per Hari - berisi total pendapatan harian yang dihasilkan dari seluruh perjalanan, "
            "termasuk komponen tarif dasar, tip, dan biaya tambahan lainnya. Data ini dapat digunakan "
            "untuk memantau kinerja finansial harian."
        ),
        "agg5_rata2_penumpang_per_hari": (
            "Rata-Rata Jumlah Penumpang per Hari - berisi nilai rata-rata jumlah penumpang per perjalanan "
            "pada setiap hari. Informasi ini menggambarkan karakteristik penggunaan layanan, apakah lebih "
            "banyak digunakan secara individu atau oleh kelompok kecil."
        ),
    }


def build_email_body(agg_descriptions: dict) -> str:
    lines = []
    lines.append("Yth. Bapak/Ibu,\n")
    lines.append(
        "Berikut kami sampaikan laporan hasil agregasi data perjalanan layanan taksi dalam bentuk file CSV "
        "yang terlampir pada email ini. Setiap file mewakili jenis agregasi yang berbeda dengan penjelasan "
        "sebagai berikut:\n"
    )

    nomor = 1
    for _, desc in agg_descriptions.items():
        lines.append(f"{nomor}. {desc}\n")
        nomor += 1

    lines.append(
        "\nApabila diperlukan, laporan ini dapat dikembangkan lebih lanjut menjadi visualisasi "
        "atau analisis lanjutan untuk mendukung pengambilan keputusan operasional dan bisnis.\n"
    )
    lines.append(
        "Demikian informasi yang dapat kami sampaikan. Atas perhatian dan kerja samanya, "
        "kami ucapkan terima kasih.\n"
    )
    lines.append("\nHormat kami,\nTim Data Analytics\n")

    body = "\n".join(lines)
    return body

def send_aggregation_email_from_folder(
    output_dir: str,
    to_email: str,
):
    email_sender = os.environ.get("robert.rasidy@gmail.com")
    email_password = os.environ.get("ObetObin2006.")

    if not email_sender or not email_password:
        logger.error("EMAIL_SENDER atau EMAIL_APP_PASSWORD belum diset di environment.")
        raise RuntimeError("Kredensial email belum dikonfigurasi.")

    # 2. Buat dict csv_paths berdasarkan file yang ada di folder
    csv_paths = {}
    for agg_name, filename in EXPECTED_FILES.items():
        full_path = os.path.join(output_dir, filename)
        if os.path.exists(full_path):
            csv_paths[agg_name] = full_path
            logger.info(f"Menemukan file agregasi: {full_path}")
        else:
            logger.warning(f"File tidak ditemukan (akan dilewati): {full_path}")

    if not csv_paths:
        raise FileNotFoundError(
            f"Tidak ada file CSV agregasi yang ditemukan di folder: {output_dir}"
        )

    # 3. Bangun deskripsi agregasi (hanya untuk yang filenya ada)
    all_desc = build_agg_descriptions()
    used_desc = {k: v for k, v in all_desc.items() if k in csv_paths}

    # 4. Susun subject dan body
    today_str = datetime.today().strftime("%d %B %Y")
    subject = f"Laporan Data Agregasi Perjalanan Taksi – {today_str}"
    body = build_email_body(used_desc)

    # 5. Buat EmailMessage
    msg = EmailMessage()
    msg["From"] = email_sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # 6. Lampirkan setiap file CSV
    for agg_name, file_path in csv_paths.items():
        with open(file_path, "rb") as f:
            file_data = f.read()
            filename = os.path.basename(file_path)

        msg.add_attachment(
            file_data,
            maintype="text",
            subtype="csv",
            filename=filename,
        )
        logger.info(f"Melampirkan file CSV: {filename} ({agg_name})")

    # 7. Kirim email via SMTP Gmail
    logger.info(f"Mengirim email ke {to_email} dari {email_sender} ...")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(msg)
        logger.info("Email laporan agregasi berhasil dikirim.")
    except Exception as e:
        logger.exception(f"Gagal mengirim email: {e}")
        raise

if __name__ == "__main__":
    TARGET_EMAIL = "samsudiney@gmail.com"

    send_aggregation_email_from_folder(
        output_dir=OUTPUT_DIR,
        to_email=TARGET_EMAIL,
    )
