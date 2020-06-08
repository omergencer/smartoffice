import time, random, asyncio, util

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import  FSMBehaviour, State


STATE_ONE = "DayStartState"
STATE_TWO = "WalkState"
STATE_THREE = "WorkState"
STATE_FOUR = "BreakState"
STATE_FIVE = "MeetingState"
STATE_SIX = "WorkState_M"
STATE_SEVEN = "WorkState_C"
STATE_EIGHT = "DayEndState"

meeting_inform_template = util.make_metadata_template(performative='inform', ontology='meeting')
n_attendance_inform_template = util.make_metadata_template(performative='inform', ontology='na')

class ExampleFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"{self.agent.pid} starting their day")

    async def on_end(self):
        print(f"{self.agent.pid} finished their day")
        await self.agent.stop()

class DayStartState(State):
    async def run(self):
        await asyncio.sleep(5)
        if random.random() > 0.2:
            move_time = random.randint(0, 15)#10 average on time
            await asyncio.sleep(move_time)
            self.agent.location = "lobby"
            self.agent.go_to = self.agent.office
            #msg = util.make_message(arrival_inform_template, to='building@localhost')
            #await self.send(msg)
            self.set_next_state(STATE_TWO)
        else:
            print(f"{self.agent.pid} not going to work")
            #msg = util.make_message(arrival_inform_template, to='building@localhost')
            #await self.send(msg)
            #self.set_next_state(STATE_THREE)

class WalkState(State):  
    def move_to(self,path,arr = False):
        print(f"{self.agent.pid} moving to {path}")
        util.Event("entry_"+path, self.agent.name)
        if arr == False:
            util.Event("exit_"+path, self.agent.name)
    
    def pathfinder(self,current,goal):
        b_layout = {"meeting":"coridor2",
                     "office1":"coridor1",
                     "office2":"coridor2",
                     "office3":"coridor2",
                     "lobby":"coridor1",
                     "supply":"coridor3",
                     "coridor1":"coridor1",
                     "coridor2":"coridor2",
                     "coridor3":"coridor3",
                     "break":"coridor1"}
        
        if b_layout[current] == b_layout[goal]:
            path = [b_layout[current], goal]
        else:
            if b_layout[current] in ["coridor1", "coridor3"] and b_layout[goal] in ["coridor1", "coridor3"]:
                if "coridor" not in goal:
                    path = [b_layout[current], "coridor2", b_layout[goal]]
                else:
                    path = [b_layout[current], "coridor2", b_layout[goal], goal]
            else:
                if "coridor" not in goal:
                    path = [b_layout[current], b_layout[goal]]
                else:
                    path = [b_layout[current], b_layout[goal], goal]
        return path
    
    async def run(self):
        print(f"{self.agent.pid} is walking to {self.agent.go_to}")
        pathway = self.pathfinder(self.agent.location,self.agent.go_to)
        util.Event("exit_"+self.agent.location, self.agent.name)
        for path in pathway:############
            if path == pathway[-1]:
                self.move_to(path, arr = True)
            else:
                self.move_to(path)
        self.agent.location = self.agent.go_to
        if  "office" in self.agent.go_to:
            if self.agent.position == "W":
                self.set_next_state(STATE_THREE)
            else:
                self.set_next_state(STATE_SIX)
        elif self.agent.go_to == "break":
            self.set_next_state(STATE_FOUR)
        elif self.agent.go_to == "lobby":
            self.set_next_state(STATE_EIGHT)
        elif self.agent.go_to == "meeting":
            self.set_next_state(STATE_FIVE)
        else:
            self.set_next_state(STATE_SEVEN)
            
class WorkState(State):
    async def run(self):
        print(f"{self.agent.pid} is working")
        diff = time.time() - self.agent.time
        break_time = 50
        leave_time = random.randint(30,50)
        if diff <= break_time:
            msg1 = await self.receive(timeout = break_time-diff)
            if msg1:
                self.agent.go_to = "meeting"
                self.set_next_state(STATE_TWO)
            else:
                self.agent.go_to = "break" #temp
                self.set_next_state(STATE_TWO)
        else:
            msg2 = await self.receive(timeout = leave_time)
            if msg2:
                self.agent.go_to = "meeting"
                self.set_next_state(STATE_TWO)
            else:
                self.agent.go_to = "lobby" #temp
                self.set_next_state(STATE_TWO)

class WorkState_M(State):#team might be an issue
    async def run(self):
        print(f"{self.agent.pid} is working")
        diff = time.time()-self.agent.time
        break_time = 50
        leave_time = random.randint(25,45)
        await asyncio.sleep(5)
        if diff <= break_time:
            if random.random() > 0.3:
                await asyncio.sleep(break_time-diff)
                self.agent.go_to = "break"
                self.set_next_state(STATE_TWO)
            else:
                for person in self.agent.team:
                    msg3 = util.make_message(meeting_inform_template, to = person+'@anoxinon.me')#temp
                    await self.send(msg3)
                self.agent.go_to = "meeting"
                self.set_next_state(STATE_TWO)
        else:
            if random.random() > 0.3:
                await asyncio.sleep(break_time-diff)
                self.agent.go_to = "lobby"
                self.set_next_state(STATE_TWO)
            else:
                for person in team:
                    msg4 = util.util.make_message(meeting_inform_template, to = person+'@localhost')#temp
                    await self.send(msg4)
                self.agent.go_to = "meeting"
                self.set_next_state(STATE_TWO)

