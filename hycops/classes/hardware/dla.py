from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.hardware.controller import Controller, my_bus, Bus
from hycops.classes.hardware.core_group import CoreGroup

class Dla:
    ''' 这个类暂时无用, system BW 从外部给定 '''
    def __init__(self, name: str, controller: Controller, core_groups: List[CoreGroup]):
        self.name = name
        self.controller = controller
        self.core_groups = core_groups
    
    
    
    
    
if __name__ == '__main__':
    example_1 = Dla(name='dla1', controller=Bus(ctrl_type='bus', system_bw=1024), core_groups=[])

