import json
import traceback

from constants import DEPARTMENT_AGENT_TYPES, OPINION_AGENT_TYPES, PRICES_AGENT_TYPES
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from utils import save_to_pdf, save_with_md


class Reporter(Agent):
    async def setup(self):
        print(f"[{self.jid}] Reporter starting...")

        self.reset_attributes()

        self.add_behaviour(self.ReceiveMessagesBehaviour())

    def reset_attributes(self):
        self.received_messages = {
            "opinions": {k: False for k in OPINION_AGENT_TYPES},
            "departments": {k: False for k in DEPARTMENT_AGENT_TYPES},
            "prices": {k: False for k in PRICES_AGENT_TYPES},
        }
        self.data = {
            "flat_info": None,
            "prices": {k: None for k in PRICES_AGENT_TYPES},
            "address": {
                "full": None,
                "street": None,
                "district": None,
            },
            "investment": {k: None for k in DEPARTMENT_AGENT_TYPES},
            "opinions": {k: None for k in OPINION_AGENT_TYPES},
        }

    class ReceiveMessagesBehaviour(CyclicBehaviour):
        async def run(self):
            try:
                msg = await self.receive(timeout=40)
                if msg:
                    sender = str(msg.sender)
                    body = json.loads(msg.body)

                    if body["type"] == "init":
                        self.agent.reset_attributes()
                        self.agent.data["address"]["full"] = body["address"]
                        print(f"[{self.agent.jid}] Reporter initialized")

                    # Opinions
                    elif body["type"] in OPINION_AGENT_TYPES:
                        self.agent.received_messages["opinions"][body["type"]] = True
                        self.agent.data["opinions"][body["type"]] = body["content"]
                        print(f"[{self.agent.jid}] Received {body['type']} from {sender}")
                    # Price
                    elif body["type"] in PRICES_AGENT_TYPES:
                        self.agent.received_messages["prices"][body["type"]] = True
                        self.agent.data["flat_info"] = body["flat_info"] if body.get("flat_info") else None
                        self.agent.data["prices"][body["type"]] = body["similar_flats"]
                        print(f"[{self.agent.jid}] Received prices from {sender}")
                    # Departments
                    elif body["type"] in DEPARTMENT_AGENT_TYPES:
                        self.agent.received_messages["departments"][body["type"]] = True
                        self.agent.data["address"]["street"] = body["address"] if body.get("address") else None
                        self.agent.data["address"]["district"] = body["district"] if body.get("district") else None
                        self.agent.data["address"]["city"] = body["city"] if body.get("city") else None
                        self.agent.data["investment"][body["type"]] = body["project"]
                        print(f"[{self.agent.jid}] Received {body['type']} from {sender}")
                    else:
                        print(f"[{self.agent.jid}] Received unknown message from {sender}")

                    if (
                        all(
                            self.agent.received_messages["opinions"][opinion_type]
                            for opinion_type in OPINION_AGENT_TYPES
                        )
                        and all(
                            self.agent.received_messages["departments"][department_type]
                            for department_type in DEPARTMENT_AGENT_TYPES
                        )
                        and self.agent.received_messages["prices"][PRICES_AGENT_TYPES[0]]
                    ):
                        print(f"\n[{self.agent.jid}] All messages received")
                        save_with_md(self.agent.data)
                        self.agent.reset_attributes()

                else:
                    print(f"[{self.agent.jid}] No message received in this cycle.")

            except Exception as e:
                traceback.print_exc()
