from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.stages.Stage import Stage

import logging
logger = logging.getLogger(__name__)


class IterateNNGStage(Stage):
    def __init__(self, list_of_callables: List[Callable], nngs: list, nng_num: int, **kwargs):
        super().__init__(list_of_callables, **kwargs)
        self.nngs = nngs
        self.nng_num = nng_num

    def run(self):
        for nng_id, nng in enumerate(self.nngs, start=1):
            logger.info(f'Evaluating nng_{nng_id} / {self.nng_num} ... ')
            kwargs = self.kwargs.copy()
            kwargs['nng'] = nng     # 一个nng 的数据结构: list[NN]
            sub_stage = self.list_of_callables[0](self.list_of_callables[1:], **kwargs)
            for cme, extra_info in sub_stage.run():
                yield cme, (nng, extra_info)

