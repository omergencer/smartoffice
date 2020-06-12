import time, random, asyncio,util

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, State

#also add template
#currently written for corridor, seperate DONE
#test seperation

class CorridorAgent(Agent, util.Observer):
    rid = ""
    
    def light_on(self, who):
        if self.occ == 0:
            print(f"{self.rid} lights on")
        self.arrival = True
        self.occ += 1
        
    def light_off(self, who):
        if self.occ == 1:
            print(f"{self.rid} lights off")
        self.occ -= 1
       

    async def setup(self):
        util.Observer.__init__(self)
        self.add_behaviour(self.CorridorBehaviour())
        self.observe('entry_corridor1',  self.light_on)
        self.observe('exit_corridor1',  self.light_off)
        self.occ = 0
        self.arrival = False
        self.assigned_to = ""
        self.temp = 24
        self.pref = [24,24]
        self.time = time.time()
        
    class OffBehaviour(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(10)
            self.agent.temp = False

    class CorridorBehaviour(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(10)
            self.agent.temp = self.agent.pref[0]
            print(f"{self.agent.rid} temp is {self.agent.temp}")

    class WaitForData(CyclicBehaviour):#pref change
        async def run(self):
            msg = await self.receive(timeout=20)
            if msg:
                if msg.metadata["topic"] == "pref":
                    self.agent.pref[0] = msg.body
                elif msg.metadata["topic"] == "def":
                    self.agent.pref[1] = msg.body
                    self.agent.add_behaviour(behaviour = RoomAgent.corridorBehaviour())
            if time.time() - self.agent.time > 100:
                self.agent.add_behaviour(behaviour = RoomAgent.OffBehaviour())

class OfficeAgent(Agent, util.Observer):
    rid = ""
    
    def light_on(self, who):
        if self.occ == 0:
            print(f"{self.rid} lights on")
        self.arrival = True
        self.occ += 1

    def light_off(self, who):
        if self.occ == 1:
            print(f"{self.rid} lights off")
        self.occ -= 1
        
    async def setup(self):
        util.Observer.__init__(self)
        self.add_behaviour(self.OfficeBehaviour())
        self.observe('entry_'+self.rid,  self.light_on)
        self.observe('exit_'+self.rid,  self.light_off)
        self.occ = 0
        self.arrival = False
        self.assigned_to = ""
        self.temp = 24
        self.pref = [24,24]
        self.time = time.time()
        
    class OffBehaviour(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(10)
            self.agent.temp = False

    class OfficeBehaviour(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                self.agent.temp = False
            else:
                self.agent.temp = self.agent.pref[1]
                print(f"Room temp: {self.agent.temp}")
                await asyncio.sleep(15)
                if self.agent.arrival == False:
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

class MeetingAgent(Agent, util.Observer):
    rid = "meeting"
    
    def light_on(self, who):
        if self.occ == 0:
            print(f"{self.rid} lights on")
        self.arrival = True
        self.occ += 1

    def light_off(self, who):
        if self.occ == 1:
            print(f"{self.rid} lights off")
        self.occ -= 1
        
    async def setup(self):
        util.Observer.__init__(self)
        self.add_behaviour(self.MeetingBehaviour())
        self.observe('entry_meeting',  self.light_on)
        self.observe('exit_meeting',  self.light_off)
        self.occ = 0
        self.arrival = False
        self.assigned_to = ""
        self.temp = 24
        self.pref = [24,24]
        self.time = time.time()
        
    class OffBehaviour(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(10)
            self.agent.temp = False
        
    class MeetingBehaviour(OneShotBehaviour):
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

