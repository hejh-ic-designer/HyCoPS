

class ControllerDefinedException(Exception):
    """ Facilitates error handling in case incorrect Controller type """
    
class Controller:
    ''' connection between CoreGroups: Bus, 2D-mesh, ... '''
    def __init__(self, ctrl_type: str):
        self.ctrl_type = ctrl_type
        self.check()

    def check(self):
        if self.ctrl_type not in ["bus", "noc"]:
            raise ControllerDefinedException(f"User defined controller {self.ctrl_type} is not supported")


class Bus(Controller):
    def __init__(self, ctrl_type: str, system_bw: int):
        super().__init__(ctrl_type)
        self.system_bw = system_bw  # bits/cycle

    def __str__(self):
        return f"Bus(ctrl_type={self.ctrl_type},system_bw={self.system_bw})"
    
    def __repr__(self):
        return str(self)



if __name__ == '__main__': 
    test_ctrl = Controller(ctrl_type='bus')
    my_bus = Bus(ctrl_type='bus', system_bw=100)
    print(my_bus)

