import json
import os
import random
import traceback

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from src.agents.price.utils import get_flat_features, get_similar_flats, load_accessible_flats
from src.utils import parse_address


class PriceServiceAgent(Agent):
    """PriceServiceAgent is an agent that retrieves features of a flat and, in its datebase, finds similar flats.
    It depends on the price service (OTODOM, ALLEGRO, OLX), each having its own database.
    Found similar flats are sent to the reporter.
    """

    def __init__(self, jid, password, json_file_path, price_service, verify_security=False):
        """ """
        super().__init__(jid, password, verify_security=verify_security)


        self.json_file_path = json_file_path
        self.price_service = price_service

        self.service_flats = load_accessible_flats(self.json_file_path)

    class ServicePricesBehaviour(CyclicBehaviour):
        async def process_message(self, input_address: str):
            address, district, city = parse_address(input_address)
            address = address + ", " + district
            target_flat = get_flat_features(city, address)
            similar_flats = get_similar_flats(self.agent.service_flats, target_flat)

            message_data = {
                "type": self.agent.price_service,
                "address": address if address else None,
                "flat_info": target_flat.to_dict(),
                "similar_flats": [
                    {"flat": flat_score_info["flat"].to_dict(), "score": flat_score_info["score"]}
                    for flat_score_info in similar_flats
                ],
            }

            try:
                print(f"\n[{self.agent.jid}] Preparing to send price information:")
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
        self.add_behaviour(self.ServicePricesBehaviour())
