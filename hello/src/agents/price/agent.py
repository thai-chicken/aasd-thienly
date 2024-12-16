import json
import os
import random
import traceback

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from src.agents.price.utils import get_flat_features, get_similar_flats, load_accessible_flats


class PriceServiceAgent(Agent):
    """PriceServiceAgent is an agent that retrieves features of a flat and, in its datebase, finds similar flats.
    It depends on the price service (OTODOM, ALLEGRO, OLX), each having its own database.
    Found similar flats are sent to the reporter.
    """

    @staticmethod
    def parse_address(full_input_address):
        parts = [part.strip() for part in full_input_address.split(",")]
        return parts[2], parts[1], parts[0]

    def __init__(self, jid, password, json_file_path, price_service, input_address, verify_security=False):
        """ """
        super().__init__(jid, password, verify_security=verify_security)
        self.json_file_path = json_file_path
        self.price_service = price_service

        self.service_flats = load_accessible_flats(self.json_file_path)

        # Parse the address based on investment level
        self.city, self.district, self.address = self.parse_address(input_address)

    class SendServicePricesBehaviour(PeriodicBehaviour):
        def __init__(self, period, agent_ref):
            super().__init__(period)
            self.agent_ref = agent_ref

        async def run(self):
            try:
                target_flat = get_flat_features(self.city, self.address)
                similar_flats = get_similar_flats(self.service_flats, target_flat)

                message_data = {
                    "type": "price",
                    "service": self.agent_ref.price_service,
                    "address": self.agent_ref.address if self.agent_ref.address else None,
                    "flat_info": target_flat.to_dict(),
                    "similar_flats": [{"flat": flat.to_dict(), "score": score} for flat, score in similar_flats],
                }

                msg = Message(to=os.getenv("REPORTER_JID"))
                msg.body = json.dumps(message_data, ensure_ascii=False)
                print(f"[{self.agent_ref.jid}] Sending message...")
                await self.send(msg)
                print(f"[{self.agent_ref.jid}] Message sent successfully.\n")

            except Exception as e:
                print(f"[{self.agent_ref.jid}] Error while sending information: {e}")
                traceback.print_exc()

    async def setup(self):
        self.add_behaviour(self.SendServicePricesBehaviour(period=30, agent_ref=self))
