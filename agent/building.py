
import time, random, asyncio,util

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import CyclicBehaviour, State

room_pref_redirect = util.make_metadata_template(performative='inform', ontology='pref')
non_attandance_redirect = util.make_metadata_template(performative='inform', ontology='na')
arrival_inform_redirect = util.make_metadata_template(performative='inform', ontology='ok')
default_temp_template = util.make_metadata_template(performative='inform', ontology='def')

class BuildingAgent(Agent):
    async def setup(self):
        self.add_behaviour(self.WaitForData())
        self.add_behaviour(self.TempCalculate())
        self.time = time.time()

    class WaitForData(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=20)
            if msg:
                if msg.metadata["ontology"] == "pref":
                    reply = util.make_message(room_pref_redirect, to=msg.body+'@anoxinon.me')
                    await self.send(reply)
                elif msg.metadata["ontology"] == "na":
                    reply = util.make_message(non_attandance_redirect, to=msg.body+'@anoxinon.me')
                    await self.send(reply)
                elif msg.metadata["ontology"] == "ok":
                    reply = util.make_message(arrival_inform_redirect, to=msg.body+'@anoxinon.me')
                    await self.send(reply)

    class TempCalculate(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(20)
            rooms = ["Agent5-om","Agent6-om","Agent7-om"]#doldur
            if random.random() < 0.2:
                for room in rooms:
                    msg = util.make_message(default_temp_template, to=room+'@anoxinon.me')
                    msg.body = str(random.randrange(20,30))
                    await self.send(msg)



