import person,room

person1 = person.Worker("Agent3-om@anoxinon.me", "1234")
person1.pid="Dude1"
person1.office="office1"
future = person1.start()
future.result()


manager1 = person.Manager("Agent4-om@anoxinon.me", "1234")
manager1.team.append("Agent3-om")
manager1.pid="Manager"
manager1.office="office2"
future = manager1.start()
future.result()

custodian = person.Custodian("Agent8-om@anoxinon.me", "1234")
custodian.pid="Kole"
future = custodian.start()
future.result()

room1 = room.MeetingAgent("Agent5-om@anoxinon.me", "1234")
room1.rid="meeting"
future = room1.start()
future.result()

room2 = room.OfficeAgent("Agent6-om@anoxinon.me", "1234")
room2.rid="office1"
future = room2.start()
future.result()

room3 = room.CoridorAgent("Agent7-om@anoxinon.me", "1234")
room3.rid="coridor1"
future = room3.start()
future.result()
