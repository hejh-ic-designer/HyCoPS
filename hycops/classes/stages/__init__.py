from .Stage import MainStage, Stage
from WorkloadParserStage import WorkloadParserStage
from IterateStripStage import IterateStripStage
from IterateNNGStage import IterateNNGStage
from PlotStage import PlotStage
from IterateComputilityStage import IterateComputilityStage
from GAStage import GAStage
from SaveStage import PickleSaveStage, CompleteSaveStage, SimpleSaveStage

#: stage pattern
# from typing import Generator, Callable, List, Tuple, Any
# from hycops.classes.stages.Stage import Stage
# import logging
# logger = logging.getLogger(__name__)


# class ???Stage(Stage):
#     def __init__(self, list_of_callables: List[Callable], **kwargs):
#         super().__init__(list_of_callables, **kwargs)
        