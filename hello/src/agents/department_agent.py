import json
import os
import random
import traceback

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message


class DepartmentsAgent(Agent):
    """
    InvestmentsAgent is an agent that retrieves investment projects data from a given JSON file.
    Depending on the investment_level ("city", "street", "district"), it will parse the given address
    and extract the required information (city, district, full street address) from it.
    It then picks a random investment project for that location and sends a message to a predefined reporter.
    """

    @staticmethod
    def parse_address(full_input_address):
        """Parse the address."""
        parts = [part.strip() for part in full_input_address.split(",")]
        return parts[2], parts[1], parts[0]

    def __init__(self, jid, password, json_file_path, investment_level, input_address, verify_security=False):
        """
        Parameters:
        - jid, password: Agent's XMPP account credentials.
        - json_file_path: path to the JSON file (city.json, street.json, or district.json).
        - investment_level: "city", "street" or "district".
        - input_address: The full address input string.
        """
        super().__init__(jid, password, verify_security=verify_security)
        self.json_file_path = json_file_path
        self.investment_level = investment_level

        # Parse the address based on investment level
        self.city, self.district, self.address = self.parse_address(input_address)

    class SendRandomDepartmentBehaviour(PeriodicBehaviour):
        def __init__(self, period, agent_ref):
            super().__init__(period)
            self.agent_ref = agent_ref

        async def run(self):
            try:
                with open(self.agent_ref.json_file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                investment = None
                # Select investment depending on the agent's investment level
                if self.agent_ref.investment_level == "city":
                    city = self.agent_ref.city
                    if city not in data:
                        print(f"[{self.agent_ref.jid}] No data available for city: {city}")
                        return
                    investment = min(data[city], key=lambda inv: inv["CzasStartu"])

                elif self.agent_ref.investment_level == "street":
                    city = self.agent_ref.city
                    address = self.agent_ref.address
                    if city not in data:
                        print(f"[{self.agent_ref.jid}] No data available for city: {city}")
                        return
                    if address not in data[city]:
                        print(f"[{self.agent_ref.jid}] No data available for address: {address} in city {city}")
                        return
                    investment = min(data[city][address], key=lambda inv: inv["CzasStartu"])

                elif self.agent_ref.investment_level == "district":
                    city = self.agent_ref.city
                    district = self.agent_ref.district
                    if city not in data:
                        print(f"[{self.agent_ref.jid}] No data available for city: {city}")
                        return
                    if district not in data[city]:
                        print(f"[{self.agent_ref.jid}] No data available for district: {district} in city {city}")
                        return
                    investment = min(data[city][district], key=lambda inv: inv["CzasStartu"])

                if not investment:
                    print(f"[{self.agent_ref.jid}] No investments to send.")
                    return

                print(f"\n[{self.agent_ref.jid}] Preparing to send investment information:")

                message_data = {
                    "type": self.agent_ref.investment_level,
                    "city": self.agent_ref.city if self.agent_ref.city else None,
                    "address": self.agent_ref.address if self.agent_ref.address else None,
                    "district": self.agent_ref.district if self.agent_ref.district else None,
                    "project": investment,
                }
                message_data = {k: v for k, v in message_data.items() if v is not None}

                msg = Message(to=os.getenv("REPORTER_JID"))
                msg.body = json.dumps(message_data, ensure_ascii=False)
                print(f"[{self.agent_ref.jid}] Sending message...")
                await self.send(msg)
                print(f"[{self.agent_ref.jid}] Message sent successfully.\n")

            except Exception as e:
                print(f"[{self.agent_ref.jid}] Error while sending information: {e}")
                traceback.print_exc()

    async def setup(self):
        self.add_behaviour(self.SendRandomDepartmentBehaviour(period=30, agent_ref=self))
