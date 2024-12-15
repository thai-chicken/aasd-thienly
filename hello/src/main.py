import asyncio
import os
import traceback

import spade

from agents.opinion_agent import OpinionHandler
from agents.price_agent import PriceHandler
from agents.reporter_agent import Reporter
from agents.department_agent import DepartmentsAgent
from constants import OPINION_AGENT_TYPES, DEPARTMENT_AGENT_TYPES

# Address format is important!
INPUT_ADDRESS = "ul. Floriańska 3, Dzielnica Stare Miasto, Kraków"

async def main():
    reporter = Reporter(os.getenv("REPORTER_JID"), os.getenv("REPORTER_PASSWORD"))

    opinions_handlers = []
    for opinion_type in OPINION_AGENT_TYPES:
        platform_name = opinion_type.split('_')[0].upper()  # Extracts 'GOOGLE', 'BOOKING', etc.
        handler = OpinionHandler(
            os.getenv(f"{platform_name}_OPINIONHANDLER_JID"),
            os.getenv(f"{platform_name}_OPINIONHANDLER_PASSWORD"),
            json_file_path=f"./data/opinions/{platform_name.lower()}.json",
            opinions_type=opinion_type,
            input_address=INPUT_ADDRESS
        )
        opinions_handlers.append(handler)

    price_handler = PriceHandler(os.getenv("PRICEHANDLER_JID"), os.getenv("PRICEHANDLER_PASSWORD"))

    departments_handler = []
    for department_type in DEPARTMENT_AGENT_TYPES:
        platform_name = department_type.upper()  # Extracts 'CITY', 'DISTRICT', 'STREET'
        handler = DepartmentsAgent(
            jid=os.getenv(f"{platform_name}_DEPARTMENTHANDLER_JID"),
            password=os.getenv(f"{platform_name}_DEPARTMENTHANDLER_PASSWORD"),
            json_file_path=f"./data/departments/{platform_name.lower()}.json",
            investment_level=department_type,
            input_address=INPUT_ADDRESS
        )
        departments_handler.append(handler)

    await reporter.start(auto_register=True)

    for handler in opinions_handlers:
        await handler.start(auto_register=True)

    for handler in departments_handler:
        await handler.start(auto_register=True)

    await price_handler.start(auto_register=True)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        print("[Main] Starting the agent system...")
        spade.run(main())
    except Exception as e:
        print(f"[Main] An error occurred: {e}")
        traceback.print_exc()
