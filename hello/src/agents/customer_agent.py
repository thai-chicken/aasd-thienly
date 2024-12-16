import json
import os
import random
import traceback

from constants import DEPARTMENT_AGENT_TYPES, OPINION_AGENT_TYPES, PRICES_AGENT_TYPES
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message

ALL_INIT_RECIPIENTS = [
    os.getenv(f"{agent.upper()}_JID")
    for agent in (
        [f"{service}_OPINIONHANDLER" for service in OPINION_AGENT_TYPES]
        + [f"{service}_PRICEHANDLER" for service in PRICES_AGENT_TYPES]
        + [f"{service}_DEPARTMENTHANDLER" for service in DEPARTMENT_AGENT_TYPES]
    )
]


class CustomerAgent(Agent):
    def __init__(self, jid, password, json_file_path, verify_security=False):
        super().__init__(jid, password, verify_security=verify_security)
        self.json_file_path = json_file_path

    class SendAddressBehaviour(PeriodicBehaviour):
        def __init__(self, period, json_file_path):
            super().__init__(period)
            self.json_file_path = json_file_path

        async def run(self):
            try:
                with open(self.json_file_path, "r") as file:
                    addresses = json.load(file)["addresses"]

                address = random.choice(addresses)
                print(f"\n[{self.agent.jid}] Preparing to send information:")

                message_data = {
                    "type": "init",
                    "address": address,
                }
                print(f"[{self.agent.jid}] Sending init messages to reporter...")
                msg = Message(to=os.getenv("REPORTER_JID"))
                msg.body = json.dumps(message_data)
                await self.send(msg)

                print(f"[{self.agent.jid}] Sending init messages to agents...")
                for recipient in ALL_INIT_RECIPIENTS:
                    msg = Message(to=recipient)
                    msg.body = json.dumps(message_data)
                    await self.send(msg)
                print(f"[{self.agent.jid}] Messages sent successfully.\n")

            except Exception as e:
                print(f"[{self.agent.jid}] Error while sending information: {e}")
                traceback.print_exc()

    async def setup(self):
        self.add_behaviour(self.SendAddressBehaviour(period=30, json_file_path=self.json_file_path))
