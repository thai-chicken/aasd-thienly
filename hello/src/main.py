import asyncio
import os
import traceback

import spade
from agents.customer_agent import CustomerAgent
from agents.department_agent import DepartmentsAgent
from agents.opinion_agent import OpinionAgent
from agents.price.agent import PriceServiceAgent
from agents.reporter_agent import Reporter
from constants import DEPARTMENT_AGENT_TYPES, OPINION_AGENT_TYPES, PRICES_AGENT_TYPES


async def main():
    reporter = Reporter(os.getenv("REPORTER_JID"), os.getenv("REPORTER_PASSWORD"))
    customer_agent = CustomerAgent(
        os.getenv("CUSTOMER_AGENT_JID"), os.getenv("CUSTOMER_AGENT_PASSWORD"), json_file_path="./data/customer/addresses.json"
    )

    opinions_handlers = []
    for opinion_type in OPINION_AGENT_TYPES:
        platform_name = opinion_type.upper()  # Extracts 'GOOGLE', 'BOOKING', etc.
        handler = OpinionAgent(
            os.getenv(f"{platform_name}_OPINIONHANDLER_JID"),
            os.getenv(f"{platform_name}_OPINIONHANDLER_PASSWORD"),
            json_file_path=f"./data/opinions/{platform_name.lower()}.json",
            opinions_type=opinion_type,
        )
        opinions_handlers.append(handler)

    price_handlers = []
    for price_agent_type in PRICES_AGENT_TYPES:
        platform_name = price_agent_type.upper()  # Extracts 'OTODOM', 'ALLEGRO', etc.
        handler = PriceServiceAgent(
            os.getenv(f"{platform_name}_PRICEHANDLER_JID"),
            os.getenv(f"{platform_name}_PRICEHANDLER_PASSWORD"),
            json_file_path=f"./data/prices/{price_agent_type.lower()}.json",
            price_service=price_agent_type,
        )
        price_handlers.append(handler)

    departments_handler = []
    for department_type in DEPARTMENT_AGENT_TYPES:
        platform_name = department_type.upper()  # Extracts 'CITY', 'DISTRICT', 'STREET'
        handler = DepartmentsAgent(
            jid=os.getenv(f"{platform_name}_DEPARTMENTHANDLER_JID"),
            password=os.getenv(f"{platform_name}_DEPARTMENTHANDLER_PASSWORD"),
            json_file_path=f"./data/departments/{platform_name.lower()}.json",
            investment_level=department_type,
        )
        departments_handler.append(handler)

    await reporter.start(auto_register=True)

    for handler in opinions_handlers:
        await handler.start(auto_register=True)

    for handler in departments_handler:
        await handler.start(auto_register=True)

    for handler in price_handlers:
        await handler.start(auto_register=True)

    await customer_agent.start(auto_register=True)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        print("[Main] Starting the agent system...")
        spade.run(main())
    except Exception as e:
        print(f"[Main] An error occurred: {e}")
        traceback.print_exc()
