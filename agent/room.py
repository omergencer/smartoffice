import time, random, asyncio,util

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, State



class RoomAgent(Agent, util.Observer):
    def light_on(self, who):#async?
        print(f"{self.id} lights on")
        self.arrival = True

    def light_off(self, who):
        print(f"{self.id} lights off")
        
    async def setup(self):
        util.Observer.__init__(self)
        self.id = "coridor1"
        self.arrival = False
        self.assigned_to = ""
        self.temp = 0
        self.pref = [24,24]
        self.time = time.time()
        self.observe('entry_coridor1',  self.light_on)
        self.observe('exit_coridor1',  self.light_off)
        #assign default
        
    class OffBehaviour(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(10)
            self.agent.temp = False

    class CoridorBehaviour(OneShotBehaviour):#10 is the work start. Maybe make this a heating behaviout that takes time
        async def run(self):
            await asyncio.sleep(10)
            self.agent.temp = self.agent.pref[0]

    class OfficeBehaviour(OneShotBehaviour):#10 is the work start. Maybe make this a heating behaviout that takes time
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                self.agent.temp = False
            else:
                self.agent.temp = self.agent.pref[1]
                await asyncio.sleep(15)
                if self.agent.arrival == False:
                    self.agent.temp = False
            
    class MeetingBehaviour(OneShotBehaviour):#10 is the work start. Maybe make this a heating behaviout that takes time
        async def run(self):
            await asyncio.sleep(10)
            self.agent.temp = self.agent.pref[0]
            msg = await self.receive(timeout=90)
            if msg:
                self.agent.temp = 24
                await asyncio.sleep(20)
                self.agent.temp = False
            self.agent.temp = False

    class WaitForData(CyclicBehaviour):#pref change
        async def run(self):
            msg = await self.receive(timeout=20)
            if msg:
                if msg.metadata["topic"] == "pref":
                    self.agent.pref[0] = msg.body
                elif msg.metadata["topic"] == "def":
                    self.agent.pref[1] = msg.body
            if time.time() - self.agent.time > 100:
                self.agent.add_behaviour(behaviour = RoomAgent.OffBehaviour())



