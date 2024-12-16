import traceback
from datetime import datetime

from constants import LOGO_PATH, OUTPUT_PDF_DIR
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def save_to_pdf(street_data, district_data, city_data, address_data):
    pdf_file_path = OUTPUT_PDF_DIR + "/raport_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".pdf"

    try:
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        page_height = letter[1]
        margin = 50

        # Draw the logo at the top-left corner
        c.drawImage(LOGO_PATH, margin, page_height - 100, width=100, height=100)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin + 110, page_height - 50, "Your Individual Report")

        # Set the starting point for text below the header
        current_y = page_height - 150
        line_height = 20

        # Extract and print the address once at the top
        # Assuming all data dicts have the same 'address' key
        address = address_data["full"]
        if address:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, current_y, f"Address: {address}")
            current_y -= line_height * 2

        # Keys to exclude from the data sections
        exclude_keys = {"type", "city", "address", "district", "street"}

        # Helper function to print dictionary data into the PDF without excluded keys
        def print_filtered_dict_data(c, data_dict, start_y, title):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, start_y, title + ":")
            c.setFont("Helvetica", 10)
            start_y -= line_height

            for key, value in data_dict.items():
                if key in exclude_keys:
                    continue
                if isinstance(value, dict):
                    # If value is a nested dictionary (e.g., 'project')
                    c.drawString(margin, start_y, f"{key}:")
                    start_y -= line_height
                    for subkey, subvalue in value.items():
                        c.drawString(margin + 20, start_y, f"{subkey}: {subvalue}")
                        start_y -= line_height
                else:
                    c.drawString(margin, start_y, f"{key}: {value}")
                    start_y -= line_height

            return start_y - line_height

        # Print "street" data
        print(street_data)
        current_y = print_filtered_dict_data(c, street_data, current_y, "Street Data")

        # Print "district" data
        current_y = print_filtered_dict_data(c, district_data, current_y, "District Data")

        # Print "city" data
        current_y = print_filtered_dict_data(c, city_data, current_y, "City Data")

        c.save()
        print(f"Report saved to {pdf_file_path}")
    except Exception as e:
        print(f"Error saving report to PDF: {e}")
        traceback.print_exc()


def parse_address(full_input_address):
    """Parse the address."""
    parts = [part.strip() for part in full_input_address.split(",")]
    return parts[0], parts[1], parts[2]
