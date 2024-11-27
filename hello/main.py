import spade
import traceback
import os

class PriceHandler(spade.agent.Agent):
    async def setup(self):
        print("PriceHandler started with JID: {}".format(str(self.jid)))
        self.add_behaviour(self.SendPricesBehaviour())

    class SendPricesBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self):
            msg = spade.message.Message(to=os.getenv("REPORTER_JID"))
            msg.body = "Prices: 100, 200, 300"
            await self.send(msg)
            print("PriceHandler sent message: {}".format(msg.body))
            self.kill()

class Reporter(spade.agent.Agent):
    async def setup(self):
        print("Reporter started with JID: {}".format(str(self.jid)))
        self.add_behaviour(self.ReceivePricesBehaviour())

    class ReceivePricesBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print("Reporter received message: {}".format(msg.body))
                self.kill()
            else:
                print("Reporter did not receive any message.")
                self.kill()

async def main():
    price_handler = PriceHandler(os.getenv("PRICEHANDLER_JID"), os.getenv("PRICEHANDLER_PASSWORD"), verify_security=False)
    reporter = Reporter(os.getenv("REPORTER_JID"), os.getenv("REPORTER_PASSWORD"), verify_security=False)

    await reporter.start(auto_register=True)
    await price_handler.start(auto_register=True)

    await price_handler.behaviours[0].join()
    await reporter.behaviours[0].join()

    await price_handler.stop()
    await reporter.stop()

if __name__ == "__main__":
    try:
        spade.run(main())
    except Exception as e:
        print("An error occurred: {}".format(str(e)))
        traceback.print_exc()
