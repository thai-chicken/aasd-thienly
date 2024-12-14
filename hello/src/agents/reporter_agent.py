import json
import traceback

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from utils import save_to_pdf
from constants import OPINION_AGENT_TYPES


class Reporter(Agent):
    async def setup(self):
        print(f"[{self.jid}] Reporter starting...")
        self.opinion_types = OPINION_AGENT_TYPES
        self.current_price = None

        for opinion_type in self.opinion_types:
            setattr(self, opinion_type, None)

        self.add_behaviour(self.ReceiveMessagesBehaviour())

    class ReceiveMessagesBehaviour(CyclicBehaviour):
        async def run(self):
            try:
                msg = await self.receive(timeout=40)
                if msg:
                    sender = str(msg.sender)
                    body = json.loads(msg.body)

                    if body["type"] in self.agent.opinion_types:
                        setattr(self.agent, body["type"], body)
                        print(f"[{self.agent.jid}] Received {body['type']} from {sender}")
                    elif body["type"] == "prices":
                        self.agent.current_price = body
                        print(f"[{self.agent.jid}] Received prices from {sender}")
                    else:
                        print(f"[{self.agent.jid}] Received unknown message from {sender}")

                    if (
                        all(getattr(self.agent, opinion_type, None) for opinion_type in self.agent.opinion_types)
                        and self.agent.current_price
                    ):
                        print(f"\n[{self.agent.jid}] All messages received")

                        save_to_pdf()

                        for opinion_type in self.agent.opinion_types:
                            setattr(self.agent, opinion_type, None)
                        self.agent.current_price = None
                else:
                    print(f"[{self.agent.jid}] No message received in this cycle.")

            except Exception as e:
                traceback.print_exc()
