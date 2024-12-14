import json
import os
import random
import traceback

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message


class OpinionHandler(Agent):
    def __init__(self, jid, password, json_file_path, opinions_type, verify_security=False):
        super().__init__(jid, password, verify_security=verify_security)
        self.json_file_path = json_file_path
        self.opinions_type = opinions_type

    class SendRandomOpinionBehaviour(PeriodicBehaviour):
        def __init__(self, period, json_file_path, opinions_type):
            super().__init__(period)
            self.json_file_path = json_file_path
            self.opinions_type = opinions_type

        async def run(self):
            try:
                with open(self.json_file_path, "r") as file:
                    data = json.load(file)

                city = random.choice(list(data.keys()))
                address, details = random.choice(list(data[city].items()))

                print(f"\n[{self.agent.jid}] Preparing to send information:")

                message_data = {
                    "type": self.opinions_type,
                    "city": city,
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
            )
        )
