def pathfind(self.agent.location,self.agent.go_to):
        if "corridor" in self.agent.location:
            if self.agent.go_to in layout[self.agent.location]:
                path = [self.agent.go_to]
            else:
                path = ["corridor2", self.agent.go_to]
        else:
            if "corridor" in self.agent.go_to:
                if self.agent.go_to in layout[self.agent.location]:
                    path = [layout[self.agent.location]]
                elif self.agent.go_to == "corridor2":
                    path = [layout[self.agent.location],"corridor2"]
                else:
                    path = [layout[self.agent.location],"corridor2","corridor1"]
            else:
                if layout[self.agent.go_to] in layout[layout[self.agent.location]]:
                    path = [layout[self.agent.location],layout[self.agent.go_to],self.agent.go_to]
                else:
                    path = [layout[self.agent.location],"corridor2",layout[self.agent.go_to],self.agent.go_to]
        return path

print(pathfind("lobby","office3"))
print(pathfind("supply","corridor2"))
