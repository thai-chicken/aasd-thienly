import json
import os
import traceback

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message


class PriceHandler(Agent):
    class SendPricesBehaviour(PeriodicBehaviour):
        async def run(self):
            try:
                msg = Message(to=os.getenv("REPORTER_JID"))
                message_data = {"type": "prices", "content": "Prices: 100, 200, 300"}
                msg.body = json.dumps(message_data)
                print(f"[{self.agent.jid}] Sending prices message for <address>..")
                await self.send(msg)
                print(f"[{self.agent.jid}] Message sent successfully.\n")
            except Exception as e:
                print(f"[{self.agent.jid}] Error sending prices: {e}")
                traceback.print_exc()

    async def setup(self):
        self.add_behaviour(self.SendPricesBehaviour(period=30))
