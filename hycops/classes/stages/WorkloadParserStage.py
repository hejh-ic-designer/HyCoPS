from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.stages.Stage import Stage
from hycops.classes.workload.WorkloadParser import WorkloadParser
import logging
logger = logging.getLogger(__name__)


class WorkloadParserStage(Stage):
    def __init__(self, list_of_callables: List[Callable], workload_path: str, strip_h: int, resolution: tuple, fixed_stack=True, **kwargs):
        super().__init__(list_of_callables, **kwargs)
        wl_parser = WorkloadParser(yaml_path=workload_path, fixed_stack=fixed_stack, h_w=(strip_h, resolution[0]))  # resolution[0] 是整图的W
        self.all_nngs = wl_parser.get_workloads()
        self.nng_num = wl_parser.get_nng_num()

    def run(self):
        sub_stage = self.list_of_callables[0](self.list_of_callables[1:], nngs=self.all_nngs, nng_num=self.nng_num, **self.kwargs)
        cme_of_nngs = []    # 下一个是 nng stage
        for cme, extra_info in sub_stage.run():
            cme_of_nngs.append(cme)
        yield cme_of_nngs, extra_info

