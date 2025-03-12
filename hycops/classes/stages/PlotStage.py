from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.stages.Stage import Stage
import logging
logger = logging.getLogger(__name__)


class PlotStage(Stage):
    def __init__(self, list_of_callables: List[Callable], dump_filename_pattern: str, **kwargs):
        super().__init__(list_of_callables, **kwargs)
        self.dump_filename_pattern = dump_filename_pattern

    def run(self):
        self.kwargs["dump_filename_pattern"] = self.dump_filename_pattern
        substage = self.list_of_callables[0](self.list_of_callables[1:], **self.kwargs)
        self.cmes = []  # 下一个是 Strip Stage
        self.strip_num_lst = []
        for cme, extra_info in substage.run():
            self.cmes.append(cme)
            self.strip_num_lst.append(extra_info[0])
            yield cme, extra_info

        logger.info(f'Charting all result information in directory, Please Wait......')
        self.plot_total()

    def plot_total(self):
        # self.cmes 的数据结构：[[sp1_nng1, sp1_nng2], [sp2_nng1, sp2_nng2], ...]
        # extra_info[0] is number_of_strip_in_pic，用来评估出一张图的系统速率
        # todo， 使用self.cmes绘图
        pass
    
    
    