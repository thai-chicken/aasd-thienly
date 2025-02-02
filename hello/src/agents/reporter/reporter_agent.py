import json
import os
import traceback

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from constants import DEPARTMENT_AGENT_TYPES, OPINION_AGENT_TYPES, PRICES_AGENT_TYPES
from utils import save_with_md


class Reporter(Agent):
    async def setup(self):
        print(f"[{self.jid}] Reporter starting...")

        self.reset_all_attributes()
        self.add_behaviour(self.ReceiveMessagesBehaviour())

    def reset_all_attributes(self):
        self.received_messages = {}
        self.data = {}

    def reset_attributes_per_object(self, object_id: str):
        self.received_messages[object_id] = {
            "opinions": {k: False for k in OPINION_AGENT_TYPES},
            "departments": {k: False for k in DEPARTMENT_AGENT_TYPES},
            "prices": {k: False for k in PRICES_AGENT_TYPES},
        }
        self.data[object_id] = {
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

    def check_attributes_object(self, object_id: str):
        return object_id in self.received_messages and object_id in self.data

    def check_all_attributes_collected(self, object_id: str):
        return (
            self.check_attributes_object(object_id=object_id)
            and all(
                self.received_messages[object_id]["opinions"][opinion_type] for opinion_type in OPINION_AGENT_TYPES
            )
            and all(
                self.received_messages[object_id]["departments"][department_type]
                for department_type in DEPARTMENT_AGENT_TYPES
            )
            and self.received_messages[object_id]["prices"][PRICES_AGENT_TYPES[0]]
        )

    class ReceiveMessagesBehaviour(CyclicBehaviour):
        async def run(self):
            try:
                msg = await self.receive(timeout=40)
                if msg:
                    sender = str(msg.sender)
                    body = json.loads(msg.body)

                    object_id = body["object_id"]

                    if body["type"] == "init":
                        self.agent.reset_attributes_per_object(object_id)
                        self.agent.data[object_id]["address"]["full"] = body["address"]
                        print(f"[{self.agent.jid}] Reporter for {object_id} initialized")

                    # Opinions
                    elif body["type"] in OPINION_AGENT_TYPES:
                        assert self.agent.check_attributes_object(object_id)
                        self.agent.received_messages[object_id]["opinions"][body["type"]] = True
                        self.agent.data[object_id]["opinions"][body["type"]] = body["content"]
                        print(f"[{self.agent.jid}] Received {body['type']} from {sender}")

                    # Price
                    elif body["type"] in PRICES_AGENT_TYPES:
                        assert self.agent.check_attributes_object(object_id)
                        self.agent.received_messages[object_id]["prices"][body["type"]] = True
                        self.agent.data[object_id]["flat_info"] = body["flat_info"] if body.get("flat_info") else None

                        self.agent.data[object_id]["prices"][body["type"]] = body["similar_flats"]
                        print(f"[{self.agent.jid}] Received prices from {sender}")

                    # Departments
                    elif body["type"] in DEPARTMENT_AGENT_TYPES:
                        assert self.agent.check_attributes_object(object_id)
                        self.agent.received_messages[object_id]["departments"][body["type"]] = True
                        self.agent.data[object_id]["address"]["street"] = (
                            body["address"] if body.get("address") else None
                        )

                        self.agent.data[object_id]["address"]["district"] = (
                            body["district"] if body.get("district") else None
                        )
                        self.agent.data[object_id]["address"]["city"] = body["city"] if body.get("city") else None
                        self.agent.data[object_id]["investment"][body["type"]] = body["project"]
                        print(f"[{self.agent.jid}] Received {body['type']} from {sender}")

                    else:
                        print(f"[{self.agent.jid}] Received unknown message for {object_id} from {sender}")

                    if self.agent.check_all_attributes_collected(object_id):
                        print(f"\n[{self.agent.jid}] All messages received")
                        pdf_file_path = save_with_md(self.agent.data[object_id], agent_jid=self.agent.jid)
                        msg = Message(to=os.getenv("CUSTOMER_AGENT_JID"))
                        msg.body = json.dumps({"type": "report", "object_id": object_id, "report_url": pdf_file_path})

                        await self.send(msg)
                        self.agent.reset_attributes_per_object(object_id)

                else:
                    print(f"[{self.agent.jid}] No message received in this cycle.")

            except Exception as e:
                traceback.print_exc()