class WorkState_C(State):
    async def run(self):
        print(f"{self.agent.pid} is working")
        room_list = ["coridor1", "coridor2", "coridor3"]
        if self.agent.work_count < 2 or self.agent.work_count == 3:
            if self.agent.location != "supply":
                room_list.remove(self.agent.location)
                self.agent.work_count += 1
                await asyncio.sleep(30)
            self.agent.go_to = random.choice(room_list)
            self.set_next_state(STATE_TWO)
        elif self.agent.work_count == 2:
            self.agent.go_to = "break"
            self.agent.work_count += 1
            self.set_next_state(STATE_TWO)
        else:
            self.agent.go_to = "lobby"
            self.set_next_state(STATE_TWO)

class BreakState(State):
    async def run(self):
        print(f"{self.agent.pid} is taking a break")
        if self.agent.pref != False and random.random() < 0.3:
            self.agent.pref = random.randrange(20,30)
            #msg = util.make_message(pref_inform_template, to='building@localhost')
            #msg.body = self.agent.pref
            #await self.send(msg)
        await asyncio.sleep(random.randint(5,15))
        self.agent.go_to = self.agent.office
        self.set_next_state(STATE_TWO)

class MeetingState(State):
    async def run(self):
        print(f"{self.agent.pid} is in a meeting")
        await asyncio.sleep(20)
        self.agent.go_to = self.agent.office
        self.set_next_state(STATE_TWO)

class DayEndState(State):
    async def run(self):
        #msg = util.make_message(exit_inform_template, to='building@localhost')
        #await self.send(msg)
        self.agent.location = "home"

class Worker(Agent):
    pid = "Dude1"
    office = "office1"
    
    async def setup(self):
        self.time = time.time()
        self.pref = 24
        self.location = "home"
        self.go_to = ""
        ###
        ###
        self.position = "W"
        
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name = STATE_ONE, state = DayStartState(), initial=True)
        fsm.add_state(name = STATE_TWO, state = WalkState())
        fsm.add_state(name = STATE_THREE, state = WorkState())
        fsm.add_state(name = STATE_FOUR, state = BreakState())
        fsm.add_state(name = STATE_FIVE, state = MeetingState())
        fsm.add_state(name = STATE_EIGHT, state = DayEndState())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        fsm.add_transition(source=STATE_TWO, dest=STATE_FOUR)
        fsm.add_transition(source=STATE_TWO, dest=STATE_FIVE)
        fsm.add_transition(source=STATE_TWO, dest=STATE_EIGHT)
        fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_FOUR, dest=STATE_TWO)
        fsm.add_transition(source=STATE_FIVE, dest=STATE_TWO)
        self.add_behaviour(fsm)

class Custodian(Agent):
    pid = ""
    office = "supply"
    
    async def setup(self):
        self.time = time.time()
        self.pref = False
        self.location = "home"
        self.go_to = ""
        self.work_count = 0
        self.position = "C"
        
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name = STATE_ONE, state = DayStartState(), initial=True)
        fsm.add_state(name = STATE_TWO, state = WalkState())
        fsm.add_state(name = STATE_SEVEN, state = WorkState_C())
        fsm.add_state(name = STATE_FOUR, state = BreakState())
        fsm.add_state(name = STATE_EIGHT, state = DayEndState())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_SEVEN)
        fsm.add_transition(source=STATE_TWO, dest=STATE_FOUR)
        fsm.add_transition(source=STATE_TWO, dest=STATE_FIVE)
        fsm.add_transition(source=STATE_TWO, dest=STATE_EIGHT)
        fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_SEVEN, dest=STATE_TWO)
        fsm.add_transition(source=STATE_FOUR, dest=STATE_TWO)
        self.add_behaviour(fsm)

class Manager(Agent):
    pid = ""
    office = ""
    team = []
        
    async def setup(self):
        self.time = time.time()
        self.location = "home"
        self.pref = 24
        self.go_to = ""
        self.position = "M"
        
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name = STATE_ONE, state = DayStartState(), initial=True)
        fsm.add_state(name = STATE_TWO, state = WalkState())
        fsm.add_state(name = STATE_SIX, state = WorkState_M())
        fsm.add_state(name = STATE_FOUR, state = BreakState())
        fsm.add_state(name = STATE_FIVE, state = MeetingState())
        fsm.add_state(name = STATE_EIGHT, state = DayEndState())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_SIX)
        fsm.add_transition(source=STATE_TWO, dest=STATE_FIVE)
        fsm.add_transition(source=STATE_TWO, dest=STATE_FOUR)
        fsm.add_transition(source=STATE_TWO, dest=STATE_EIGHT)
        fsm.add_transition(source=STATE_SIX, dest=STATE_TWO)
        fsm.add_transition(source=STATE_FOUR, dest=STATE_TWO)
        fsm.add_transition(source=STATE_FIVE, dest=STATE_TWO)
        self.add_behaviour(fsm)
