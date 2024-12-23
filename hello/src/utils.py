import traceback
from datetime import datetime

from constants import LOGO_PATH, OUTPUT_PDF_DIR
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


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
            f.write('''<div style="text-align: center">
                        <h1 style="font-size: 24px;">Indywidualny Raport</h1>
                        <img src="./data/logo/thienly_logo.png" style="height: 150px;">
                    </div>\n\n''')
            # Address Section
            address = address_data["full"]
            f.write(f"## **Adres**: {address}\n\n")

            # Flat Information Section
            f.write("- - -\n\n")
            f.write("## **Informacje o mieszkaniu**\n\n")
            for key, value in flat_info.items():
                f.write(f"- {key.replace('_', ' ').capitalize()}: {value}\n")
            f.write("\n")

            # Prices Section
            f.write("---\n\n")
            f.write("## **Ceny**\n\n")
            for source, flats in prices_data.items():
                f.write(f"### **{source.capitalize()}**\n\n")
                for idx, entry in enumerate(flats):
                    f.write(f"#### Mieszkanie {idx + 1}\n")
                    for key, value in entry["flat"].items():
                        f.write(f"- {key.replace('_', ' ').capitalize()}: {value}\n")
                    f.write(f"- Wynik dopasowania: {entry['score']}\n\n")

            # Investment Section
            f.write("---\n\n")
            f.write("## **Inwestycje**\n\n")
            titles = [
                "Inwestycje na wybranej ulicy",
                "Inwestycje w wybranej dzielnicy",
                "Inwestycje w wybranym mieście"
            ]
            data_investment = [street_data, district_data, city_data]
            for title, investment in zip(titles, data_investment):
                f.write(f"### {title}\n\n")
                for key, value in investment.items():
                    f.write(f"- {key.replace('_', ' ').capitalize()}: {value}\n")
                f.write("\n")

            # Opinions Section
            f.write("---\n\n")
            f.write("## **Opinie**\n\n")
            for platform, categories in opinions_data.items():
                f.write(f"### {platform.capitalize()}\n\n")
                for category, details in categories.items():
                    f.write(f"#### {category.capitalize()}\n\n")
                    f.write(f"- Liczba opinii: {details['liczba_opinii']}\n")
                    f.write(f"- Średnia ocena: {details['średnia_opinii']}\n")
                    f.write(f"- Minimalna ocena: {details['min_możliwa_ocena']}\n")
                    f.write(f"- Maksymalna ocena: {details['max_możliwa_ocena']}\n\n")
                    f.write("##### **Top 3 opinie**\n\n")
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

            html_content = f"""
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                <meta charset="UTF-8">
                <style>
                @font-face {{
                    font-family: "DejaVuSans";
                    src: url("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
                }}
                * {{
                    font-family: DejaVuSans;
                }}
                </style>
            </head>
            <body>
                {markdown(md_content)}
            </body>
            </html>
            """
            print(html_content)
            with open(pdf_file_path, "wb") as pdf_file:
                pisa.CreatePDF(html_content, dest=pdf_file, encoding="UTF-8")

            print(f"PDF report saved to {pdf_file_path}")
        except Exception as pdf_error:
            print(f"Error converting markdown to PDF: {pdf_error}")

    except Exception as e:
        print(f"Error saving report to markdown: {e}")
        traceback.print_exc()
