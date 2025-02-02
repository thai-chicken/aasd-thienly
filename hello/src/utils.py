import hashlib
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from constants import DEJAVU_FONT_PATH, LOGO_PATH, OUTPUT_PDF_DIR
from src.agents.reporter.engine import generate_completion
from src.agents.reporter.prompts import INTRODUCTION_INVESTMENTS, INTRODUCTION_OPINIONS, INTRODUCTION_PRICE


def string_to_sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()


def prepare_flat_info(flat_info: dict) -> str:
    content = "## **Informacje o mieszkaniu**\n\n"
    for key, value in flat_info.items():
        content += f"- {key.replace('_', ' ').capitalize()}: {value}\n"
    content += "\n"
    return content


def prepare_content_prices(prices_data: dict, flat_info: dict) -> str:
    flat_info = prepare_flat_info(flat_info)

    content = "## **Ceny**\n\n"
    for source, flats in prices_data.items():
        content += f"### **{source.capitalize()}**\n\n"
        for idx, entry in enumerate(flats):
            content += f"#### Mieszkanie {idx + 1}\n"
            for key, value in entry["flat"].items():
                content += f"- {key.replace('_', ' ').capitalize()}: {value}\n"
            content += f"- Wynik dopasowania: {entry['score']}\n\n"
    return content, INTRODUCTION_PRICE.format(house_details=flat_info)


def prepare_content_investments(investments_data: dict) -> str:
    content = "## **Inwestycje**\n\n"
    titles = ["Inwestycje na wybranej ulicy", "Inwestycje w wybranej dzielnicy", "Inwestycje w wybranym mieście"]
    data_investment = [investments_data["street"], investments_data["district"], investments_data["city"]]
    for title, investment in zip(titles, data_investment):
        content += f"### {title}\n\n"
        for key, value in investment.items():
            content += f"- {key.replace('_', ' ').capitalize()}: {value}\n"
        content += "\n"
    return content, INTRODUCTION_INVESTMENTS


def prepare_content_opinions(opinions_data: dict) -> str:
    content = "## **Opinie**\n\n"
    for platform, categories in opinions_data.items():
        content += f"### {platform.capitalize()}\n\n"
        for category, details in categories.items():
            content += f"#### {category.capitalize()}\n\n"
            content += f"- Liczba opinii: {details['liczba_opinii']}\n"
            content += f"- Średnia ocena: {details['średnia_opinii']}\n"
            content += f"- Minimalna ocena: {details['min_możliwa_ocena']}\n"

            content += f"- Maksymalna ocena: {details['max_możliwa_ocena']}\n\n"
            content += "##### **Top 3 opinie**\n\n"
            for opinion in details["top_3_opinii"]:

                content += f"- **{opinion['nazwa']}** od {opinion['użytkownik']}\n"
                content += f"  - Ocena: {opinion['ocena']}\n"
                content += f"  - Opinia: {opinion['opinia']}\n"
                content += f"  - Data: {opinion['data']}\n\n"
    return content, INTRODUCTION_OPINIONS


def parse_address(full_input_address):
    """Parse the address."""
    parts = [part.strip() for part in full_input_address.split(",")]
    return parts[0], parts[1], parts[2]


def save_with_md(data, agent_jid: str):
    street_data = data["investment"]["street"]
    district_data = data["investment"]["district"]
    city_data = data["investment"]["city"]
    address_data = data["address"]
    flat_info = data["flat_info"]
    prices_data = data["prices"]
    opinions_data = data["opinions"]

    md_file_path = OUTPUT_PDF_DIR + "/raport_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".md"

    executor = ThreadPoolExecutor(max_workers=3)
    futures = {
        "prices": prepare_content_prices(prices_data, flat_info),
        "investments": prepare_content_investments(
            {"street": street_data, "district": district_data, "city": city_data}
        ),
        "opinions": prepare_content_opinions(opinions_data),
    }

    for name, (str_data, introduction_prompt) in futures.items():
        futures[name] = executor.submit(generate_completion, str_data, introduction_prompt)

    for name, future in futures.items():
        futures[name] = future.result()

    try:
        with open(md_file_path, "w", encoding="utf-8") as f:

            # Header Section
            f.write(
                f"""<div style="text-align: center">
                        <h1 style="font-size: 24px;">Indywidualny Raport</h1>
                        <img src={LOGO_PATH} style="height: 150px;">
                    </div>\n\n"""
            )

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
            f.write("\n\n")
            f.write("## **Ceny**\n\n")
            f.write(futures["prices"])

            # Investment Section
            f.write("\n\n")
            f.write("## **Inwestycje**\n\n")
            f.write(futures["investments"])

            # Opinions Section
            f.write("\n\n")
            f.write("## **Opinie**\n\n")
            f.write(futures["opinions"])

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
                    src: url({DEJAVU_FONT_PATH})
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
            with open(pdf_file_path, "wb") as pdf_file:
                pisa.CreatePDF(html_content, dest=pdf_file, encoding="UTF-8")

            print(f"[{agent_jid}] PDF report saved to {pdf_file_path}")
            return pdf_file_path
        except Exception as pdf_error:
            print(f"[{agent_jid}] Error converting markdown to PDF: {pdf_error}")
            return None

    except Exception as e:
        print(f"[{agent_jid}] Error saving report to markdown: {e}")
        traceback.print_exc()
