import json
import os
import random
import traceback

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from src.utils import parse_address


class OpinionAgent(Agent):
    def __init__(self, jid, password, json_file_path, opinions_type, verify_security=False):
        super().__init__(jid, password, verify_security=verify_security)
        self.json_file_path = json_file_path
        self.opinions_type = opinions_type

    class HandleOpinionBehaviour(CyclicBehaviour):
        async def process_message(self, input_address: str):
            address, district, city = parse_address(input_address)
            with open(self.agent.json_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # TODO(KZ): improve this logic
            address, details = random.choice(list(data[city].items()))

            try:
                print(f"\n[{self.agent.jid}] Preparing to send opinion information:")

                message_data = {
                    "type": self.agent.opinions_type,
                    "city": city,
                    "address": address,
                    "content": details,
                }

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
                        await self.process_message(address)
                    else:
                        print(f"[{self.agent.jid}] Received unknown message: {body['type']}")
                else:
                    print(f"[{self.agent.jid}] No message received in this cycle.")
            except Exception as e:
                print(f"[{self.agent.jid}] Error when receiving init message: {e}")
                traceback.print_exc()

    async def setup(self):
        self.add_behaviour(self.HandleOpinionBehaviour())
