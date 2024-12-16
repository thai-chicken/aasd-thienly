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


def save_with_md(data):
    street_data = data["investment"]["street"]
    district_data = data["investment"]["district"]
    city_data = data["investment"]["city"]
    address_data = data["address"]
    flat_info = data["flat_info"]
    prices_data = data["prices"]
    opinions_data = data["opinions"]

    md_file_path = OUTPUT_PDF_DIR + "/raport_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".md"

    try:
        with open(md_file_path, "w", encoding="utf-8") as f:
            f.write("# Indywidualny Raport\n\n")

            # Logo Section
            f.write("![Logo](./data/logo/thienly_logo.png)\n\n")

            # Address Section
            address = address_data["full"]
            f.write(f"## Adres\n\n")
            f.write(f"- Pełny adres: {address}\n\n")

            # Flat Information Section
            f.write("## Informacje o mieszkaniu\n\n")
            for key, value in flat_info.items():
                f.write(f"- {key.replace('_', ' ').capitalize()}: {value}\n")

            f.write("\n")

            # Prices Section
            f.write("## Ceny\n\n")
            for source, flats in prices_data.items():
                f.write(f"### {source.capitalize()}\n\n")
                for entry in flats:
                    f.write("#### Mieszkanie\n")
                    for key, value in entry["flat"].items():
                        f.write(f"- {key.replace('_', ' ').capitalize()}: {value}\n")
                    f.write(f"- Wynik dopasowania: {entry['score']}\n\n")

            # Investment Section
            f.write("## Inwestycje\n\n")
            for scope, investment in data["investment"].items():
                f.write(f"### {scope.capitalize()}\n\n")
                for key, value in investment.items():
                    f.write(f"- {key.replace('_', ' ').capitalize()}: {value}\n")
                f.write("\n")

            # Opinions Section
            f.write("## Opinie\n\n")
            for platform, categories in opinions_data.items():
                f.write(f"### {platform.capitalize()}\n\n")
                for category, details in categories.items():
                    f.write(f"#### {category.capitalize()}\n\n")
                    f.write(f"- Liczba opinii: {details['liczba_opinii']}\n")
                    f.write(f"- Średnia ocena: {details['średnia_opinii']}\n")
                    f.write(f"- Minimalna ocena: {details['min_możliwa_ocena']}\n")
                    f.write(f"- Maksymalna ocena: {details['max_możliwa_ocena']}\n\n")
                    f.write("##### Top 3 opinie\n\n")
                    for opinion in details["top_3_opinii"]:
                        f.write(f"- **{opinion['nazwa']}** od {opinion['użytkownik']}\n")
                        f.write(f"  - Ocena: {opinion['ocena']}\n")
                        f.write(f"  - Opinia: {opinion['opinia']}\n")
                        f.write(f"  - Data: {opinion['data']}\n\n")

        # Convert Markdown to PDF
        pdf_file_path = md_file_path.replace(".md", ".pdf")
        try:
            from markdown2 import markdown
            from xhtml2pdf import pisa

            with open(md_file_path, "r", encoding="utf-8") as md_file:
                md_content = md_file.read()

            html_content = markdown(md_content)
            with open(pdf_file_path, "w+b") as pdf_file:
                pisa.CreatePDF(html_content, dest=pdf_file)

            print(f"PDF report saved to {pdf_file_path}")
        except Exception as pdf_error:
            print(f"Error converting markdown to PDF: {pdf_error}")

    except Exception as e:
        print(f"Error saving report to markdown: {e}")
        traceback.print_exc()
