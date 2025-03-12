from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.stages.Stage import Stage
import logging
logger = logging.getLogger(__name__)


class IterateComputilityStage(Stage):
    def __init__(self, list_of_callables: List[Callable], computility_range: tuple, **kwargs):
        super().__init__(list_of_callables, **kwargs)
        self.compt_lst = self.get_compt_lst(computility_range)
        
    def run(self):
        for id, compt in enumerate(self.compt_lst, start=1):
            logger.info(f'Start GA at computulity of {compt}, id {id} / {len(compt)}')
            kwargs = self.kwargs.copy()
            kwargs['compt'] = compt
            sub_stage = self.list_of_callables[0](self.list_of_callables[1:], **kwargs)
            for cme, extra_info in sub_stage.run(): 
                yield cme, extra_info
    
    def get_compt_lst(self, computility_range: tuple[int]):
        ''' range: (start, end), defalt step is 1024 '''
        step = 1024
        size_lower_limit = computility_range[0]
        size_upper_limit = computility_range[1]
        size_points = int((size_upper_limit - size_lower_limit) / step) + 1
        return [size_lower_limit + i * step for i in range(size_points)]


