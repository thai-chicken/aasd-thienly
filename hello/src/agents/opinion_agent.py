import json
import os
import random
import traceback

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message


class OpinionHandler(Agent):
    @staticmethod
    def parse_address(full_input_address):
        """ Parse the address. """
        parts = [part.strip() for part in full_input_address.split(",")]
        return parts[2], parts[1], parts[0]
    
    def __init__(self, jid, password, json_file_path, opinions_type, input_address, verify_security=False):
        super().__init__(jid, password, verify_security=verify_security)
        self.json_file_path = json_file_path
        self.opinions_type = opinions_type
        print(input_address)
        self.city, self.district, self.address = self.parse_address(input_address)

    class SendRandomOpinionBehaviour(PeriodicBehaviour):
        def __init__(self, period, json_file_path, opinions_type, agent_ref):
            super().__init__(period)
            self.json_file_path = json_file_path
            self.opinions_type = opinions_type
            self.agent_ref = agent_ref

        async def run(self):
            try:
                with open(self.json_file_path, "r") as file:
                    data = json.load(file)
                address = ", ".join([self.agent_ref.address, self.agent_ref.district])
                details = data[self.agent_ref.city][address]

                print(f"\n[{self.agent.jid}] Preparing to send information:")

                message_data = {
                    "type": self.opinions_type,
                    "city": self.agent_ref.city,
                    "address": address,
                    "content": details,
                }
                msg = Message(to=os.getenv("REPORTER_JID"))
                msg.body = json.dumps(message_data)
                print(f"[{self.agent.jid}] Sending message...")
                await self.send(msg)
                print(f"[{self.agent.jid}] Message sent successfully.\n")

            except Exception as e:
                print(f"[{self.agent.jid}] Error while sending information: {e}")
                traceback.print_exc()

    async def setup(self):
        self.add_behaviour(
            self.SendRandomOpinionBehaviour(
                period=30,
                json_file_path=self.json_file_path,
                opinions_type=self.opinions_type,
                agent_ref=self
            )
        )
