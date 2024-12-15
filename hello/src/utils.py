import traceback

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from constants import LOGO_PATH, OUTPUT_PDF_DIR
from datetime import datetime


def save_to_pdf():
    # TODO: Implement the save_to_pdf function

    pdf_file_path = OUTPUT_PDF_DIR + "/raport_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".pdf"

    try:
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        page_height = letter[1]
        margin = 50
        current_y = page_height - 100
        c.drawImage(LOGO_PATH, 50, page_height - 100, width=100, height=100)
        c.drawString(160, page_height - 50, "Twój Indywidualny Raport")

        c.drawString(margin, current_y - 50, "Opinie:")
        c.drawString(margin, current_y - 70, "Ceny:")

        c.save()
        print(f"Messages saved to {pdf_file_path}")
    except Exception as e:
        print(f"Error saving messages to PDF: {e}")
        traceback.print_exc()
