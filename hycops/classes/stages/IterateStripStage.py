from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.stages.Stage import Stage
from math import ceil
import logging
logger = logging.getLogger(__name__)


class IterateStripStage(Stage):
    def __init__(self, list_of_callables: List[Callable], resolution: tuple, strip_h_range: tuple = (60, 540, 160), **kwargs):
        super().__init__(list_of_callables, **kwargs)
        # self.strip_lst = self.get_strip_lst_1(strip_h_range)  # 这两个二选一即可    
        self.strip_lst = self.get_strip_lst_2(resolution)       # 这两个二选一即可    
        self.resolution = resolution

    def run(self):
        logger.info(f'Evaluating strip_h size in: {self.strip_lst}')
        for id, strip_h in enumerate(self.strip_lst, start=1):
            logger.info(f'Start strip h at {strip_h}, id {id} / {len(self.strip_lst)} ...... ')
            number_of_strip_in_pic = ceil(self.resolution[1] / strip_h)     # 这样的strip_h下，一张图有多少个strip？
            kwargs = self.kwargs.copy()
            kwargs['strip_h'] = strip_h
            kwargs['resolution'] = self.resolution
            sub_stage = self.list_of_callables[0](self.list_of_callables[1:], **kwargs)
            for cme, extra_info in sub_stage.run():     # 下一个是 workload parser stage, 传上来的cme是 [cme_nng1, cme_nng2]
                yield cme, (number_of_strip_in_pic, extra_info)

    @staticmethod
    def get_strip_lst_1(strip_h_range: tuple[int]):
        ''' 根据给定的range表达式:range: (start, end, step) 输出迭代列表 '''
        step = strip_h_range[2]
        size_lower_limit = strip_h_range[0]
        size_upper_limit = strip_h_range[1]
        size_points = int((size_upper_limit - size_lower_limit) / step) + 1
        return [size_lower_limit + i * step for i in range(size_points)]

    @staticmethod
    def get_strip_lst_2(resolution: tuple[int]):
        ''' 根据给定的分辨率输出迭代列表 '''
        h = resolution[1]
        divide_lst = [1, 2, 8, 30]
        # divide_lst = [1, 2, 3, 4, 5, 8, 15, 30]
        return [ceil(h / denominator) for denominator in divide_lst]


if __name__ == '__main__': 
    strip_h_range = (60, 540, 160)
    # stp_lst = IterateStripStage.get_strip_lst_1(strip_h_range)
    stp_lst = IterateStripStage.get_strip_lst_2((1920, 1080))
    print(stp_lst)
