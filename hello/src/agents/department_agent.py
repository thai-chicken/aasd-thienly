import json
import os
import traceback

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from src.utils import parse_address


class DepartmentsAgent(Agent):
    """
    InvestmentsAgent is an agent that retrieves investment projects data from a given JSON file.
    Depending on the investment_level ("city", "street", "district"), it will parse the given address
    and extract the required information (city, district, full street address) from it.
    It then picks a random investment project for that location and sends a message to a predefined reporter.
    """

    def __init__(self, jid, password, json_file_path, investment_level, verify_security=False):
        """
        Parameters:
        - jid, password: Agent's XMPP account credentials.
        - json_file_path: path to the JSON file (city.json, street.json, or district.json).
        - investment_level: "city", "street" or "district".
        """
        super().__init__(jid, password, verify_security=verify_security)
        self.json_file_path = json_file_path
        self.investment_level = investment_level

    class ServiceDepartmentBehaviour(CyclicBehaviour):
        async def process_message(self, input_address: str, object_id: str):
            address, district, city = parse_address(input_address)
            with open(self.agent.json_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            investment = None

            # Select investment depending on the agent's investment level
            if self.agent.investment_level == "city":
                if city not in data:
                    print(f"[{self.agent.jid}] No data available for city: {city}")
                    return
                investment = min(data[city], key=lambda inv: inv["CzasStartu"])

            elif self.agent.investment_level == "street":
                if city not in data:
                    print(f"[{self.agent.jid}] No data available for city: {city}")
                    return
                if address not in data[city]:
                    print(f"[{self.agent.jid}] No data available for address: {address} in city {city}")
                    return
                investment = min(data[city][address], key=lambda inv: inv["CzasStartu"])

            elif self.agent.investment_level == "district":
                if city not in data:
                    print(f"[{self.agent.jid}] No data available for city: {city}")
                    return
                if district not in data[city]:
                    print(f"[{self.agent.jid}] No data available for district: {district} in city {city}")
                    return
                investment = min(data[city][district], key=lambda inv: inv["CzasStartu"])

            if not investment:
                print(f"[{self.agent.jid}] No investments to send.")
                return

            try:
                print(f"\n[{self.agent.jid}] Preparing to send investment information:")

                message_data = {
                    "type": self.agent.investment_level,
                    "object_id": object_id,
                    "city": city if city else None,
                    "address": address if address else None,
                    "district": district if district else None,
                    "project": investment,
                }
                message_data = {k: v for k, v in message_data.items() if v is not None}

                msg = Message(to=os.getenv("REPORTER_JID"))
                msg.body = json.dumps(message_data, ensure_ascii=False)
                print(f"[{self.agent.jid}] Sending message...")
                await self.send(msg)
                print(f"[{self.agent.jid}] Message sent successfully.\n")
            except Exception as e:
                print(f"[{self.agent.jid}] Error while sending information: {e}")
                traceback.print_exc()

        async def run(self):
            try:
                msg = await self.receive(timeout=40)
                if msg:
                    body = json.loads(msg.body)

                    if body["type"] == "init":
                        address = body["address"]
                        print(f"[{self.agent.jid}] Received init message for address: {address}")
                        await self.process_message(address, object_id=body["object_id"])
                    else:
                        print(f"[{self.agent.jid}] Received unknown message: {body['type']}")
                else:
                    print(f"[{self.agent.jid}] No message received in this cycle.")
            except Exception as e:
                print(f"[{self.agent.jid}] Error when receiving init message: {e}")
                traceback.print_exc()

    async def setup(self):
        self.add_behaviour(self.ServiceDepartmentBehaviour())
