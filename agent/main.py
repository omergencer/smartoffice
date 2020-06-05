import person,room


person1 = person.Person1("Agent20-om@anoxinon.me", "1234")
future = person1.start()
future.result()

room1 = room.RoomAgent("Agent19-om@anoxinon.me", "1234")
future = room1.start()
future.result()
